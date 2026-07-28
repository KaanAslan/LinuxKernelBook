===================
Sayfa Önbelleği
===================

Biz şimdiye kadar Linux çekirdeğindeki bellek yönetimiyle ilgili önemli konuları gördük. Şimdi
dikkatimizi "sayfa önbelleğine (page cache)" yönelteceğiz. Sayfa önbelleği hem bellek yönetimi ile
hem de dosya sistemi ile ilişkili bir konudur. Çünkü sayfa önbelleği ağırlıklı olarak dosya
işlemlerinde devreye girmektedir. Biz sayfa önbelleğine dosya sistemini ele aldığımız beşinci ve
altıncı bölümlerde kavramsal olarak değinmiştik. Bu bölümde bu alt sistemi ayrıntılarıyla ele
alacağız.

Sayfa önbelleği (page cache) dosyalara ilişkin disk bloklarının fiziksel bellekte tutularak disk
erişiminin azaltılmasını hedefleyen bir önbellek sistemidir. Böylece ``read``/``write`` gibi
işlemlerde diske başvurulmadan istek sayfa önbelleğinden karşılanabilmektedir. Sayfa önbelleğinin
kullanımını aşağıdaki şekille betimleyebiliriz:

.. figure:: _static/page-cache-architecture.png
   :alt: Sayfa önbelleği mimarisi
   :align: center
   :width: 60%

Biz *simplefs* dosya sistemimizde sayfa önbelleğini "tampon (buffer)" işlemleriyle dolaylı bir
biçimde kullandık. Daha önceden de belirttiğimiz gibi eskiden Linux çekirdeklerinde "tampon önbelleği
(buffer cache)" ile "sayfa önbelleği (page cache)" birbirinden ayrılıyordu. Sonra bunlar birleştirildi.
Ancak tampon önbelleği ile sayfa önbelleği birleştirildiği için biz aslında *simplefs* dosya
sistemimizde tampon işlemleri yapmış olsak da dolaylı olarak sayfa önbelleğini de kullanmış olduk.
Sayfa önbelleğini tampon işlemleriyle kullanmak oldukça kolaydır. Bu nedenle biz *simplefs* dosya
sisteminde bu yola saptık. Ancak modern dosya sistemleri (örneğin ext4 gibi) dosyaların
önbelleklenmesinde tampon işlemleri yapmadan sayfa önbelleğini doğrudan kullanmaktadır. (Bu dosya
sistemleri yine disk bloklarının okunması ve yazılması işlemlerini tampon yoluyla yapmaktadır.) Biz
de dosya sistemlerinde doğrudan sayfa önbelleğinin kullanılmasını ayrı bir başlık altında ele
alacağız.

Anımsatma: simplefs Dosya Sisteminde Sayfa Önbelleğinin Kullanımı
=================================================================

Önce *simplefs* dosya sistemimizdeki tampon işlemleriyle sayfa önbelleğini nasıl kullandığımızı
anımsatmak istiyoruz. *simplefs* dosya sistemimizde kullanıcı modundan ``read`` işlemi yapıldığında
aygıt sürücümüzün aşağıdaki fonksiyonu çalıştırılıyordu:

.. code-block:: c

    static ssize_t simplefs_read(struct file *filp, char *buf, size_t size, loff_t *off)
    {
        struct inode *inode;
        struct simplefs_inode *inode_sfs;
        struct buffer_head *bh;
        struct timespec64 now;
        size_t esize;

        inode = file_inode(filp);
        inode_sfs = container_of(inode, struct simplefs_inode, vfs_inode);

        if (*off >= inode->i_size)
            return 0;

        if (inode_sfs->block_no == 0)
            return 0;

        if ((bh = sb_bread(inode->i_sb, inode_sfs->block_no)) == NULL)
            return -EIO;

        esize = min_t(size_t, inode->i_size - *off, size);
        if (copy_to_user(buf, bh->b_data + *off, esize) != 0) {
            brelse(bh);
            return -EFAULT;
        }
        *off += esize;

        now = current_time(inode);
        inode_set_atime(inode, now.tv_sec, now.tv_nsec);

        mark_inode_dirty(inode);
        brelse(bh);

        return esize;
    }

Bu fonksiyonda biz diskteki dosya bilgilerinin bulunduğu bloğu ``sb_bread`` fonksiyonuyla okuyup bu
fonksiyondan bir ``buffer_head`` nesnesi elde etmiştik. ``sb_bread`` fonksiyonu okunmak istenen disk
bloğu sayfa önbelleğinde varsa gerçek bir okuma yapmadan bize o bloğa ilişkin ``buffer_head`` nesnesini
veriyordu. Ancak ilgili disk bloğu sayfa önbelleğinde yoksa gerçek disk okuması yaparak onu sayfa
önbelleğine çekiyordu. *simplefs* dosya sistemimizde kullanıcı modundan ``write`` işlemi yapıldığında
çağrılan fonksiyon da şöyleydi:

.. code-block:: c

    static ssize_t simplefs_write(struct file *filp, const char *buf, size_t size, loff_t *off)
    {
        struct inode *inode;
        struct simplefs_inode *inode_sfs;
        int block;
        struct buffer_head *bh;
        size_t esize;
        struct timespec64 now;

        inode = file_inode(filp);
        inode_sfs = container_of(inode, struct simplefs_inode, vfs_inode);

        printk(KERN_INFO "write stats...\n");

        if (*off >= SIMPLEFS_BLOCK_SIZE)
            return -EFBIG;

        if (inode_sfs->block_no == 0) {
            if ((block = simplefs_alloc_data_block(inode->i_sb)) < 0)
                return block;
            printk(KERN_INFO "New block allocated for file: %d\n", block);
            inode_sfs->block_no = block;
            inode->i_blocks = 1;
        }
        if ((bh = sb_bread(inode->i_sb, inode_sfs->block_no)) == NULL) {
            simplefs_free_data_block(inode->i_sb, block);
            return -EIO;
        }
        esize = min_t(size_t, SIMPLEFS_BLOCK_SIZE - *off, size);
        if (copy_from_user(bh->b_data + *off, buf, esize) != 0) {
            brelse(bh);
            simplefs_free_data_block(inode->i_sb, block);
            return -EFAULT;
        }

        *off += esize;
        if (*off > inode->i_size)
            inode->i_size = *off;

        now = current_time(inode);
        inode_set_mtime(inode, now.tv_sec, now.tv_nsec);
        inode_set_ctime(inode, now.tv_sec, now.tv_nsec);

        mark_buffer_dirty(bh);
        mark_inode_dirty(inode);
        brelse(bh);

        return esize;
    }

Burada da benzer işlemler yapılmıştır. Yazmanın yapılacağı blok için yine ``sb_bread`` fonksiyonuyla
sayfa önbelleğine başvurulmuştur. Eğer ilgili blok sayfa önbelleğinde yoksa ``sb_bread`` fonksiyonu
onu gerçekten diskten okuyup sayfa önbelleğine yerleştirmektedir. Anımsanacağı gibi biz yazma
işleminde yazmayı doğrudan önbelleğe yapıyorduk. Sayfa önbelleklerinin işletim sistemi tarafından
gecikmeli bir biçimde *flush* edildiğini anımsayınız.

``sb_bread`` fonksiyonu ileride de göreceğimiz gibi aslında okuma ve yazmaları blok aygıt sürücüsünün
sayfa önbelleğinden yapmaktadır.

Sayfa Önbelleğinin Organizasyonu
================================

Linux'un sayfa önbelleği belli bir uzunluğu olan global bir bellek bölgesi değildir. Dosya işlemleri
sırasında dosya temelinde önbellekleme yapılmaktadır. Yani adeta her dosyanın sanki ayrı bir önbelleği
varmış gibi bir durum söz konusudur. Sayfa önbelleği sayfalardan oluşmaktadır, önbellekteki sayfalar
da dosyanın sayfa büyüklüğündeki kısımlarını tutmaktadır.

Anımsanacağı gibi Linux çekirdeğinde ``inode`` nesneleri dosyanın diskteki varlığını temsil
ediyordu. Aynı dosyayı birden fazla kez açıkça ya da katı bağ (hard link) yoluyla açtığımızda
aslında birden fazla dosya nesnesi (``struct file``) oluşturulurken tek bir ``inode`` nesnesi
oluşturuluyordu. İşte bir dosyanın önbellek sayfaları ``inode`` elemanının ``i_mapping`` elemanında
tutulmaktadır:

.. code-block:: c

    struct inode {
        /* ... */

        struct address_space *i_mapping;

        /* ... */
    };

Burada ``i_mapping`` elemanının ``address_space`` isimli bir yapı türünden olduğuna dikkat ediniz.
Bu ``address_space`` yapısı dosyanın sayfa önbelleğinin giriş noktasıdır. Her dosya için çekirdek
bir ``address_space`` nesnesi oluşturmaktadır.

``address_space`` yapısı dosyaya ilişkin önbellek işlemlerinde gereksinim duyulacak tüm bilgileri
içermektedir. Nesneler arasındaki ilişkiyi aşağıdaki şekille betimleyebiliriz:

.. figure:: _static/file-inode-address-space.png
   :alt: dosya nesnesi, inode ve address_space ilişkisi
   :align: center
   :width: 75%

Peki bir dosyanın önbelleklenmiş sayfaları ``address_space`` nesnesi içerisinde nasıl
tutulmaktadır? Çekirdek dosyanın okunacak ya da yazılacak kısmının önbellekte olup olmadığını
nasıl anlamaktadır? İşte bunun için daha önce görmüş olduğumuz *XArray* veri yapısı
kullanılmaktadır. Anımsanacağı gibi *XArray* aslında "radix ağaçlarının (radix tree)" Linux'a özgü
bir gerçekleştirimiydi. Radix ağaçlarının sayısal anahtarlara sahip sistemlerde hızlı arama
amacıyla kullanıldığını anımsayınız. Radix ağaçlarında her düğümün n tane alt düğümü
olabilmektedir. İşte sayfa önbelleğinde kullanılan radix ağaçlarında dosyaya ilişkin sayfa
indeksi (sayfa offset'i de diyebiliriz) anahtar durumundadır. Bu ağaçlarda her kademede 6 bitlik
değer tutulmaktadır. Yani ağacın her düğümü 64 bit temel alındığından 64 alt düğüm içermektedir.
Tabii XArray gerçekleştiriminde düğümler ancak gerektiğinde yaratılmaktadır. Yani her düğümün 64
alt düğümü olmakla birlikte bu alt düğümlere ilişkin slotlar kullanılmadığı sürece ``NULL`` adres
içermektedir. Böylece belli bir sayfa numarası ağaçta 64 / 6 + 1 = 11 karşılaştırmayla
bulunabilmektedir.

address_space Yapısı
--------------------




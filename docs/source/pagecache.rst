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

Biz yukarıda sayfa önbelleğinin yalnızca disk tabanlı dosya işlemlerinde kullanıldığı yönünde bir
izlenim vermiş olabiliriz. Ancak sayfa önbelleği disk dosyalarının dışında başka çekirdek
mekanizmaları tarafından da kullanılmaktadır:

.. figure:: _static/page-cache-users.png
   :alt: Sayfa önbelleği kullanıcıları
   :align: center
   :width: 55%

Buradaki VFS kutucuğu disk tabanlı dosya işlemlerini belirtmektedir.

address_space Yapısı
--------------------

Şimdi ``address_space`` yapısını inceleyelim. ``address_space`` yapısı güncel çekirdeklerde
``include/linux/fs.h`` dosyasında aşağıdaki gibi tanımlanmıştır:

.. code-block:: c

    struct address_space {
        struct inode                    *host;
        struct xarray                    i_pages;
        struct rw_semaphore              invalidate_lock;
        gfp_t                            gfp_mask;
        atomic_t                         i_mmap_writable;
    #ifdef CONFIG_READ_ONLY_THP_FOR_FS
        /* number of thp, only for non-shmem files */
        atomic_t                         nr_thps;
    #endif
        struct rb_root_cached            i_mmap;
        unsigned long                    nrpages;
        pgoff_t                          writeback_index;
        const struct address_space_operations *a_ops;
        unsigned long                    flags;
        errseq_t                         wb_err;
        spinlock_t                       i_private_lock;
        struct list_head                 i_private_list;
        struct rw_semaphore              i_mmap_rwsem;
        void                            *i_private_data;
    } __attribute__((aligned(sizeof(long)))) __randomize_layout;

``address_space`` yapısının ``i_pages`` elemanı ``xarray`` yapısı türündendir. Yani *XArray* ağacı
yapının bu elemanında tutulmaktadır. Başka bir deyişle önbellekte arama bu elemanın belirttiği ağaç
kullanılarak yapılmaktadır. Yapının ``nrpages`` elemanı bu dosyanın önbelleğinde tutulan sayfaların
toplam sayısını belirtmektedir. Bazı durumlarda elde bir ``address_space`` nesnesi varken geriye
dönüp ona ilişkin ``inode`` nesnesine erişilmesi gerekebilmektedir. Yapının ``host`` elemanı
``address_space`` nesnesinin sahibi olan ``inode`` nesnesini göstermektedir. Yapının içerisinde bazı
senkronizasyon nesnelerini görüyorsunuz. Bunlar dosyanın önbellek işlemlerinde eşzamanlı erişimlerde
koruma sağlamak için kullanılmaktadır. Yapının ``flags`` elemanında işleyiş sırasında kullanılan bazı
bayraklar tutulmaktadır. Yapının ``i_mmap`` elemanı bellek tabanlı dosyalarda ve genel olarak bellek
haritalama (memory mapping) işlemlerinde kullanılmaktadır. Yapının ``a_ops`` elemanı çokbiçimli
davranış için kullanılan fonksiyon göstericilerinden oluşan bir yapı nesnesinin adresini
tutmaktadır. Biz bu konuları ayrı bir paragrafta ele alacağız. Aşağıdaki tabloda yapı elemanlarının
işlevlerini özet olarak veriyoruz:

.. figure:: _static/address-space-fields-table.png
   :alt: address_space yapısı elemanları
   :align: center
   :width: 70%

Dosya Offset'inden Hareketle Dosyanın Önbellekteki Kısmına Erişilmesi
-------------------------------------------------------------------------

Her ``inode`` nesnesinin ayrı bir sayfa önbelleği olduğunu ve sayfa önbelleğinde dosyaya ilişkin
kısımların tutulduğunu, arama işleminin de XArray yani radix ağacı yoluyla yapıldığını belirttik.
Şimdi önbelleğin organizasyonunun nasıl yapıldığı üzerinde duralım. Önbellekte anahtar dosyaya
ilişkin sayfa indeksidir. Yani dosyanın parçaları sayfa temelinde (tipik olarak 4K) sayfa
önbelleğinde tutulmaktadır. Örneğin bir dosyanın 80000 byte olduğunu düşünelim. Aslında bu dosya
4K'lık sayfaların söz konusu olduğu tipik sistemlerde 80000 / 4096 = 19.53125 yani 20 sayfa olarak
düşünülebilir. Tabii dosyaya offset yoluyla erişilmektedir. Dosya offset'inin dosyanın kaçıncı
sayfasında olduğunun hesabı oldukça basittir: ``offset >> PAGE_SHIFT``. Burada ``PAGE_SHIFT`` bir
sayfanın 2 üzeri kaç byte'tan oluştuğunu belirtmektedir. (4K sayfalar için ``PAGE_SHIFT`` değeri
12'dir.) Tabii ``offset % PAGE_SIZE`` değeri ile ilgili sayfadaki offset de elde edilebilir. İşte
çekirdek belli bir dosya offset'inden hareketle önce dosya offset'ini sayfa indeksine (sayfa
offset'i de diyebiliriz) dönüştürüp sonra ilgili sayfayı dosyanın sayfa önbelleğinde aramaktadır.
Örneğin biz aşağıdaki gibi bir çağrı yapmış olalım:

.. code-block:: c

    result = read(fd, buf, 100);

Dosya göstericisinin konumu da 10254 olsun. Çekirdek önce dosya nesnesine, oradan dosyaya ilişkin
``inode`` nesnesine, oradan da dosyanın önbellek bilgilerinin bulunduğu ``address_space`` nesnesine
erişir. *XArray* yani radix ağacının kökünün ``address_space`` nesnesi içerisinde olduğunu
belirtmiştik. İşte radix ağacındaki anahtar sayfa indeksidir. Çekirdek 10254 numaralı dosya
offset'ini 4096'ya tam bölerek sayfa indeksini elde eder. Örneğimizde bu değer 2'dir. İşte bu 2
değerini radix ağacına anahtar yapmaktadır.

*XArray* radix ağacının anahtarının sayfa indeksi (dosya offset'i değil) olduğunu söyledik. Peki
aramadan elde edilecek değer nedir? İşte güncel çekirdeklerde sayfa önbelleğindeki aramadan
``folio`` isimli bir yapı türünden nesne adresi elde edilmektedir. Yani radix ağacındaki anahtarlar
sayfa indeksidir, elde edilecek değerler ise ``folio`` nesneleridir. Eskiden (çekirdeğin 5.16
sürümünden önce) ``folio`` nesneleri yerine doğrudan ``page`` nesneleri kullanılıyordu. Yani
çekirdeğin 5.16 sürümünden önce buradaki radix ağacı bize dosyanın bellekteki kısmına ilişkin
``page`` nesnesinin adresini veriyordu. Ancak 5.16'dan itibaren sistem biraz daha iyileştirilmiş ve
``folio`` yapısı kullanılmaya başlanmıştır. Tabii izleyen paragraflarda ele alacağımız gibi ``folio``
nesnesinden ``page`` nesnesine, dolayısıyla da dosyanın ilgili kısmının fiziksel bellekteki kısmına
erişilmektedir.

Bir dosyaya ilişkin önbelleğin *XArray* ağacını sembolik biçimde şöyle betimleyebiliriz:

.. figure:: _static/xarray-page-cache-table.png
   :alt: Sayfa önbelleği XArray ağacı örneği
   :align: center
   :width: 45%

Sayfa Önbelleğinde Büyük Blokların Saklanması
--------------------------------------------- 

Sayfa önbelleğinde saklanan önbellek blokları genellikle sayfa büyüklüğündedir. Yani genellikle bir
dosyanın çeşitli kısımlarının birer sayfalık (tipik olarak 4K'lık) bölümleri önbelleğe alınmaktadır.
Ancak bazı durumlarda ilgili dosyanın (genellikle bellek haritalama işlemlerinde karşımıza çıkmaktadır)
daha büyük kısımları da önbelleğe alınabilmektedir. Biz bir dosyanın 4K'lık değil de 64K'lık
kısımlarının önbelleğe alınacağını düşünelim. Bu durumda organizasyon nasıl olacaktır? İşte sayfa
önbelleğindeki bir sayfadan büyük bloklara "bileşik sayfa (compound page)" denilmektedir. Örneğin
önbellekte 64K'lık blokların da tutulduğunu düşünelim. Çekirdek bu 64K'lık bileşik sayfayı aslında
16 tane normal sayfa gibi XArray ağacında tutmaktadır. Bu 16 sayfanın ilk sayfasına "baş (head)"
sayfa, diğerlerine ise "kuyruk (tail)" sayfaları denilmektedir. Yani kuyruk sayfaları bloğun baş
sayfa dışındaki sayfalarını temsil etmektedir.

*XArray* ağacında her zaman sayfa temelinde arama yapılmaktadır. Bu durumda örneğin dosyanın 64K'lık
bir kısmı tek bir birim gibi sayfa önbelleğine yerleştirilip belli bir offset'e dayalı arama
yapıldığında bulunan sayfa bu 16 sayfanın baş sayfası olabileceği gibi kuyruk sayfalarından biri de
olabilecektir. Bir sayfadan daha büyük birimlerin önbelleğe yerleştirilmesi durumunda sayfa önbelleği
için metadata bilgileri her zaman baş sayfada tutulmaktadır. O halde çekirdek bir sayfa indeksiyle
*XArray* ağacında arama yaptığında o sayfanın bir baş sayfa mı yoksa kuyruk sayfası mı olduğunu
anlayabilmeli; eğer erişilen sayfa bir kuyruk sayfası ise onun baş sayfasını bulabilmelidir. *XArray*
aramasında baş sayfanın nasıl bulunduğunu izleyen paragraflarda açıklayacağız. Ancak bazen çekirdeğin
bir ``page`` nesnesinden hareketle o ``page`` nesnesinin ilişkin olduğu büyük bloğun baş sayfasına
ilişkin ``page`` nesnesine de erişmesi gerekebilmektedir. İşte bu işlem ``page`` yapısının
içerisindeki ``compound_head`` isimli eleman yardımıyla yapılmaktadır:

.. code-block:: c

    struct page {
        /* ... */
        unsigned long compound_head;    /* Bit zero is set for tail pages */
        /* ... */
    };

``compound_head`` elemanının en düşük anlamlı biti (0 numaralı biti) 1 ise ``page`` nesnesi bir
kuyruk sayfasına, 0 ise baş sayfaya ilişkindir. Sayfa eğer kuyruk sayfasıysa ``compound_head``
elemanının en düşük anlamlı biti sıfırlandığında (bu işlem 1 çıkartılarak da yapılabilir)
``compound_head`` elemanı baş sayfaya ilişkin ``page`` nesnesinin adresini vermektedir. Eğer
``compound_head`` elemanının en düşük anlamlı biti 1 değilse zaten ilgili sayfa bir baş sayfadır.
Bu durumda bu eleman artık ``page`` içerisindeki birlik yoluyla LRU listesindeki sonraki elemanı
gösteren düğümle çakıştırılmış durumda olur. Çekirdekte bir ``page`` nesnesinin adresini parametre
olarak alıp nesnesinin baş sayfasına ilişkin ``page`` nesne adresini elde eden ``_compound_head``
isimli bir fonksiyon bulunmaktadır:

.. code-block:: c

    static __always_inline unsigned long _compound_head(const struct page *page)
    {
        unsigned long head = READ_ONCE(page->compound_head);

        if (unlikely(head & 1))
            return head - 1;
        return (unsigned long)page_fixed_fake_head(page);
    }

Bir sayfadan (tipik olarak 4K'dan) büyük birimlerin önbelleklerde tutulması Linux çekirdeğine 4.8
sürümüyle eklenmiş bir özelliktir. Dolayısıyla daha önceki çekirdeklerin ``page`` yapılarında
``compound_head`` elemanı yoktu.

Aslında sayfa önbelleğinde bir sayfadan (yani 4K'dan) daha büyük birimlerle seyrek karşılaşılmaktadır.
Bir sayfadan büyük önbellek birimleri kullanan başlıca kaynaklar şunlardır:

.. figure:: _static/large-folio-users-table.png
   :alt: Büyük folio kullanan dosya sistemleri ve mekanizmalar
   :align: center
   :width: 75%

folio Yapısı
------------

Yukarıda da belirttiğimiz gibi eskiden sayfa önbelleğine ilişkin *XArray* ağacına dosyanın sayfa
indeksi verildiğinde o bize doğrudan sayfaya ilişkin ``page`` nesnesinin adresini veriyordu. Ancak
daha sonra ``folio`` nesneleri kullanılmaya başlandı. Mevcut çekirdeklerde sayfa önbelleğinden
yapılan başarılı aramalarda ``folio`` nesnelerinin adresleri elde edilmektedir. ``folio`` nesneleri için 
ayrıca bir tahsisat yapılmamaktadır. Yani ``folio`` nesneleri aslında ``page`` nesneleri 
ile aynı alanı kullanmaktadır.

``folio`` yapısı birlikler içeren oldukça karmaşık bir görünümdedir. Yapının tanımlaması
``include/linux/mm_types.h`` dosyası içerisinde şöyle yapılmıştır:

.. code-block:: c

    struct folio {
        /* private: don't document the anon union */
        union {
            struct {
        /* public: */
                memdesc_flags_t flags;
                union {
                    struct list_head lru;
        /* private: avoid cluttering the output */
                    /* For the Unevictable "LRU list" slot */
                    struct {
                        /* Avoid compound_head */
                        void *__filler;
        /* public: */
                        unsigned int mlock_count;
        /* private: */
                    };
        /* public: */
                    struct dev_pagemap *pgmap;
                };
                struct address_space *mapping;
                union {
                    pgoff_t index;
                    unsigned long share;
                };
                union {
                    void *private;
                    swp_entry_t swap;
                };
                atomic_t _mapcount;
                atomic_t _refcount;
    #ifdef CONFIG_MEMCG
                unsigned long memcg_data;
    #elif defined(CONFIG_SLAB_OBJ_EXT)
                unsigned long _unused_slab_obj_exts;
    #endif
    #if defined(WANT_PAGE_VIRTUAL)
                void *virtual;
    #endif
    #ifdef LAST_CPUPID_NOT_IN_PAGE_FLAGS
                int _last_cpupid;
    #endif
        /* private: the union with struct page is transitional */
            };
            struct page page;
        };
        union {
            struct {
                unsigned long _flags_1;
                unsigned long _head_1;
                union {
                    struct {
        /* public: */
                        atomic_t _large_mapcount;
                        atomic_t _nr_pages_mapped;
    #ifdef CONFIG_64BIT
                        atomic_t _entire_mapcount;
                        atomic_t _pincount;
    #endif /* CONFIG_64BIT */
                        mm_id_mapcount_t _mm_id_mapcount[2];
                        union {
                            mm_id_t _mm_id[2];
                            unsigned long _mm_ids;
                        };
        /* private: the union with struct page is transitional */
                    };
                    unsigned long _usable_1[4];
                };
                atomic_t _mapcount_1;
                atomic_t _refcount_1;
        /* public: */
    #ifdef NR_PAGES_IN_LARGE_FOLIO
                unsigned int _nr_pages;
    #endif /* NR_PAGES_IN_LARGE_FOLIO */
        /* private: the union with struct page is transitional */
            };
            struct page __page_1;
        };
        union {
            struct {
                unsigned long _flags_2;
                unsigned long _head_2;
        /* public: */
                struct list_head _deferred_list;
    #ifndef CONFIG_64BIT
                atomic_t _entire_mapcount;
                atomic_t _pincount;
    #endif /* !CONFIG_64BIT */
        /* private: the union with struct page is transitional */
            };
            struct page __page_2;
        };
        union {
            struct {
                unsigned long _flags_3;
                unsigned long _head_3;
        /* public: */
                void *_hugetlb_subpool;
                void *_hugetlb_cgroup;
                void *_hugetlb_cgroup_rsvd;
                void *_hugetlb_hwpoison;
        /* private: the union with struct page is transitional */
            };
            struct page __page_3;
        };
    };

Yapının anlaşılması oldukça zordur. Parça parça incelenerek daha kolay anlaşılabilir. Yapının baş
kısmı bir birlik içermektedir:

.. code-block:: c

    struct folio {
        union {
            struct {
                /* ... */
            };
            struct page page;
        };
        /* ... */
    };

``folio`` yapısının baş kısmı birlik kullanılarak tamamen ``page`` yapısının üzerine oturtulmuştur.
``folio`` yapısının ``page`` yapısı dışında kalan alanlarına ancak ``folio`` yapısı birden fazla
sayfadan oluşan bir önbellek bloğuna ilişkinse erişilmektedir. Bu alanlar ``folio`` nesnesi bir
sayfadan büyük birimleri tutuyorsa onun sonraki ``page`` nesnesi içerisinde bulunmaktadır. Bir
sayfadan büyük önbellek bloklarının ikinci ``page`` nesnesinde de bazı ``folio`` bilgileri
saklanmaktadır. Bunu aşağıdaki çizimle görselleştirebiliriz:

.. figure:: _static/folio-page-layout.png
   :alt: folio ve page nesnelerinin bellek düzeni
   :align: center
   :width: 70%

Peki bir ``folio`` nesnesinin belirttiği önbellek sayfasına nasıl erişilmektedir? ``folio`` nesnesi
aslında bir ``page`` nesnesi olduğuna göre ``folio`` nesnesinin adresi ile ``page`` nesnesinin adresi
aynıdır. Biz bir ``page`` nesnesinin adresi ile o nesnenin belirttiği sayfanın fiziksel ve sanal
adreslerine makrolar ve fonksiyonlarla erişebiliyorduk. ``include/linux/mm.h`` dosyası içerisinde
``folio`` nesnesinin adresini alarak ona ilişkin önbellek bloğunun adresini veren ``folio_address``
isimli fonksiyon bulunmaktadır:

.. code-block:: c

    static inline void *folio_address(const struct folio *folio)
    {
        return page_address(&folio->page);
    }

Gördüğünüz gibi fonksiyonun tek yaptığı şey ``page_address`` fonksiyonunu çağırmaktır. Biz bu
fonksiyonu incelemiştik. ``folio`` yapısının ``page`` elemanının aslında nesnesinin başlangıç
adresiyle, dolayısıyla da ``folio`` adresiyle aynı olduğuna dikkat ediniz. ``page_address``
fonksiyonu ``page`` türünden bir adres istediği için erişim bu biçimde yapılmıştır.

Peki bir sayfadan büyük (örneğin 64K) önbellek bloğuna sahip bir dosya sisteminde belli bir dosya
offset'inden ``read`` fonksiyonuyla okuma yapıldığında çekirdek önbellekteki yeri nasıl tespit
etmektedir? İşte çekirdek önce dosya offset'ini yine sayfa indeksine dönüştürerek bu sayfa indeksi
ile XArray ağacında arama yapar. *XArray* ağacında arama yapıldığında ağaçtaki alt düğümün yerlerini
belirten slotlarda aranan hedef slot bulunur (anımsayacağınız gibi düğümün slotları alt düğümlerin
yerlerini tutan göstericileri barındırmaktadır). İşte bulunan slot eğer baş sayfaya ilişkin bir slot
değilse buna *kardeş slot (sibling slot)* denilmektedir. Bu kardeş slotun içerisinde ``folio``
nesnesinin adresi değil baş sayfanın slot indeksinin yeri tutulmaktadır. Eğer bu slot baş sayfaya
ilişkinse (baş sayfaya ilişkin slotlara *kanonik slotlar* da denilmektedir) slot indeks değil
doğrudan ``folio`` nesnesinin adresini tutmaktadır. Yani bulunan kardeş slottan hareketle baş slotun
(kanonik slotun) yeri, oradan hareketle de büyük birimin ``folio`` nesne adresi elde edilmektedir.
Yani işlemler çekirdek tarafından şu aşamalardan geçilerek yürütülmektedir:

1. Dosya offset'inden hareketle erişilecek yerin sayfa indeksi elde edilir.
2. Bu sayfa indeksi XArray ağacına anahtar yapılarak ağaçtan bu sayfa indeksine ilişkin slot elde
   edilir. Bu slot baş sayfaya ilişkin değilse baş sayfaya ilişkin slota (kanonik slota) geçilir.
3. Baş sayfaya ilişkin slotun (kanonik slotun) içerisinden ``folio`` nesne adresinden hareketle bir
   sayfadan büyük (örneğin 64K) önbellek bloğunun başlangıç adresi elde edilir.
4. Aranan dosya offset'inin önbellek bloğu içerisindeki offset'i elde edilir.
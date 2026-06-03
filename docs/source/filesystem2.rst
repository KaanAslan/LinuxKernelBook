.. _dosya-sistemi-2:

=========================
Dosya Sistemi - II. Bölüm
=========================

Bu bölümde Linux çekirdeğinin dosya sistemine ilişkin bazı ayrıntıları "simplefs" isimli bir dosya sistemini 
gerçekleşitrerek açıklayacağız. *simplefs* dosya sistemi **Linux Kernel - İşletim Sistemlerinin Tasatımı ve Gerçekleştirilmesi**
kursuna sınıf içerisinde tasarlanmış oldukça basit bir dosya sistemidir. Bu dosya sistemini bugün yoğun biçimde kullandığımız
*ext2* gibi *ext4* gibi dosya sistemlerinin basit bir biçimi gibi düşünebilirsiniz. 

Hazırlık İşlemleri
==================

*simplfs* dosya sistemiminin gerçekleştirimine başlamadan önce bazı hazırlık bilgileri vereceğiz.

Linux Çekirdeğinde Kullanılan Temel Türlere İlişkin typedef İsimleri
---------------------------------------------------------------------

Linux çekirdeğinin kodlamasında tür ve uzunluk belirten bazı typedef tür isimleri kullanılmıştır.
Çekirdeğin içsel kodlarında belli uzunlukta tamsayı türleri ``include/linux/types.h`` dosyası
içerisinde aşağıdaki isimlerle typedef edilmiştir:

.. code-block:: c

    typedef unsigned char      __u8;
    typedef signed char        __s8;
    typedef unsigned short     __u16;
    typedef signed short       __s16;
    typedef unsigned int       __u32;
    typedef signed int         __s32;
    typedef unsigned long long __u64;
    typedef signed long long   __s64;

    typedef __u8    u8;
    typedef __s8    s8;
    typedef __u16   u16;
    typedef __s16   s16;
    typedef __u32   u32;
    typedef __s32   s32;
    typedef __u64   u64;
    typedef __s64   s64;

    typedef unsigned long  ulong;
    typedef unsigned int   uint;
    typedef unsigned short ushort;

Endian bilgisinin de vurgulandığı türler ``include/uapi/linux/types.h`` dosyası içerisinde
aşağıdaki gibi typedef edilmiştir:

.. code-block:: c

    typedef __u16 __bitwise __le16;
    typedef __u16 __bitwise __be16;
    typedef __u32 __bitwise __le32;
    typedef __u32 __bitwise __be32;
    typedef __u64 __bitwise __le64;
    typedef __u64 __bitwise __be64;

Burada işaretli tamsayı türlerinin bulunmadığına dikkat ediniz.

C'ye C99 ile eklenen *intN_t* ve *uintN_t* tür isimleri (örneğin *int32_t* ya da *uint32_t* gibi
tür isimleri) Linux çekirdek kodlarında kullanılmamaktadır. Zaten bunların bildirimleri C'ye özgü
``<stdint.h>`` içerisindedir. Linux çekirdeğinde C'nin herhangi bir standart başlık dosyası
kullanılmamaktadır. Bu nedenle çekirdek kodlamaları yapılırken yukarıda belirttiğimiz *typedef*
türlerini tercih etmelisiniz.

Loop Aygıtları
---------------

Bir dosya sistemini gerçekleştirirken bizim bir diske gereksinimimiz olacaktır. Neyse ki Linux'ta bir 
dosyanın bir disk gibi kullanılmasını sağlayan ismine *loop* denilen aygıt sürücüler bulunmaktadır. Bu *loop* 
aygıtları sayesinde bir dosyayı disk gibi kullanarak denemelerimizi kolay bir biçimde yapabileceğiz. O halde önce bu *loop* aygıt
sürücüsünün nasıl kullanıldığını açıklayalım.

Loop Aygıt Dosyaları
~~~~~~~~~~~~~~~~~~~~

*loop* aygıt sürücülerine ilişkin aygıt dosyaları Linux'ta ``/dev`` dizininin altında
bulunmaktadır:

.. code-block:: bash

    $ ls /dev/loop* -l
    brw-rw---- 1 root disk  7,   0 Kas 23 12:22 /dev/loop0
    brw-rw---- 1 root disk  7,   1 Kas 23 12:22 /dev/loop1
    brw-rw---- 1 root disk  7,   2 Kas 23 12:22 /dev/loop2
    brw-rw---- 1 root disk  7,   3 Kas 23 12:22 /dev/loop3
    brw-rw---- 1 root disk  7,   4 Kas 23 12:22 /dev/loop4
    brw-rw---- 1 root disk  7,   5 Kas 23 12:22 /dev/loop5
    brw-rw---- 1 root disk  7,   6 Kas 23 12:22 /dev/loop6
    brw-rw---- 1 root disk  7,   7 Kas 23 12:22 /dev/loop7
    crw-rw---- 1 root disk 10, 237 Kas 23 12:22 /dev/loop-control

Görüldüğü gibi bu sistemde majör numaraları aynı olan, minör numaraları farklı olan 8 loop aygıtı
bulunmaktadır.

Loop Aygıtları İçin Dosya Oluşturma
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bir loop aygıtını kullanıma hazır hale getirmek için önce onun kullanacağı bir dosyanın
oluşturulması gerekir. Linux'ta komut satırında içi 0'larla dolu olan bir dosya *dd* (*disk dump*)
komutuyla oluşturulabilir. *dd* komutu aslında iki dosyayı blok blok kopyalamaktadır. Komutta
*if* (*input file*) komut satırı argümanı kaynak dosyayı, *of* (*output file*) komut satırı
argümanı ise hedef dosyayı belirtmektedir. Blok uzunluğu *bs* (*block size*) komut satırı
argümanıyla, kopyalanacak blok sayısı ise *count* argümanıyla belirtilmektedir. *bs* argümanı
kullanılmayabilir; bu durumda varsayılan blok büyüklüğü 512 alınmaktadır. Eğer *count* argümanı
kullanılmazsa tüm kaynak dosya kopyalanana kadar işlemlere devam edilmektedir. Linux'ta
``/dev/zero`` aygıt sürücüsü okunduğunda hep 0 baytı veren bir aygıt sürücüdür. Bu bilgiler
eşliğinde içi 0'larla dolu 10 MB civarında bir dosya şöyle oluşturulabilir:

.. code-block:: bash

    $ dd if=/dev/zero of=mydisk.dat bs=512 count=20480

Bu komutla elimizde içi sıfırlarla dolu 10 MB'lık bir dosya elde etmiş olacağız.


Loop Aygıtlarını Yapılandırma
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dosyayı oluşturduktan sonra onun loop aygıtı tarafından disk gibi kullanılmasını sağlamalıyız.
Bu işlem *losetup* programıyla yapılmaktadır. *losetup* programı şöyle kullanılmaktadır:

.. code-block:: text

    losetup <loop_aygıt_dosyası> <disk_olarak_kullanılacak_dosya>

Örneğin:

.. code-block:: bash

    $ sudo losetup /dev/loop0 mydisk.dat

``/dev/loop`` aygıtına erişebilmek için programın *sudo* ile çalıştırılması gerekmektedir.

Artık elimizde ``mydisk.dat`` dosyasını kullanan *loop0* isimli bir blok aygıtı bulunmaktadır.
Sistemdeki blok aygıtlarını *lsblk* komutu ile görüntülediğimizde bu aygıtı da görmeliyiz:

.. code-block:: bash

    $ lsblk
    NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
    loop0    7:0    0    10M  0 loop
    sda      8:0    0   120G  0 disk
    ├─sda1   8:1    0     1M  0 part
    ├─sda2   8:2    0   513M  0 part /boot/efi
    └─sda3   8:3    0 119,5G  0 part /
    sr0     11:0    1   2,8G  0 rom  /media/kaan/Linux Mint 22.1 Cinnamon 64-bit


Loop Aygıtına İlişkin Diskin Formatlanması ve Mount Edilmesi
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Artık ``/dev/loop0`` dosyasını bir disk gibi kullanabiliriz. Bu diske yazma yaptığımızda bu
işlemden yalnızca bu dosya etkilenecektir. Örneğin bu diskimizi ext2 dosya sistemiyle
formatlayalım:

.. code-block:: bash

    $ sudo mkfs.ext2 /dev/loop0
    mke2fs 1.47.0 (5-Feb-2023)
    Discarding device blocks: bitti
    Creating filesystem with 2560 4k blocks and 2560 inodes

    Allocating group tables: bitti
    Düğüm tabloları yazılıyor: bitti
    Süperblokların ve dosya sisteminin hesap bilgileri yazılıyor: bitti

Şimdi de bu dosya sistemini mount edelim. Bunun için önce mount noktası olarak kullanılacak boş
bir dizin oluşturmamız gerekir. (Aslında mount noktası içi dolu bir dizin de olabilir; bu durumda
mount işleminden sonra o dizinin içeriğine unmount yapılana kadar erişilemez.):

.. code-block:: bash

    $ mkdir ext2-test

Mount işlemi şöyle yapılabilir:

.. code-block:: bash

    $ sudo mount /dev/loop0 ext2-test

Artık *ext2-test* dizinine geçtiğimizde yeni bir kök dizine geçmiş oluruz. Mount sonrasında mount
noktasına ilişkin dizinin (örneğimizdeki *ext2-test*) sahibi ve grubu *root* olacaktır. Tabii
isterseniz *chown* komutuyla bunu değiştirebilirsiniz:

.. code-block:: bash

    $ sudo chown kaan:study ext2-test

Eğer dizinin sahibini *root* olarak bırakırsanız bu dizinde girdi yaratmak için hep *sudo*
komutunu kullanmak zorunda kalırsınız.


Geri Alma İşlemleri
~~~~~~~~~~~~~~~~~~~~

Peki bu işlemlerin hepsi nasıl geri alınacaktır? Geri alımları sırasıyla tersine yapmak gerekir.
Önce unmount işlemi yapılmalıdır:

.. code-block:: bash

    $ sudo umount ext2-test

Bundan sonra *loop* aygıtının dosyayla ilişkisinin kesilerek onun blok aygıtı durumundan
çıkartılması gerekir. Bunun için *"losetup -d"* komutu kullanılmaktadır:

.. code-block:: bash

    $ sudo losetup -d /dev/loop0

Artık *lsblk* komutunda *loop0* aygıtını görmememiz gerekir:

.. code-block:: bash

    $ lsblk
    NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
    sda      8:0    0   120G  0 disk
    ├─sda1   8:1    0     1M  0 part
    ├─sda2   8:2    0   513M  0 part /boot/efi
    └─sda3   8:3    0 119,5G  0 part /
    sr0     11:0    1   2,8G  0 rom  /media/kaan/Linux Mint 22.1 Cinnamon 64-bit

Tabii burada oluşturduğumuz ``mydisk.dat`` dosyası kalmaya devam etmektedir. Biz o dosyayı yine
*losetup* ile blok aygıtı gibi kullanabiliriz ve işlemlerimize kaldığımız yerden devam
edebiliriz.


Loop Aygıtlarının Kullanım Akışı
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Aşağıdaki şema, loop aygıtının tipik kullanım akışını özetlemektedir:

.. code-block:: text

    ┌─────────────────────────────────────────────────────────────┐
    │                   Loop Aygıtı Kullanım Akışı                │
    └──────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
    ┌─────────────────────────────────────────────────────────────┐
    │  1. Disk dosyası oluştur                                    │
    │     dd if=/dev/zero of=mydisk.dat bs=512 count=20480        │
    └──────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
    ┌─────────────────────────────────────────────────────────────┐
    │  2. Loop aygıtına bağla                                     │
    │     sudo losetup /dev/loop0 mydisk.dat                      │
    └──────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
    ┌─────────────────────────────────────────────────────────────┐
    │  3. Dosya sistemi oluştur (formatla)                        │
    │     sudo mkfs.ext2 /dev/loop0                               │
    └──────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
    ┌─────────────────────────────────────────────────────────────┐
    │  4. Mount et                                                │
    │     mkdir ext2-test                                         │
    │     sudo mount /dev/loop0 ext2-test                         │
    └──────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
    ┌─────────────────────────────────────────────────────────────┐
    │  5. Kullan  (ext2-test dizini üzerinden erişim)             │
    └──────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
    ┌─────────────────────────────────────────────────────────────┐
    │  6. Geri al (ters sırayla)                                  │
    │     sudo umount ext2-test                                   │
    │     sudo losetup -d /dev/loop0                              │
    └─────────────────────────────────────────────────────────────┘

simplefs Dosya Sisteminin Tasarımı
==================================

Sıfırdan bir dosya sistemi tasarlanacaksa öncelikle dosya sisteminin disk organizasyonu üzerinde
belirlemelerin yapılması gerekir. Her dosya sisteminin bir metadata alanı bir de data alanı vardır.
Metadata alanında dosya sistemine ilişkin parametrik bilgiler ve önemli bölümlerin bilgileri
bulundurulur. Data alanı dosyaların içindeki bilgilerin saklandığı alandır. Bugün kullandığımız
dosya sistemleri evrim süreci içerisinde sürekli iyileştirilmiş ve bugünkü durumlarına
getirilmiştir. Dolayısıyla örneğin ext4 gibi bir dosya sisteminin ya da FAT32 gibi bir dosya
sisteminin gerçekleştirimini bir proje biçiminde yapmak gerekir. Yani bunun için belli bir süre düzenli
çalışma zamanının ayrılması gerekir. Biz burada oldukça basit bir dosya sistemini gerçekleştirmeye
çalışacağız. Bu dosya sistemini *simplefs* olarak isimlendireceğiz.

simplefs Dosya Sisteminin Disk Organizasyonu
--------------------------------------------

*simplefs* dosya sisteminin disk organizasyonu aşağıdaki şekilde gösterilmektedir:

.. figure:: _static/simplefs-disk-org.png
   :align: center
   :alt: simplefs disk organizasyonu
   :width: 50%

   simplefs dosya sisteminin disk organizasyonu

*simplefs* dosya sistemimizin ilk bloğu (yani ilk 4096 byte'ı) süper bloktur. Burada dosya
sistemimize ilişkin önemli parametrik bilgiler tutulmaktadır. UNIX/Linux sistemlerinde her dosyanın
bilgileri diskte *inode blok* denilen bir grup bloktaki inode elemanlarında tutulmaktadır.

Inode Blok Yapısı
~~~~~~~~~~~~~~~~~~

Inode blok, aşağıdaki gibi inode elemanlarından oluşmaktadır:

.. figure:: _static/simplefs-inode-block.png
   :align: center
   :alt: inode blok yapısı
   :width: 50%

   Inode blok yapısı

Her dosya ve dizin için dosya sisteminin diskte bir inode elemanını tahsis etmesi gerekir. Boş bir
inode elemanının belirlenebilmesi için inode tabanlı dosya sistemlerinde genellikle bir *inode
bitmap* kullanılmaktadır. Bu *inode bitmap* içerisindeki her bit ilgili inode elemanının boş mu
dolu mu olduğunu göstermektedir. Dosya sistemimizde inode bitmap bir blok yer kapladığına göre
toplamda 4096 × 8 = 32768 inode elemanının durumu tutulabilmektedir.

Inode tabanlı dosya sistemlerinde *data blok* içerisindeki blokların da boş mu dolu mu olduğu
bilgisi benzer biçimde bir *data bitmap* ile tutulmaktadır. Bu *data bitmap* içerisindeki her bit
diskteki data bloğunun boş mu dolu mu olduğu bilgisini tutmaktadır.

Pek çok dosya sisteminin disk organizasyonunda dizinler de birer dosyaymış gibi ele alınmaktadır.
Dolayısıyla her dizin data bloğunda bir blok yer kaplamaktadır. Genellikle kök dizin belli bir
yerde bulundurulur. Kök dizinin yeri de süper blokta belirtilir. Tabii kök dizin için en uygun yer
data bloklarının ilk bloğudur.

*simplefs* dosya sistemimizde her dosya ve dizin en fazla bir blok (yani varsayılan olarak 4096
byte) uzunluğunda olabilmektedir. Bu kısıtı koyduğumuzda artık dosyanın bloklarının yerlerini
tutmamıza gerek kalmaz. *simplefs* dosya sistemimizdeki inode elemanlarının sayısı formatlama
sırasında belirlenebilmektedir. Ancak *data bitmap* ve *inode bitmap* 4096 × 8 = 32768 bitten
oluştuğuna göre dosya sistemi de en fazla 32768 × 4096 = 134 MB büyüklüğünde bir diski
desteklemektedir.

Süper Blok Yapısı
~~~~~~~~~~~~~~~~~~

Diskimizin süper blok bilgileri aşağıdaki C yapısıyla tanımlanmıştır:

.. code-block:: c

    struct simplefs_disk_super_block {
        __le32 magic;              /* 0x53494D46 ("SIMF") */
        __le32 block_size;         /* 4096 */
        __le32 inode_count;        /* Total inodes */
        __le32 block_count;        /* Total blocks */
        __le32 free_inodes;        /* Free inodes */
        __le32 free_blocks;        /* Free blocks */
        __le32 inode_table_block;  /* Start of the inode table (3) */
        __le32 inode_table_size;   /* Size of the inode table */
        __le32 data_block_start;   /* Start of data blocks */
        __u8   padding[4060];      /* Padding to 4096 bytes */
    };

Buradaki *__le32* türü *little endian* 4 byte'lık tamsayı türünü temsil etmektedir. Buradaki
*little endian* belirlemesiyle derleyici özel bir işlem uygulamaz; yalnızca dosya sistemini
gerçekleştirenler için okunabilirliği artırmaktadır. Yani burada söylenmek istenen şey
"makineniz big endian olsa bile bu bilgiler diskte little endian biçiminde tutulmaktadır"
bilgisidir.

Her dosya sisteminde bir *sihirli sayı* (*magic number*) bulundurulur. *simplefs* dosya
sistemimizdeki sihirli sayı süper blokta ``0x53494D46`` ("SIMF") biçiminde tutulmaktadır.
Süper blok içerisindeki ``block_size`` elemanı her zaman 4096 biçimindedir. İleride bu dosya
sistemini farklı blok uzunluklarıyla da çalışabilir hale getirebilirsiniz. Ancak bizim dosya
sistemimizde bir blok her zaman 4096 byte'tır.

Süper bloktaki ``inode_count`` elemanı inode elemanlarının toplam sayısını belirtmektedir. Disk
bölümü içerisinde toplamda buradaki sayıdan daha fazla dosya ve dizin bulunamaz; çünkü her dosya
ve dizin için bir inode elemanı kullanılmaktadır. ``block_count`` alanında ise diskteki tüm
blokların sayısı tutulmaktadır; bu bloklara metadata blokları da dahildir. ``free_inodes`` ve
``free_blocks`` elemanları kullanılmayan inode elemanlarının ve blokların sayısını belirtmektedir.

Inode tablosunun yeri ``inode_table_block`` alanında tutulmaktadır. Dosya sistemimizde burada her
zaman 3 değeri bulunacaktır. Ancak bu dosya sistemini iyileştirmek isterseniz geleceğe uyum için
bu alan bulundurulmaktadır. Inode elemanlarının sayısı formatlama sırasında belirtilmektedir.
Dolayısıyla inode bloktaki blok sayısı da değişebilmektedir. Inode bloğun bir blok uzunlukta
olmayabileceğine dikkat ediniz. ``data_block_start`` alanında data bloğun başlangıç blok numarası
bulunmaktadır. Data bloğun ilk bloğunda kök dizinin içeriğinin bulunduğunu anımsayınız.

Bu alanların anlamları aşağıdaki tabloda özetlenmiştir:

.. list-table:: simplefs Süper Blok Alanları
   :widths: 22 10 68
   :header-rows: 1

   * - Alan
     - Tür
     - Açıklama
   * - ``magic``
     - ``__le32``
     - ``0x53494D46`` — sihirli sayı ("SIMF")
   * - ``block_size``
     - ``__le32``
     - Her zaman 4096 byte
   * - ``inode_count``
     - ``__le32``
     - Format sırasında belirlenir
   * - ``block_count``
     - ``__le32``
     - Aygıt boyutu / 4096
   * - ``free_inodes``
     - ``__le32``
     - Dinamik güncellenir
   * - ``free_blocks``
     - ``__le32``
     - Dinamik güncellenir
   * - ``inode_table_block``
     - ``__le32``
     - Her zaman 3
   * - ``inode_table_size``
     - ``__le32``
     - ``(inode_count + 63) / 64`` — yukarı yuvarlanır
   * - ``data_block_start``
     - ``__le32``
     - ``3 + inode_table_size + 1``
   * - ``padding[4060]``
     - ``__u8[]``
     - Bloğu 4096 byte'a tamamlamak için dolgu

İzleyen paragraflarda da göreceğimiz gibi bir inode elemanı inode blokta 64 byte yer kaplamaktadır.
Dolayısıyla bir blokta 64 inode elemanı bulunmaktadır. Yukarıdaki tabloda ``inode_table_size``
açıklamasında inode elemanlarının sayısı 64'e doğru yukarı yuvarlanmıştır.

Disk *simplefs* dosya sistemi ile formatlanırken inode sayısı da formatlama sırasında
belirtilmektedir. Örneğin:

.. code-block:: bash

    $ ./mkfs.simplefs /dev/loop0 512

Disk Inode Elemanının Yapısı
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
Inode bloğun inode elemanlarından oluştuğunu ve *simplefs* dosya sistemimizde bu bloğun değişken
uzunlukta olabileceğini belirtmiştik. *simplefs* dosya sisteminde diskteki bir inode elemanının
alanları ``simplefs_disk_inode`` adlı C yapısıyla tanımlanmıştır:
 
.. code-block:: c
 
    struct simplefs_disk_inode {
        __le32 mode;            /* File type + permissions */
        __le32 uid;             /* Owner user ID */
        __le32 gid;             /* Owner group ID */
        __le32 size;            /* File size in bytes */
        __le32 nlink;           /* Hard link count */
        __le32 blocks;          /* Block count (0 or 1) */
        __le32 block_no;        /* Data block number */
        __le32 ctime;           /* Creation time */
        __le32 mtime;           /* Modification time */
        __le32 atime;           /* Access time */
        __u8   padding[24];     /* Padding to 64 bytes */
    };
 
Inode elemanının ``mode`` alanında dosyanın tür bilgisi ve erişim hakları tutulmaktadır. Burada
Linux'un uyguladığı bitsel organizasyon kullanılmaktadır:
 
.. figure:: _static/simplefs-mode-bits.png
   :align: center
   :alt: inode mode alanı bit organizasyonu
   :width: 90%
 
   inode ``mode`` alanının bit organizasyonu
 
.. list-table:: ``mode`` Alanı Bit Açıklamaları
   :widths: 12 88
   :header-rows: 1
 
   * - Kısaltma
     - Açıklama
   * - ``UID``
     - setuid biti
   * - ``GID``
     - setgid biti
   * - ``STK``
     - sticky bit
   * - ``UR``
     - Kullanıcı okuma (*user read*)
   * - ``UW``
     - Kullanıcı yazma (*user write*)
   * - ``UX``
     - Kullanıcı çalıştırma (*user execute*)
   * - ``GR``
     - Grup okuma (*group read*)
   * - ``GW``
     - Grup yazma (*group write*)
   * - ``GX``
     - Grup çalıştırma (*group execute*)
 
Inode elemanının ``uid`` ve ``gid`` alanları dosyaya ilişkin kullanıcı ve grup kimliklerini
belirtmektedir. ``size`` alanı dosyanın uzunluğunu, ``nlink`` alanı hard link sayacını
belirtmektedir. *simplefs* sistemimizde dosyalar en fazla bir blok yer kapladığından yalnızca tek
bir bloğun yeri tutulacaktır. Inode elemanının ``block_no`` alanı dosyanın bulunduğu bloğu
belirtmektedir.
 
Inode elemanının ``ctime``, ``mtime`` ve ``atime`` alanları sırasıyla inode bilgilerinin son
güncelleme zamanını, dosyanın son değiştirilme zamanını ve dosyanın son okunma zamanını
belirtmektedir.
Buradaki zamanlar 01/01/1970'ten geçen saniye sayısı biçiminde tutulmaktadır. Biz burada her ne
kadar *dosya* terimini kullandıysak da dizinleri de kastetmekteyiz; çünkü dizinlerin de inode
elemanları vardır.
 
Inode tabanlı dosya sistemlerinde inode bloktaki ilk inode elemanı *reserved* bırakılmaktadır. Bu
inode elemanının inode numarası 0'dır. (Eski sistemlerde 0 numaralı inode elemanı "başarısızlık"
anlamında kullanılıyordu.) Linux'un ext dosya sistemlerinde ilk 2 inode elemanı *reserved*
yapılmıştır. Biz *simplefs* dosya sistemimizde yalnızca 0 numaralı inode elemanını *reserved*
yapacağız. Bizim dosya sistemimizde kök dizinin bilgileri her zaman 1 numaralı inode elemanında
bulunacaktır.

Dizin Girişleri
~~~~~~~~~~~~~~~~
 
*simplefs* dosya sistemimizdeki her dizin girişi eşit uzunluktadır. (ext dosya sistemlerinde
bunların eşit uzunlukta olmadığını anımsayınız.) *simplefs* dosya sistemimizdeki dizin
girişlerinin formatı ``simplefs_disk_dentry`` yapısıyla tanımlanmıştır:
 
.. code-block:: c
 
    #define SIMPLEFS_FILENAME_MAXLEN        32
 
    struct simplefs_disk_dentry {
        __le32 inode;                           /* İnode number */
        char name[SIMPLEFS_FILENAME_MAXLEN];    /* File name */
    };
 
Dizin girişinin ilk alanında ilgili dosyanın inode numarası bulunmaktadır. Dosya ismi her zaman
32 byte yer kaplamaktadır. Dosya isminin sonunda null karakter vardır. Biz genel olarak dizin
girişlerindeki isimlerin sonuna null padding uygulayacağız. Bu durumda dosya isimleri en fazla
31 karakter olabilmektedir.
 
Formatlama Programı: mkfs.simplefs
------------------------------------
 
Bir dosya sistemini gerçekleştirirken ilk yapacağımız işlemlerden biri formatlama programının
yazılmasıdır. Formatlama programı disk bölümünü (yani blok aygıtını) metadata alanlarını
oluşturarak kullanıma hazır hale getirmektedir. Dosya sistemi aygıt sürücümüz bu metadata
alanlarını kullanacaktır. Biz formatlama programımıza *mkfs.simplefs* ismini vereceğiz.
 
*simplefs* dosya sisteminin formatlanması sırasında şu işlemler yapılmalıdır:
 
1. Süper blok bilgileri oluşturulup blok aygıtının ilk bloğuna yazılmalıdır.
 
2. Inode bitmap'ta 0 ve 1 numaralı inode elemanlarının bitleri 1 yapılmalıdır. Anımsayacağınız
   gibi 0 numaralı inode elemanı *reserved* durumdaydı, 1 numaralı inode elemanı ise kök dizine
   ilişkindi.
 
3. Data bitmap'in de ilk duruma getirilmesi gerekir. 0 numaralı data bloğu kök dizini içerdiği
   için onun bitinin 1 yapılması gerekir.
 
4. Inode bloğun da ilk durumuna getirilmesi gerekir. Inode bloğun ilk inode elemanı 0'lar
   içerecek biçimde boş bırakılmalıdır. Ancak sonraki inode elemanı (yani 1 numaralı inode
   elemanı) kök dizin bilgilerini tutacak biçimde güncellenmelidir.
 
5. Sıra kök dizindeki dizin girişlerinin başlangıçtaki durumunu oluşturmaya gelmiştir. Kök
   dizinde "." ve ".." isimli iki dizin girişinin bulundurulması gerekir. Bu dizin girişlerinin
   inode numaralarının yine kök dizinin inode numarasını (örneğimizde 1) içermesi gerekmektedir.
 
Format programımızda önce komut satırı argümanları kontrol edilmiştir:
 
.. code-block:: c
 
    int n_inodes = DEF_NUMBER_OF_INODES;
    int fd;
 
    if (argc > 3) {
        fprintf(stderr, "too many arguments!\n");
        fprintf(stderr, "usage: mkfs.simplefs <device_path> [number_of_inodes]\n");
        exit(EXIT_FAILURE);
    }
    if (argc == 1) {
        fprintf(stderr, "too few arguments!\n");
        fprintf(stderr, "usage: mkfs.simplefs <device_path> [number_of_inodes]\n");
        exit(EXIT_FAILURE);
    }
 
    if (argc == 3) {
        n_inodes = atoi(argv[2]);
        if (n_inodes < MIN_NUMBER_OF_INODES || n_inodes > MAX_NUMBER_OF_INODES) {
            fprintf(stderr, "incorrect number of inodes!...\n");
            exit(EXIT_FAILURE);
        }
    }
 
Sonra aygıt dosyası ``open`` fonksiyonuyla açılmıştır:
 
.. code-block:: c
 
    if ((fd = open(argv[1], O_WRONLY)) == -1)
        exit_sys(argv[1]);
 
Süper bloğun yazılması ``write_super_block`` fonksiyonu tarafından yapılmaktadır:
 
.. code-block:: c
 
    int write_super_block(int fd, int n_inodes, struct simplefs_disk_super_block *sbd)
    {
        uint64_t size;
 
        sbd->magic = SIMPLEFS_MAGIC;
        sbd->block_size = SIMPLEFS_BLOCK_SIZE;
        sbd->inode_count = n_inodes;
        /*
        if (ioctl(fd, BLKGETSIZE64, &size) == -1)
            return -1;
        */
        if ((size = lseek(fd, 0, SEEK_END)) == -1)
            return -1;
 
        sbd->block_count = size / SIMPLEFS_BLOCK_SIZE;
        sbd->free_inodes = n_inodes - 2;
        sbd->inode_table_block = 3;
        sbd->inode_table_size = (n_inodes + INODE_SIZE - 1) / INODE_SIZE;
        sbd->data_block_start = 3 + sbd->inode_table_size;
        sbd->free_blocks = sbd->block_count - sbd->data_block_start - 1;
 
        lseek(fd, 0, SEEK_SET);
        if (write(fd, sbd, sizeof(*sbd)) != (ssize_t)sizeof(*sbd))
            return -1;
 
        return 0;
    }
 
Burada diskin uzunluğunu bulmak için dosya göstericisini sona çekip onun konumunu aldık. Aslında
aynı işlem blok aygıt sürücülerine ``BLKGETSIZE64`` ioctl komutu gönderilerek de yapılabilmektedir.
``write_super_block`` fonksiyonunun ikinci parametresinin inode elemanlarının sayısını belirttiğine
dikkat ediniz.
 
Süper bloğu oluşturduktan sonra inode bitmap ve data bitmap blokları oluşturulmalıdır. Inode
bitmap içerisindeki her bit bir inode elemanının dolu mu boş mu olduğunu tutmaktadır. Başlangıçta
ilk iki inode elemanı doludur. Anımsayacağınız gibi 0'ıncı inode elemanı pek çok inode tabanlı
dosya sisteminde hiç kullanılmamaktadır. Bizim dosya sistemimizde kök dizinin bilgileri 1 numaralı
inode elemanındadır. Inode bitmap'in ilk iki bitini 1'leyip geri kalan bitlerini 0'lamak için en
pratik yöntem önce içi sıfırlarla dolu bir dizi almak, sonra dizinin ilk elemanının düşük anlamlı
iki bitini 1'lemektir. Bu işlem formatlama programımızda şöyle yapılmıştır:
 
.. code-block:: c
 
    unsigned char bitmap[SIMPLEFS_BLOCK_SIZE] = {0};
    /* ... */
 
    bitmap[0] = 0x03;           /* first two bits in inode bitmap must be 1 */
    if (write(fd, bitmap, SIMPLEFS_BLOCK_SIZE) != SIMPLEFS_BLOCK_SIZE) {
        fprintf(stderr, "cannot write inode bitmap!..\n");
        exit(EXIT_FAILURE);
    }
 
Data bitmap'in yalnızca ilk biti 1 olmalıdır. Çünkü diskin data bloğunda yalnızca ilk blok
(orada kök dizinin olduğunu anımsayınız) doludur. Bu işlem de formatlama programımızda şöyle
yapılmıştır:
 
.. code-block:: c
 
    bitmap[0] = 0x01;       /* first bit in data bitmap must be 1 */
    if (write(fd, bitmap, SIMPLEFS_BLOCK_SIZE) != SIMPLEFS_BLOCK_SIZE) {
        fprintf(stderr, "cannot write data bitmap!..\n");
        exit(EXIT_FAILURE);
    }
 
Sıra inode tablosunun yazılmasına gelmiştir. Inode tablosundaki ilk inode elemanının boş olması
gerektiğini anımsayınız. Sonraki inode elemanı (yani 1 numaralı inode elemanı) kök dizinine
ilişkin inode elemanı olmalıdır. Format programımızda inode tablosu ``write_inode_table`` isimli
bir fonksiyonla ilk haline getirilmiştir:
 
.. code-block:: c
 
    int write_inode_table(int fd, struct simplefs_disk_super_block *sbd)
    {
        unsigned char buf[SIMPLEFS_BLOCK_SIZE] = {0};
        struct simplefs_disk_inode inoded = {0};
        time_t curtime;
        off_t pos;
 
        pos = lseek(fd, 0, SEEK_CUR);
        for (int i = 0; i < sbd->inode_table_size; ++i)
            if (write(fd, buf, SIMPLEFS_BLOCK_SIZE) != SIMPLEFS_BLOCK_SIZE)
                return -1;
 
        lseek(fd, pos, SEEK_SET);
        if (write(fd, &inoded, sizeof(inoded)) != (ssize_t)sizeof(inoded))
            return -1;
 
        inoded.mode = S_IFDIR | S_IRWXU | S_IRWXG | S_IRWXO;
        inoded.uid = 0;
        inoded.gid = 0;
        inoded.size = SIMPLEFS_BLOCK_SIZE;
        inoded.nlink = 3;
        inoded.blocks = 1;
        inoded.block_no = sbd->data_block_start;
 
        curtime = time(NULL);
        inoded.ctime = curtime;
        inoded.mtime = curtime;
        inoded.atime = curtime;
 
        if (write(fd, &inoded, sizeof(inoded)) != (ssize_t)sizeof(inoded))
            return -1;
 
        return 0;
    }
 
Kök dizine ilişkin inode elemanının ``size`` alanına ``SIMPLEFS_BLOCK_SIZE`` değerini
yerleştirdiğimize dikkat ediniz. Pek çok dosya sisteminde dizin dosyalarının uzunluğu onlar için
ayrılan blokların toplam uzunluğu ile ifade edilmektedir. Biz de *simplefs* dosya sistemimizde
tüm dizinlerin uzunluklarını ``SIMPLEFS_BLOCK_SIZE`` yani 4096 biçiminde set edeceğiz.
 
Artık son olarak kök dizinin girişlerinin oluşturulması gerekir. Kök dizinin ilk girişinin "."
ve ".." dizinlerinden oluşması zorunludur. Bu dizin girişlerini kök dizine ilişkin bloğun ilk iki
girişine yazmak için formatlama programımızda ``write_dentries`` fonksiyonu kullanılmıştır:
 
.. code-block:: c
 
    int write_dentries(int fd, struct simplefs_disk_super_block *sbd)
    {
        unsigned char buf[SIMPLEFS_BLOCK_SIZE] = {0};
        struct simplefs_disk_dentry de = {0};
 
        lseek(fd, sbd->data_block_start * SIMPLEFS_BLOCK_SIZE, SEEK_SET);
        if (write(fd, buf, SIMPLEFS_BLOCK_SIZE) != SIMPLEFS_BLOCK_SIZE)
            return -1;
 
        lseek(fd, sbd->data_block_start * SIMPLEFS_BLOCK_SIZE, SEEK_SET);
        de.inode = 2;
        strcpy(de.name, ".");
        if (write(fd, &de, SIMPLEFS_DENTRY_LEN) != SIMPLEFS_DENTRY_LEN)
            return -1;
 
        de.inode = 2;
        strcpy(de.name, "..");
        if (write(fd, &de, SIMPLEFS_DENTRY_LEN) != SIMPLEFS_DENTRY_LEN)
            return -1;
 
        return 0;
    }
 
Formatlama programımızın tamamı ``mkfs.simplefs.c`` ismiyle aşağıda verilmiştir:
 
.. code-block:: c
 
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    #include <time.h>
    #include <fcntl.h>
    #include <sys/stat.h>
    #include <unistd.h>
    #include <sys/ioctl.h>
    #include <linux/fs.h>
    #include <linux/types.h>
 
    #define SIMPLEFS_BLOCK_SIZE         4096
    #define DEF_NUMBER_OF_INODES        1024
    #define MAX_NUMBER_OF_INODES        (4096 * 8)
    #define MIN_NUMBER_OF_INODES        50
    #define INODE_SIZE                  64
    #define SIMPLEFS_FILENAME_MAXLEN    32
    #define SIMPLEFS_DENTRY_LEN         36
    #define SIMPLEFS_MAGIC              0x53494D46
 
    struct simplefs_disk_super_block {
        __le32 magic;              /* 0x464D4953 ("SIMF") */
        __le32 block_size;         /* 4096 */
        __le32 inode_count;        /* Total inodes */
        __le32 block_count;        /* Total blocks */
        __le32 free_inodes;        /* Free inodes */
        __le32 free_blocks;        /* Free blocks */
        __le32 inode_table_block;  /* Start of the inode table (3) */
        __le32 inode_table_size;   /* Size of the inode table */
        __le32 data_block_start;   /* Start of data blocks */
        __u8   padding[4060];      /* Padding to 4096 bytes */
    };
 
    struct simplefs_disk_inode {
        __le32 mode;            /* File type + permissions */
        __le32 uid;             /* Owner user ID */
        __le32 gid;             /* Owner group ID */
        __le32 size;            /* File size in bytes */
        __le32 nlink;           /* Hard link count */
        __le32 blocks;          /* Block count (0 or 1) */
        __le32 block_no;        /* Data block number */
        __le32 ctime;           /* Creation time */
        __le32 mtime;           /* Modification time */
        __le32 atime;           /* Access time */
        __u8   padding[24];     /* Padding to 64 bytes */
    };
 
    struct simplefs_disk_dentry {
        __le32 inode;                           /* Inode number */
        char name[SIMPLEFS_FILENAME_MAXLEN];    /* File name */
    };
 
    int write_super_block(int fd, int n_inodes, struct simplefs_disk_super_block *sbd);
    int write_inode_table(int fd, struct simplefs_disk_super_block *sbd);
    int write_dentries(int fd, struct simplefs_disk_super_block *sbd);
    void exit_sys(const char *msg);
 
    /* usage: mkfs.simplefs <device_path> [number_of_inodes] */
 
    int main(int argc, char *argv[])
    {
        int n_inodes = DEF_NUMBER_OF_INODES;
        int fd;
        unsigned char bitmap[SIMPLEFS_BLOCK_SIZE] = {0};
        struct simplefs_disk_super_block sbd = {0};
 
        if (argc > 3) {
            fprintf(stderr, "too many arguments!\n");
            fprintf(stderr, "usage: mkfs.simplefs <device_path> [number_of_inodes]\n");
            exit(EXIT_FAILURE);
        }
        if (argc == 1) {
            fprintf(stderr, "too few arguments!\n");
            fprintf(stderr, "usage: mkfs.simplefs <device_path> [number_of_inodes]\n");
            exit(EXIT_FAILURE);
        }
 
        if (argc == 3) {
            n_inodes = atoi(argv[2]);
            if (n_inodes < MIN_NUMBER_OF_INODES || n_inodes > MAX_NUMBER_OF_INODES) {
                fprintf(stderr, "incorrect number of inodes!. Number of inodes must be "
                                "between 50 and 32768...\n");
                exit(EXIT_FAILURE);
            }
        }
 
        if ((fd = open(argv[1], O_WRONLY)) == -1)
            exit_sys(argv[1]);
 
        if (write_super_block(fd, n_inodes, &sbd) == -1)
            exit_sys("write_super_block");
 
        bitmap[0] = 0x03;       /* first two bits in inode bitmap must be 1 */
        if (write(fd, bitmap, SIMPLEFS_BLOCK_SIZE) != SIMPLEFS_BLOCK_SIZE) {
            fprintf(stderr, "cannot write inode bitmap!..\n");
            exit(EXIT_FAILURE);
        }
 
        bitmap[0] = 0x01;       /* first bit in data bitmap must be 1 */
        if (write(fd, bitmap, SIMPLEFS_BLOCK_SIZE) != SIMPLEFS_BLOCK_SIZE) {
            fprintf(stderr, "cannot write data bitmap!..\n");
            exit(EXIT_FAILURE);
        }
 
        if (write_inode_table(fd, &sbd) == -1) {
            fprintf(stderr, "cannot write inode table!..\n");
            exit(EXIT_FAILURE);
        }
 
        if (write_dentries(fd, &sbd) == -1) {
            fprintf(stderr, "cannot write dentries!..\n");
            exit(EXIT_FAILURE);
        }
 
        printf("mkfs.simplefs completed successfully...\n");
 
        return 0;
    }
 
    int write_super_block(int fd, int n_inodes, struct simplefs_disk_super_block *sbd)
    {
        uint64_t size;
 
        sbd->magic = SIMPLEFS_MAGIC;
        sbd->block_size = SIMPLEFS_BLOCK_SIZE;
        sbd->inode_count = n_inodes;
        /*
        if (ioctl(fd, BLKGETSIZE64, &size) == -1)
            return -1;
        */
        if ((size = lseek(fd, 0, SEEK_END)) == -1)
            return -1;
 
        sbd->block_count = size / SIMPLEFS_BLOCK_SIZE;
        sbd->free_inodes = n_inodes - 2;
        sbd->inode_table_block = 3;
        sbd->inode_table_size = (n_inodes + INODE_SIZE - 1) / INODE_SIZE;
        sbd->data_block_start = 3 + sbd->inode_table_size;
        sbd->free_blocks = sbd->block_count - sbd->data_block_start - 1;
 
        lseek(fd, 0, SEEK_SET);
        if (write(fd, sbd, sizeof(*sbd)) != (ssize_t)sizeof(*sbd))
            return -1;
 
        return 0;
    }
 
    int write_inode_table(int fd, struct simplefs_disk_super_block *sbd)
    {
        unsigned char buf[SIMPLEFS_BLOCK_SIZE] = {0};
        struct simplefs_disk_inode inoded = {0};
        time_t curtime;
        off_t pos;
 
        pos = lseek(fd, 0, SEEK_CUR);
        for (int i = 0; i < sbd->inode_table_size; ++i)
            if (write(fd, buf, SIMPLEFS_BLOCK_SIZE) != SIMPLEFS_BLOCK_SIZE)
                return -1;
 
        lseek(fd, pos, SEEK_SET);
        if (write(fd, &inoded, sizeof(inoded)) != (ssize_t)sizeof(inoded))
            return -1;
 
        inoded.mode = S_IFDIR | S_IRWXU | S_IRWXG | S_IRWXO;
        inoded.uid = 0;
        inoded.gid = 0;
        inoded.size = SIMPLEFS_BLOCK_SIZE;
        inoded.nlink = 3;
        inoded.blocks = 1;
        inoded.block_no = sbd->data_block_start;
 
        curtime = time(NULL);
        inoded.ctime = curtime;
        inoded.mtime = curtime;
        inoded.atime = curtime;
 
        if (write(fd, &inoded, sizeof(inoded)) != (ssize_t)sizeof(inoded))
            return -1;
 
        return 0;
    }
 
    int write_dentries(int fd, struct simplefs_disk_super_block *sbd)
    {
        unsigned char buf[SIMPLEFS_BLOCK_SIZE] = {0};
        struct simplefs_disk_dentry de = {0};
 
        lseek(fd, sbd->data_block_start * SIMPLEFS_BLOCK_SIZE, SEEK_SET);
        if (write(fd, buf, SIMPLEFS_BLOCK_SIZE) != SIMPLEFS_BLOCK_SIZE)
            return -1;
 
        lseek(fd, sbd->data_block_start * SIMPLEFS_BLOCK_SIZE, SEEK_SET);
        de.inode = 2;
        strcpy(de.name, ".");
        if (write(fd, &de, SIMPLEFS_DENTRY_LEN) != SIMPLEFS_DENTRY_LEN)
            return -1;
 
        de.inode = 2;
        strcpy(de.name, "..");
        if (write(fd, &de, SIMPLEFS_DENTRY_LEN) != SIMPLEFS_DENTRY_LEN)
            return -1;
 
        return 0;
    }
 
    void exit_sys(const char *msg)
    {
        perror(msg);
 
        exit(EXIT_FAILURE);
    }
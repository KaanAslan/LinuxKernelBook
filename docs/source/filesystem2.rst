.. _dosya-sistemi-2:

=========================
Dosya Sistemi - 2. Bölüm
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


Diskin Formatlanması ve Mount Edilmesi
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

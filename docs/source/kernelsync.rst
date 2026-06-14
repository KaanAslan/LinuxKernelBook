=========================
Çekirdek Senkronizasyonu
=========================

Kitabımızın bu bölümünde Linux çekirdeğindeki senkronizasyon mekanizmaları üzerinde
duracağız. Çekirdek içerisindeki kodlar iç içe geçebilecek biçimde (re-entrant)
çalışabilmektedir. Eğer makinenizde birden fazla işlemci ya da çekirdek varsa
çekirdek kodları bunlar tarafından eş zamanlı biçimde işletilebilmektedir. Tek
işlemcili ya da çekirdekli sistemlerde de *thread'ler arası geçiş ve kesme
mekanizmalarından dolayı* akışların iç içe geçmesi söz konusu olabilmektedir.

Linux çekirdekleri 2.6 ile birlikte *preemptive* hale getirilmiştir. Eskiden
2.6'dan önceki çekirdeklerde bir thread akışı çekirdek moduna geçtiğinde oradan
çıkana kadar kesilme (preemption) oluşmuyordu. Ancak 2.6 çekirdekleriyle birlikte
bir thread akışı örneğin bir sistem fonksiyonunda ilerlerken de quantum süresi
dolduğundan dolayı çekirdek içerisinde de kesilebilmektedir.

Linux çekirdeğinde oldukça çeşitli senkronizasyon nesneleri bulunmaktadır. Bu
bölümde biz bu nesneleri ele alıp onların nasıl kullanıldığını açıklayacağız.
Aynı zamanda çok işlemcili ya da çekirdeklerdeki senkronizasyon sorunlarını ele
alacağız.

Kritik Kod Blokları
===================

Çekirdek kodlarında senkronizasyona neden gerek duyulmaktadır? İşte tıpkı kullanıcı
modundaki çok thread'li uygulamalarda olduğu gibi bir akış çekirdek içerisinde
paylaşılan bir veri yapısı üzerinde işlem yaparken bir biçimde thread'ler arası
geçiş ya da kesme olayı söz konusu olduğunda başka bir akış da bu paylaşılan veri
yapısını kullanmak isterse bu veri yapısı bozulabilmektedir. Çok çekirdekli
sistemlerde farklı çekirdeklerdeki thread'ler de çekirdek içerisindeki ortak veri
yapıları üzerinde eş zamanlı işlemler yapabilmektedir. Örneğin çekirdek kodunun bir
bağlı listeye eleman eklediğini varsayalım. Tam bu işlemin ortalarında bir yerde
thread'ler arası geçiş oluşursa ya da başka bir çekirdekteki thread de aynı bağlı
liste üzerinde işlem yapmaya çalışırsa tüm veri yapısı bozulabilecektir.

Çekirdek senkronizasyonunda en önemli kavram *kritik kod blokları (critical section)* denilen
kavramdır. Başından sonuna kadar tek bir akış tarafından işletilmesi gereken kod bloklarına
*kritik kod blokları* denilmektedir. Kritik kod kavramını atomiklikle karıştırmayınız.
Atomiklik "bir işlem yapılırken thread'ler arası geçiş ya da kesme mekanizması
yoluyla işlemin kesintiye uğramaması" anlamına gelmektedir. Bir akış çekirdekteki
bir kritik kod bloğuna girdiğinde akış *preemption*'dan dolayı kesintiye uğrayabilir.
Ancak bu durumda bile başka bir akış kesintiye uğramış olan akış işini bitirene kadar
kritik kod bloğuna girmemelidir. Yani kritik kod bloğuna girmiş olan bir akışın kesintiye uğramaması
biçiminde bir koşul yoktur.

Çekirdek kodları kullanıcı modundaki kodlar gibi değildir. Çekirdek kodları aynı
zaman diliminde pek çok akış tarafından iç içe geçecek biçimde çalıştırılabilmektedir.
Bu nedenle çekirdek tasarımında ve aygıt sürücü yazımında senkronizasyon her zaman
göz önüne alınmalıdır. Maalesef senkronizasyon sorunlarının tespit edilmesi oldukça
zor olabilmektedir. Çünkü senkronizasyon problemlerinin oluşturduğu böceklerin
yeniden üretilmesi edilmesi oldukça zordur.

Çekirdek içerisindeki kritik kod bloklarının önemli bir bölümü birden fazla akışın
paylaşılan bir veri yapısına erişilmesi nedeniyle oluşturulmaktadır. Örneğin aynı
hash tablosuna birden fazla prosesin çağırdığı sistem fonksiyonları eleman ekleyebilir.
Bu durumda bu hash tablosunun böyle erişimlerde *seri hale getirilmesi (serialize edilmesi)* gerekir. Ancak
senkronizasyon sorunu yalnızca ortak veri yapılarına ve nesnelere erişirken ortaya
çıkmaz. Bu bölümde ele alacağımız senkronizasyonu gerektiren başka durumlar da
vardır.

Genel olarak (ancak her zaman değil) bir nesne — burada çekirdek alanı içerisinde
tahsis edilmiş bir alanı kastediyoruz — eğer birden fazla akış tarafından
kullanılıyorsa bu nesnenin senkronize edilmesi için ayrı bir senkronizasyon nesnesi
bulundurulmaktadır. Linux'un çekirdek kodlarında yapıların içerisinde senkronizasyon
nesnelerini görürseniz şaşırmayınız. Bir senkronizasyon nesnesi ile birden fazla
nesneyi korumak genel olarak iyi bir fikir değildir; çünkü bu nesnelerden birine
erişirken kilit alındığı için aslında alakasız olan diğerine erişim de engellenmiş
olacaktır. Her nesnenin ayrı bir senkronizasyon nesnesi ile korunması en normal olan
durumdur. Linux çekirdek nesnelerini incelediğinizde onları belirten yapıların
elemanlarında senkronizasyon nesneleri göreceksiniz.

Kritik Kod Bloklarının Manuel Oluşturulmasındaki Sorunlar
---------------------------------------------------------

Kritik kod blokları ancak özel makine komutları kullanılarak oluşturulabilmektedir.
Aşağıdaki gibi basit bir mantıkla kritik kod bloğu oluşturulamaz:

.. code-block:: c

    int g_flag = 0;
    /* ... */

    while (g_flag)
        ;
    g_flag = 1;
    ...
    ...         <KRİTİK KOD BLOĞU>
    ...
    g_flag = 0;

Bu biçimdeki manuel kritik kod bloğu oluşturma girişiminin iki sorunu vardır:

1. Bekleme bloke edilerek değil meşgul bir döngüde (busy loop) yapılmaktadır.
   Yani bir thread kritik kod bloğu içerisindeyse diğeri CPU zamanı harcayarak meşgul
   bir döngüde sürekli bekler.

2. Kodda açık bir pencere bulunmaktadır:

   .. code-block:: c

       while (g_flag)
           ;

       /* ← DİKKAT: burada thread'ler arası geçiş oluşabilir! */

       g_flag = 1;
       ...
       ...      <KRİTİK KOD BLOĞU>
       ...
       g_flag = 0;

   Yukarıda gösterilen noktada thread'ler arası geçiş oluşursa birden fazla
   thread kritik kod bloğuna girebilir.

İşte bu sakıncayı ortadan kaldırmak için özel makine komutlarından
faydalanılmaktadır. Bugün bilgisayar sistemlerinde birden fazla işlemci ya da çekirdek
bulunabildiği için kritik kod bloğunu oluşturan sistem programcılarının bunlara dikkat
etmesi gerekir. Linux'un çekirdek kodlarında zaten çeşitli senaryolar için
kullanılabilecek senkronizasyon nesneleri hazır biçimde bulunmaktadır. Bu bölümde
biz bu senkronizasyon nesnelerini ele alacağız. Bölümün sonlarına doğru da bu
senkronizasyon nesnelerinin oluşturulabilmesi için gereken makine komutları hakkında
bilgiler vereceğiz.

Blokeye Yol Açabilen ve Blokeye Yol Açmayan Senkronizasyon Nesneleri
--------------------------------------------------------------------

İşletim sistemindeki senkronizasyon nesnelerini temelde iki gruba ayırabiliriz:

1) Blokeye yol açabilen senkronizasyon nesneleri
2) Blokeye yol açmayan senkronizasyon nesneleri

Blokeye yol açabilen senkronizasyon nesneleri çalışmakta olan kodun çalışmasına ara vererek ileride ele alacağımız
*bekleme kuyruklarında (wait queue)* bekletilebildiği, yani göreli olarak uzun süre beklemeye yol açabilen senkronizasyon
nesneleridir. Blokeye yol açmayan senkronizasyon nesneleri ise akışın uykuya yatırılarak bekletilmediği senkronizasyon 
nesneleridir. Bunları da kendi aralarında iki kısma ayırabiliriz. Bunların bir bölümü okuma sırasında spin
yaparak beklemeye yol açabilmekte, diğer bölümü ise bekleme yapmadan okumayı sağlayabilmektedir. Okuma sırasında beklemeye 
yol açmayan modern senkronizasyon nesnelerine "klitsiz (lock-free) senkronizasyon nesnesleri" denilmektedir.

Bu bölümde açıklayacağımız çekirdek senkronizasyon nesnelerini kullanıcı modundaki thread senkronizasyonunda
kullanılan senkronizasyon nesneleri ile karıştırmayınız. Kullanıcı modundaki senkronizasyon nesneleri kullanıcı
modundaki thread'leri senkronize etmek için bulundurulmuştur. Oysa bu bölümde göreceğimiz senkronizasyon nesneleri
-isimleri benzer olsa da- çekirdek kodlarının senkronizasyonunda kullanılmaktadır. Tabii kullanıcı modundaki
senkronizasyon nesnelerinin bir bölümü aslında burada açıklayacağımız çekirdekteki senkronizasyon nesneleri
kullanılarak yazılmıştır.

Mutex Nesneleri
===============

Kritik kod bloğu oluşturmak için en çok kullanılan senkronizasyon nesnelerinden biri *mutex (mutual exclusion)*
denilen nesnelerdir. (UNIX/Linux sistemlerinde kullanıcı modundan kullanılabilecek mutex nesneleri de
vardır. Yukarıda belirttiğimiz gibi biz burada çekirdeğin içerisinde bulunan mutex nesneleri üzerinde
duracağız.) Mutex nesneleri Linux çekirdeğine 2.6 versiyonlarıyla eklenmiştir. Bundan önce mutex işlemleri
ikili semaphore'larla yapılıyordu.

Çekirdeğin mutex mekanizması kullanım bakımından kullanıcı modundaki mutex mekanizmasına çok
benzemektedir. Çekirdek mutex nesnelerinin yine thread temelinde sahipliği vardır. Çekirdek mutex
nesneleri thread'i bloke edip onu bekleme kuyruklarında bekletebilmektedir.

Mutex mekanizması şöyle işletilmektedir: Önce global düzeyde ya da çekirdeğin heap sisteminde bir mutex
nesnesi yaratılır. Kritik kod bloğuna girişte bu mutex nesnesinin sahipliği ele geçirilmeye çalışılır. Mutex'in
sahipliğinin ele geçirilmesine *mutex'in kilitlenmesi (mutex lock)* de denilmektedir. Eğer mutex'in
sahipliği ele geçirilirse (yani mutex kilitlenirse) sahiplik bırakılana kadar (yani kilit bırakılana kadar)
başka bir thread kritik kod bloğuna giremez. Mutex'in sahipliğini almaya çalışan thread mutex kilitli ise bloke
olarak mutex kilidi açılana kadar bekler. Mutex'in sahipliğini almış olan thread kritik kod bloğundan çıkarken
mutex'in sahipliğini bırakır (yani mutex'in kilidini açar). Böylece blokede bekleyen thread'lerden biri
mutex'in sahipliğini alarak kritik kod bloğuna girer. Kritik kod bloğu tipik olarak şöyle oluşturulmaktadır:

.. code-block:: c

    mutex_lock(...);
    ...
    ...    <KRİTİK KOD BLOĞU>
    ...
    mutex_unlock(...);

Akışlardan biri ``mutex_lock`` fonksiyonuna geldiğinde eğer mutex kilitlenmemişse mutex'i kilitler ve
kritik kod bloğuna giriş yapar. Eğer mutex zaten kilitlenmişse ``mutex_lock`` fonksiyonunda thread bloke edilir
ve bekleme kuyruğuna alınır. Kritik kod bloğuna girmiş olan akış ``mutex_unlock`` fonksiyonu ile mutex nesnesinin
kilidini bırakır. Böylece nesneyi bekleyen thread'lerden biri nesnenin sahipliğini alarak mutex'i
kilitler. Birden fazla akışın ``mutex_lock`` fonksiyonunda bloke edilmesi durumunda mutex'in kilidi
açıldığında bunlardan hangisinin mutex kilidini alarak kritik kod bloğuna gireceği konusunda bir garanti
verilmemektedir. (İlk bloke olan akışın mutex kilidini alarak kritik kod bloğuna gireceğini düşünebilirsiniz,
ancak bunun bir garantisi yoktur.)

Çekirdekteki mutex mekanizmasının tipik gerçekleştirimi şöyledir:

1) ``mutex_lock`` işlemi sırasında işlemcinin maliyetsiz CAS (compare-and-swap) komutlarıyla mutex'in
   kilitli olup olmadığına bakılır. CAS komutları ileride ayrı bir başlıkta ele alınacaktır.

2) Diğer bir işlemcideki ya da çekirdekteki thread mutex'i kilitlemişse gereksiz bloke olmamak için yine
   CAS komutlarıyla biraz spin işlemi yapılır. Buradaki spin süresi çeşitli faktörlere bağlı olarak
   değişebilmektedir. Ancak ortalama 1 ile 10 ms arasında sürebilmektedir. Spin işleminin ne olduğu
   izleyen paragraflarda açıklanacaktır.

3) Spin işleminden sonuç elde edilemezse bloke oluşturulur.

4) Mutex nesnesinin kilidini alan thread mutex'in kilidini bırakınca çekirdek bu mutex'i bekleyen
   thread'leri uykudan uyandırır ve bunlardan biri mutex'in kilidini ele geçirir, diğerleri yine uykuya
   dalar.

Çekirdeğin mutex nesneleri tipik olarak şöyle kullanılmaktadır:

**1)** Mutex nesnesi ``mutex`` isimli bir yapıyla temsil edilmektedir. Sistem programcısı bu yapı türünden
global olarak ya da çekirdeğin heap sisteminde dinamik biçimde bir nesne yaratır ve ona ilk değerini
verir. ``DEFINE_MUTEX(name)`` makrosu hem ``struct mutex`` türünden nesneyi tanımlamakta hem de ona ilk
değerini vermektedir. Örneğin:

.. code-block:: c

    #include <linux/mutex.h>

    static DEFINE_MUTEX(g_mutex);

Bu makro güncel çekirdeklerde şöyle bildirilmiştir:

.. code-block:: c

    #define DEFINE_MUTEX(mutexname)                                     \
        struct mutex mutexname = __MUTEX_INITIALIZER(mutexname)

Buradaki ``__MUTEX_INITIALIZER`` makrosu da şöyle bildirilmiştir:

.. code-block:: c

    #define __MUTEX_INITIALIZER(lockname)                               \
        { .owner = ATOMIC_LONG_INIT(0)                                  \
        , .wait_lock = __RAW_SPIN_LOCK_UNLOCKED(lockname.wait_lock)     \
        , .wait_list = LIST_HEAD_INIT(lockname.wait_list)               \
        __DEBUG_MUTEX_INITIALIZER(lockname)                             \
        __DEP_MAP_MUTEX_INITIALIZER(lockname) }

``DEFINE_MUTEX`` makrosu yerine önce mutex nesnesi tanımlanıp nesneye ilk değerini ``mutex_init``
fonksiyonuyla da verebiliriz. Bu fonksiyon güncel çekirdeklerde makro biçiminde yazılmıştır:

.. code-block:: c

    #define mutex_init(mutex)                       \
    do {                                            \
        static struct lock_class_key __key;         \
        __mutex_init((mutex), #mutex, &__key);      \
    } while (0)

Fonksiyon mutex nesnesinin adresini almaktadır. Örneğin:

.. code-block:: c

    static struct mutex g_mutex;
    ...

    mutex_init(&g_mutex);

**2)** Mutex nesnesini kilitlemek için ``mutex_lock`` fonksiyonu kullanılır:

.. code-block:: c

    #include <linux/mutex.h>

    void mutex_lock(struct mutex *lock);

Fonksiyon parametresiyle mutex nesnesinin adresini almaktadır. Bloke olmadan mutex'i kilitlemek için
``mutex_trylock`` fonksiyonu da bulundurulmuştur:

.. code-block:: c

    #include <linux/mutex.h>

    int mutex_trylock(struct mutex *lock);

Eğer mutex kilitliyse bu fonksiyon bloke olmadan 0 değeriyle geri döner. Eğer mutex kilitli değilse
mutex'i kilitler ve fonksiyon 1 değeri ile geri döner.

Mutex nesnesi ``mutex_lock`` ile kilitlenmek istendiğinde bloke oluşursa bu blokeden sinyal yoluyla
çıkılamamaktadır. Örneğin ``mutex_lock`` ile çekirdek modunda biz mutex kilidini alamadığımızdan dolayı
bloke oluştuğunu düşünelim. Bu durumda ilgili prosese bir sinyal gelirse ve eğer o sinyal için sinyal
fonksiyonu set edilmişse thread uyandırılıp sinyal fonksiyonu çalıştırılmamaktadır. Ayrıca bu durumda biz
ilgili prosese ``SIGINT`` gibi, ``SIGKILL`` gibi sinyaller göndererek de prosesi sonlandıramayız. İşte eğer
mutex'in kilitli olması nedeniyle bloke oluştuğunda sinyal yoluyla thread'in uyandırılıp sinyal
fonksiyonunun çalıştırması ya da sinyal fonksiyonu set edilmemişse prosesin sonlandırılması isteniyorsa
mutex nesnesi ``mutex_lock`` ile değil, ``mutex_lock_interruptible`` fonksiyonu ile kilitlenmeye
çalışılmalıdır. ``mutex_lock_interruptible`` fonksiyonunun prototipi şöyledir:

.. code-block:: c

    #include <linux/mutex.h>

    int mutex_lock_interruptible(struct mutex *lock);

Fonksiyon eğer mutex kilidini alarak sonlanırsa 0 değerine, bloke olup sinyal dolayısıyla sonlanırsa
``-EINTR`` değerine geri dönmektedir. Programcı bu fonksiyonun 0 ile geri dönmediğini ya da ``-EINTR`` ile
geri döndüğünü tespit ettiğinde ilgili sistem fonksiyonunun yeniden çalıştırılabilirliğini sağlamak için
``-ERESTARTSYS`` ile geri dönebilir. Örneğin:

.. code-block:: c

    if (mutex_lock_interruptible(&g_mutex) != 0)
        return -ERESTARTSYS;

Sistem programcıları çoğu kez ``mutex_lock`` yerine ``mutex_lock_interruptible`` fonksiyonunu tercih
etmektedir.

**3)** Mutex nesnesinin kilidini bırakmak için (nesneyi unlock etmek için) ``mutex_unlock`` fonksiyonu
kullanılmaktadır:

.. code-block:: c

    #include <linux/mutex.h>

    void mutex_unlock(struct mutex *lock);

Bu durumda örneğin tipik olarak çekirdek kodlarında belli bir bölgeyi mutex yoluyla koruma işlemi şöyle
yapılmaktadır:

.. code-block:: c

    static DEFINE_MUTEX(g_mutex);
    ...

    if (mutex_lock_interruptible(&g_mutex) != 0)
        return -ERESTARTSYS;
    ...
    ...    KRİTİK KOD
    ...
    mutex_unlock(&g_mutex);

Mutex nesnesini kilitledikten sonra fonksiyonlarınızı geri döndürürken kilidi açmayı unutmayınız.

Çekirdeğin mutex nesneleri *özyinelemeli (recursive)* değildir. Yani thread kilitlediği bir mutex nesnesini
yeniden kilitlemeye çalışırsa *deadlock* oluşur.

Mutex Kullanımına Bir Örnek
---------------------------

Aşağıda mutex mekanizmasının çalışmasına ilişkin bir örnek verilmiştir. Burada aygıt sürücü için iki *ioctl*
kodu oluşturulmuştur. ``IOCTL_TEST1`` kodunda mutex'in sahipliği alınıp 30 saniye beklenmektedir.
``IOCTL_TEST2`` kodunda ise bekleme yapılmadan mutex'in sahipliği alınmak istenmiştir. Test için farklı terminallerde önce
*test-sync1* programını sonra da *test-sync2* programını çalıştırmalısınız. Mesajları *dmesg* komutuyla inceleyebilirsiniz.

Aygıt sürücüyü şöyle derleyebilirsiniz:

.. code-block:: console

    $ make file=test-driver

Aşağıdaki gibi yükleyebilirsiniz:

.. code-block:: console

    $ sudo ./load test-driver

Farklı terminallerden *test-sync1* ve *test-sync2* programlarını çalıştırdıktan sonra aygıt sürücüyü
çekirdekten çıkarmalısınız:

.. code-block:: console

    $ sudo ./unload test-driver

``test-driver.h``

.. code-block:: c

    #ifndef TEST_DRIVER_H_
    #define TEST_DRIVER_H_

    #include <linux/stddef.h>
    #include <linux/ioctl.h>

    #define TEST_DRIVER_MAGIC   't'
    #define IOC_TEST1           _IO(TEST_DRIVER_MAGIC, 0)
    #define IOC_TEST2           _IO(TEST_DRIVER_MAGIC, 1)

    #endif

``test-driver.c``

.. code-block:: c

    #include <linux/module.h>
    #include <linux/kernel.h>
    #include <linux/fs.h>
    #include <linux/cdev.h>
    #include <linux/delay.h>
    #include "test-driver.h"

    MODULE_LICENSE("GPL");
    MODULE_AUTHOR("Kaan Aslan");
    MODULE_DESCRIPTION("test-driver");

    static int test_driver_open(struct inode *inodep, struct file *filp);
    static int test_driver_release(struct inode *inodep, struct file *filp);
    static ssize_t test_driver_read(struct file *filp, char *buf, size_t size, loff_t *off);
    static ssize_t test_driver_write(struct file *filp, const char *buf, size_t size, loff_t *off);
    static long test_driver_ioctl(struct file *filp, unsigned int cmd, unsigned long arg);

    static long ioctl_test1(struct file *filp, unsigned long arg);
    static long ioctl_test2(struct file *filp, unsigned long arg);

    static dev_t g_dev;
    static struct cdev g_cdev;
    static struct file_operations g_fops = {
        .owner = THIS_MODULE,
        .open = test_driver_open,
        .read = test_driver_read,
        .write = test_driver_write,
        .release = test_driver_release,
        .unlocked_ioctl = test_driver_ioctl
    };

    static DEFINE_MUTEX(g_mutex);

    static int __init test_driver_init(void)
    {
        int result;

        printk(KERN_INFO "test-driver module initialization...\n");

        if ((result = alloc_chrdev_region(&g_dev, 0, 1, "test-driver")) < 0) {
            printk(KERN_INFO "cannot alloc char driver!...\n");
            return result;
        }
        cdev_init(&g_cdev, &g_fops);
        if ((result = cdev_add(&g_cdev, g_dev, 1)) < 0) {
            unregister_chrdev_region(g_dev, 1);
            printk(KERN_ERR "cannot add device!...\n");
            return result;
        }

        return 0;
    }

    static void __exit test_driver_exit(void)
    {
        cdev_del(&g_cdev);
        unregister_chrdev_region(g_dev, 1);

        printk(KERN_INFO "test-driver module exit...\n");
    }

    static int test_driver_open(struct inode *inodep, struct file *filp)
    {
        return 0;
    }

    static int test_driver_release(struct inode *inodep, struct file *filp)
    {
        return 0;
    }

    static ssize_t test_driver_read(struct file *filp, char *buf, size_t size, loff_t *off)
    {
        return 0;
    }

    static ssize_t test_driver_write(struct file *filp, const char *buf, size_t size, loff_t *off)
    {
        return 0;
    }

    static long test_driver_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)
    {
        long result;

        switch (cmd) {
            case IOC_TEST1:
                result = ioctl_test1(filp, arg);
                break;
            case IOC_TEST2:
                result = ioctl_test2(filp, arg);
                break;
            default:
                result = -ENOTTY;
        }

        return result;
    }

    static long ioctl_test1(struct file *filp, unsigned long arg)
    {
        if (mutex_lock_interruptible(&g_mutex) != 0)
            return -ERESTARTSYS;

        printk(KERN_INFO "mutex locked and wait 30 seconds...\n");

        ssleep(30);

        mutex_unlock(&g_mutex);

        printk(KERN_INFO "mutex unlocked...\n");

        return 0;
    }

    static long ioctl_test2(struct file *filp, unsigned long arg)
    {
        if (mutex_lock_interruptible(&g_mutex) != 0)
            return -ERESTARTSYS;

        printk(KERN_INFO "mutex locked...\n");

        mutex_unlock(&g_mutex);

        printk(KERN_INFO "mutex unlocked...\n");

        return 0;
    }

    module_init(test_driver_init);
    module_exit(test_driver_exit);

``Makefile``

.. code-block:: makefile

    obj-m += ${file}.o

    all:
    	make -C /lib/modules/$(shell uname -r)/build M=${PWD} modules
    clean:
    	make -C /lib/modules/$(shell uname -r)/build M=${PWD} clean

``load``

.. code-block:: bash

    #!/bin/bash

    module=$1
    mode=666

    /sbin/insmod ./${module}.ko ${@:2} || exit 1
    major=$(awk "\$2 == \"$module\" {print \$1}" /proc/devices)
    rm -f $module
    mknod -m $mode $module c $major 0

``unload``

.. code-block:: bash

    #!/bin/bash

    module=$1

    /sbin/rmmod ./${module}.ko || exit 1
    rm -f $module

``test-sync1.c``

.. code-block:: c

    #include <stdio.h>
    #include <stdlib.h>
    #include <fcntl.h>
    #include <unistd.h>
    #include <sys/ioctl.h>
    #include "test-driver.h"

    void exit_sys(const char *msg);

    int main(void)
    {
        int fd;

        if ((fd = open("test-driver", O_RDONLY)) == -1)
            exit_sys("open");

        if (ioctl(fd, IOC_TEST1) == -1)
            exit_sys("ioctl");

        close(fd);

        return 0;
    }

    void exit_sys(const char *msg)
    {
        perror(msg);

        exit(EXIT_FAILURE);
    }

``test-sync2.c``

.. code-block:: c

    #include <stdio.h>
    #include <stdlib.h>
    #include <fcntl.h>
    #include <unistd.h>
    #include <sys/ioctl.h>
    #include "test-driver.h"

    void exit_sys(const char *msg);

    int main(void)
    {
        int fd;

        if ((fd = open("test-driver", O_RDONLY)) == -1)
            exit_sys("open");

        if (ioctl(fd, IOC_TEST2) == -1)
            exit_sys("ioctl");

        close(fd);

        return 0;
    }

    void exit_sys(const char *msg)
    {
        perror(msg);

        exit(EXIT_FAILURE);
    }
    
Çekirdekteki Mutex Kodları
--------------------------

Güncel çekirdeklerde mutex yapısı ``linux/mutex_types.h`` dosyası içerisinde şöyle bildirilmiştir:

.. code-block:: c

    struct mutex {
        atomic_long_t           owner;
        raw_spinlock_t          wait_lock;
    #ifdef CONFIG_MUTEX_SPIN_ON_OWNER
        struct optimistic_spin_queue osq; /* Spinner MCS lock */
    #endif
        struct list_head        wait_list;
    #ifdef CONFIG_DEBUG_MUTEXES
        void    *magic;
    #endif
    #ifdef CONFIG_DEBUG_LOCK_ALLOC
        struct lockdep_map      dep_map;
    #endif
    };

Yapıya bazı elemanların konfigürasyon seçeneklerine bağlı olarak eklendiğine dikkat ediniz. Burada ``owner``
elemanı mutex kilidi için kullanılmaktadır. ``wait_lock`` elemanı nesnenin bazı elemanlarına erişirken nesneyi
korumak için bulundurulmuştur. Bloke olan thread'ler yapının ``wait_list`` elemanında kaydedilmemektedir.
``mutex_lock`` fonksiyonu ``kernel/locking/mutex.c`` dosyasında şöyle tanımlanmıştır:

.. code-block:: c

    void __sched mutex_lock(struct mutex *lock)
    {
        might_sleep();

        if (!__mutex_trylock_fast(lock))
            __mutex_lock_slowpath(lock);
    }
    EXPORT_SYMBOL(mutex_lock);

Buradaki ``might_sleep`` fonksiyonu eğer mutex nesnesi *atomik bir bağlamda (atomic context)* çağrılmışsa
debug mesajları oluşturmaktadır. Bunun dışında çalışma üzerinde bir etkisi yoktur. ``__mutex_trylock_fast``
fonksiyonu kilide bakıp eğer kilit açıksa hemen onu almaktadır. Kilit kapalı ise ``__mutex_lock_slowpath``
fonksiyonu çağrılmaktadır. Bu fonksiyon kendi içerisinde yukarıda belirttiğimiz gibi önce spin yaparak kilidin
açılmasını beklemekte, eğer kilit açılmazsa thread'i wait kuyruğuna yerleştirerek bloke olmaktadır. Linux
çekirdeğinin ileri versiyonlarındaki bu tür spin mekanizmalarına *optimistic spin* de denilmektedir. Buradaki
spin süresi belli koşullara bağlı olarak değişebilmektedir.

Semaphore Nesneleri
===================

Çekirdekte yaygın kullanılan senkronizasyon nesnelerinden bir diğeri de *semaphore* nesneleridir. Semaphore
nesneleri 1965 yılında Hollandalı bilgisayar bilimcisi Edsger W. Dijkstra tarafından ortaya atılmıştır.
Semaphore'lar bugün işletim sistemlerinin çekirdeklerinde ve kullanıcı modundaki thread senkronizasyonunda en
yaygın kullanılan senkronizasyon nesnelerinden biridir. (Semaphore *tren yollarındaki dur-geç lambaları* için
kullanılan bir sözcüktür. Bunu anafor sözcüğü ile karıştırmayınız.) Eskiden Linux çekirdeklerinde mutex
nesneleri yoktu. Mutex nesneleri yerine sonraki paragraflarda açıklayacağımız ikili (binary) semaphore
nesneleri kullanılıyordu.

Semaphore'lar sayaçlı senkronizasyon nesneleridir. Kritik kod bloğuna en fazla n tane thread'in girebilmesini
sağlamaktadır. Örneğin biz kritik kod bloğuna en fazla 3 thread'in girebilmesini isteyelim. Bu durumda birinci
thread kritik kod bloğuna girecektir. İkinci thread de üçüncü thread de girecektir. Ancak dördüncü ve beşinci
thread'ler kritik kod bloğuna giremeyecek ve bloke edilerek bekleme kuyruklarında bekletilecektir. Kritik kod bloğu
içerisindeki üç thread'ten birinin kritik kod bloğundan çıktığını varsayalım. Bu durumda kritik kod bloğuna girmek için
bekleyen thread'lerden biri kritik kod bloğuna girecektir. Görüldüğü gibi kritik kod bloğunun içerisinde en fazla 3 thread
bulunabilmektedir.

Kritik kod bloğuna en fazla n tane thread'in girebilmesinin sağlanması size anlamsız gelebilir. Ne de olsa kritik
koddaki iki thread bile paylaşılan kaynağı bozabilmektedir. Ancak semaphore'lar genellikle kaynak paylaştırmak
için kullanılmaktadır. Örneğin elimizde üç kaynak olabilir. Her gelen thread'e bunlardan birini tahsis
edebiliriz. Bu durumda ilk üç thread'e eldeki üç kaynak atanacaktır ancak kaynağı talep eden diğer thread'ler
CPU zamanı harcamadan blokede bekletilecektir. İşte bu mekanizma semaphore nesneleriyle oluşturulabilmektedir.

Semaphore nesnelerinin bir başlangıç sayaç değeri vardır. Bu başlangıç sayaç değeri kritik kod bloğuna en fazla kaç
thread'in girebileceğini belirtir. Kritik kod bloğuna giren thread bu sayaç değerini azaltır, çıkan thread bu sayaç
değerini artırır. Eğer semaphore'un sayacı 0 ise kritik kod bloğuna girmek isteyen thread bloke edilerek bekletilir.
Ta ki sayaç değeri 0'dan büyük olana kadar. Tabii sayacın artırılması ve azaltılması atomik bir biçimde
yapılmaktadır.

Çekirdekte Semaphore Kullanımı
-------------------------------

Çekirdek semaphore nesneleri şöyle kullanılmaktadır:

**1)** Semaphore nesnesi ``semaphore`` isimli bir yapıyla temsil edilmiştir. Güncel çekirdeklerde ``semaphore``
yapısı şöyle bildirilmiştir:

.. code-block:: c

    struct semaphore {
        raw_spinlock_t      lock;
        unsigned int        count;
        struct list_head    wait_list;
    #ifdef CONFIG_DETECT_HUNG_TASK_BLOCKER
        unsigned long       last_holder;
    #endif
    };

Buradaki ``lock`` elemanı nesne üzerinde işlem yaparken kritik kod bloğu oluşturmak için kullanılmaktadır. ``count``
elemanı semaphore sayacının o anki değerini belirtmektedir. ``wait_list`` elemanı ise bloke olan thread'lerin
saklandığı bekleme kuyruğunu temsil etmektedir. ``last_holder`` elemanın konfigürasyon seçeneği ile yapıya
eklendiğine dikkat ediniz. Bu eleman semaphore'dan geçen son thread'e ilişkin bilgiyi tutmaktadır.

Bir semaphore nesnesi ``DEFINE_SEMAPHORE(name)`` makrosuyla oluşturulabilir. Bu makro tıpkı mutex nesnelerinde
olduğu gibi hem semaphore nesnesini tanımlar hem de ona ilkdeğerini verir:

.. code-block:: c

    #include <linux/semaphore.h>

    static DEFINE_SEMAPHORE(g_sem);

Güncel çekirdeklerde bu makro şöyle tanımlanmıştır:

.. code-block:: c

    #define DEFINE_SEMAPHORE(_name, _n)  \
        struct semaphore _name = __SEMAPHORE_INITIALIZER(_name, _n)

Buradaki ``__SEMAPHORE_INITIALIZER`` makrosu da şöyle tanımlanmıştır:

.. code-block:: c

    #define __SEMAPHORE_INITIALIZER(name, n)                        \
    {                                                               \
        .lock       = __RAW_SPIN_LOCK_UNLOCKED((name).lock),       \
        .count      = n,                                           \
        .wait_list  = LIST_HEAD_INIT((name).wait_list)             \
        __LAST_HOLDER_SEMAPHORE_INITIALIZER                        \
    }

``DEFINE_SEMAPHORE`` makrosunun birinci parametresi semaphore değişkeninin ismini, ikinci parametresi ise
başlangıç semaphore sayacını belirtmektedir. Eskiden ``DEFINE_SEMAPHORE`` makrosu tek parametreliydi.
Semaphore sayacı da default 1 değeriyle olarak oluşturuluyordu. Bu makro 6.4 çekirdeği ile birlikte iki
parametreli hale getirilmiştir. 2.6 çekirdeği öncesinde bu makro yerine ``DECLARE_MUTEX`` makrosu
kullanılıyordu.

Semaphore nesnelerine başlangıç değerlerini vermek için ayrıca ``sema_init`` isimli bir fonksiyon da
bulundurulmuştur. Çünkü bazen semaphore nesnelerine ilkdeğer vermek mümkün olmayabilir. (Örneğin semaphore
nesnesi çekirdeğin heap alanında yaratılıyor olabilir.) Fonksiyonun prototipi şöyledir:

.. code-block:: c

    #include <linux/semaphore.h>

    void sema_init(struct semaphore *sem, int val);

Fonksiyon inline olarak yazılmıştır. Fonksiyonun birinci parametresi semaphore nesnesinin adresini, ikinci
parametresi ise semaphore sayacının başlangıç değerini belirtmektedir. Güncel çekirdeklerde bu fonksiyon
inline olarak şöyle yazılmıştır:

.. code-block:: c

    static inline void sema_init(struct semaphore *sem, int val)
    {
        static struct lock_class_key __key;
        *sem = (struct semaphore) __SEMAPHORE_INITIALIZER(*sem, val);
        lockdep_init_map(&sem->lock.dep_map, "semaphore->lock", &__key, 0);
    }

Fonksiyonun içerisinde ilkdeğer verme işleminin *designated initializer* sentaksıyla yapıldığına dikkat
ediniz.

**2)** Kritik kod bloğu ``down`` ve ``up`` fonksiyonları arasına alınır. ``down`` fonksiyonları sayacı bir eksilterek
kritik kod bloğuna giriş yapar. ``up`` fonksiyonu ise sayacı bir artırmaktadır. Fonksiyonların prototipleri
şöyledir:

.. code-block:: c

    #include <linux/semaphore.h>

    void down(struct semaphore *sem);
    int down_interruptible(struct semaphore *sem);
    int down_killable(struct semaphore *sem);
    int down_trylock(struct semaphore *sem);
    int down_timeout(struct semaphore *sem, long jiffies);
    void up(struct semaphore *sem);

Kritik kod bloğuna ``down`` fonksiyonu ile oluşturulduğunda thread bloke olursa sinyal yoluyla uyandırılamamaktadır.
Ancak kritik kod bloğu ``down_interruptible`` fonksiyonu ile oluşturulduğunda thread bloke olursa sinyal yoluyla
uyandırılabilmektedir. (Örneğin biz kritik kod bloğuna ``down`` fonksiyonuyla girmiş olalım. Thread'imizin bloke
olduğunu varsayalım. Şimdi kullanıcı modunda Ctrl+C tuşuyla ``SIGINT`` sinyalini oluşturduğumuzda bu bloke
çözülmeyecektir.) ``down_interruptible`` fonksiyonu normal sonlanmada 0 değerine, sinyal yoluyla sonlanmada
``-ERESTARTSYS`` değeri ile geri döner. Normal uygulama eğer bu fonksiyonlar ``-ERESTARTSYS`` ile geri
dönerse aygıt sürücüdeki fonksiyonun da aynı değerle geri döndürülmesidir. Zaten çekirdek bu ``-ERESTARTSYS``
geri dönüş değerini aldığında asıl sistem fonksiyonunu eğer sinyal için otomatik restart mekanizması aktif
değilse ``-EINTR`` değeri ile geri döndürmektedir. Bu da tabii POSIX fonksiyonlarının başarısız olup ``errno``
değerini ``-EINTR`` biçiminde set eder.

``down_killable`` fonksiyonu bloke olmuş thread'in yalnızca ``SIGKILL`` sinyalini kabul edip
sonlandırılabilmesini sağlamaktadır. ``down_killable`` fonksiyonunda eğer thread bloke olursa diğer sinyaller
yine blokeyi sonlandıramamaktadır.

``down_trylock`` nesnenin açık olup olmadığına bakmak için kullanılır. Eğer nesne açıksa yine sayaç 1
eksiltilir ve kritik kod bloğuna girilir. Bu durumda fonksiyon 0 dışı bir değerle geri döner. Nesne kapalıysa
(yani semaphore sayacı 0 ise) fonksiyon bloke olmadan 0 değerine geri döner. ``down_timeout`` ise en kötü
olasılıkla belli miktar *jiffy* zamanı kadar blokeye yol açmaktadır. (*jiffy* kavramı ileride ele
alınacaktır.) Fonksiyon zaman aşımı dolduğundan dolayı sonlanmışsa negatif hata koduna, normal bir biçimde
sonlanmışsa 0 değerine geri dönmektedir.

``up`` fonksiyonu yukarıda da belirttiğimiz gibi semaphore sayacını 1 artırmaktadır.

Bu durumda semaphore nesneleri ile kritik kod bloğu tipik olarak şöyle oluşturulmaktadır:

.. code-block:: c

    down_interruptible(&sem);
    ... 
    ...     <KRİTİK KOD BLOĞU> 
    ...
    up(&sem);

Binary Semaphore Örneği
------------------------

Aşağıda daha önce yapmış olduğumuz örneğin binary semaphore versiyonunu veriyoruz.

``test-driver.h``

.. code-block:: c

    #ifndef TEST_DRIVER_H_
    #define TEST_DRIVER_H_

    #include <linux/stddef.h>
    #include <linux/ioctl.h>

    #define TEST_DRIVER_MAGIC   't'
    #define IOC_TEST1           _IO(TEST_DRIVER_MAGIC, 0)
    #define IOC_TEST2           _IO(TEST_DRIVER_MAGIC, 1)

    #endif

``test-driver.c``

.. code-block:: c

    #include <linux/module.h>
    #include <linux/kernel.h>
    #include <linux/fs.h>
    #include <linux/cdev.h>
    #include <linux/delay.h>
    #include "test-driver.h"

    MODULE_LICENSE("GPL");
    MODULE_AUTHOR("Kaan Aslan");
    MODULE_DESCRIPTION("test-driver");

    static int test_driver_open(struct inode *inodep, struct file *filp);
    static int test_driver_release(struct inode *inodep, struct file *filp);
    static ssize_t test_driver_read(struct file *filp, char *buf, size_t size, loff_t *off);
    static ssize_t test_driver_write(struct file *filp, const char *buf, size_t size, loff_t *off);
    static long test_driver_ioctl(struct file *filp, unsigned int cmd, unsigned long arg);

    static long ioctl_test1(struct file *filp, unsigned long arg);
    static long ioctl_test2(struct file *filp, unsigned long arg);

    static dev_t g_dev;
    static struct cdev g_cdev;
    static struct file_operations g_fops = {
        .owner = THIS_MODULE,
        .open = test_driver_open,
        .read = test_driver_read,
        .write = test_driver_write,
        .release = test_driver_release,
        .unlocked_ioctl = test_driver_ioctl
    };

    static DEFINE_SEMAPHORE(g_sem, 1);

    static int __init test_driver_init(void)
    {
        int result;

        printk(KERN_INFO "test-driver module initialization...\n");

        if ((result = alloc_chrdev_region(&g_dev, 0, 1, "test-driver")) < 0) {
            printk(KERN_INFO "cannot alloc char driver!...\n");
            return result;
        }
        cdev_init(&g_cdev, &g_fops);
        if ((result = cdev_add(&g_cdev, g_dev, 1)) < 0) {
            unregister_chrdev_region(g_dev, 1);
            printk(KERN_ERR "cannot add device!...\n");
            return result;
        }

        return 0;
    }

    static void __exit test_driver_exit(void)
    {
        cdev_del(&g_cdev);
        unregister_chrdev_region(g_dev, 1);

        printk(KERN_INFO "test-driver module exit...\n");
    }

    static int test_driver_open(struct inode *inodep, struct file *filp)
    {
        return 0;
    }

    static int test_driver_release(struct inode *inodep, struct file *filp)
    {
        return 0;
    }

    static ssize_t test_driver_read(struct file *filp, char *buf, size_t size, loff_t *off)
    {
        return 0;
    }

    static ssize_t test_driver_write(struct file *filp, const char *buf, size_t size, loff_t *off)
    {
        return 0;
    }

    static long test_driver_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)
    {
        long result;

        switch (cmd) {
            case IOC_TEST1:
                result = ioctl_test1(filp, arg);
                break;
            case IOC_TEST2:
                result = ioctl_test2(filp, arg);
                break;
            default:
                result = -ENOTTY;
        }

        return result;
    }

    static long ioctl_test1(struct file *filp, unsigned long arg)
    {
        if (down_interruptible(&g_sem) != 0)
            return -ERESTARTSYS;

        printk(KERN_INFO "semaphore down and wait 30 seconds...\n");

        ssleep(30);

        up(&g_sem);

        printk(KERN_INFO "semaphore up...\n");

        return 0;
    }

    static long ioctl_test2(struct file *filp, unsigned long arg)
    {
        if (down_interruptible(&g_sem) != 0)
            return -ERESTARTSYS;

        printk(KERN_INFO "semaphore down...\n");

        up(&g_sem);

        printk(KERN_INFO "semaphore up...\n");

        return 0;
    }

    module_init(test_driver_init);
    module_exit(test_driver_exit);

Makefile
~~~~~~~~

.. code-block:: makefile

    obj-m += ${file}.o

    all:
    	make -C /lib/modules/$(shell uname -r)/build M=${PWD} modules
    clean:
    	make -C /lib/modules/$(shell uname -r)/build M=${PWD} clean

``load``

.. code-block:: bash

    #!/bin/bash

    module=$1
    mode=666

    /sbin/insmod ./${module}.ko ${@:2} || exit 1
    major=$(awk "\$2 == \"$module\" {print \$1}" /proc/devices)
    rm -f $module
    mknod -m $mode $module c $major 0

``unload``

.. code-block:: bash

    #!/bin/bash

    module=$1

    /sbin/rmmod ./${module}.ko || exit 1
    rm -f $module

``test-sync1.c``

.. code-block:: c

    #include <stdio.h>
    #include <stdlib.h>
    #include <fcntl.h>
    #include <unistd.h>
    #include <sys/ioctl.h>
    #include "test-driver.h"

    void exit_sys(const char *msg);

    int main(void)
    {
        int fd;

        if ((fd = open("test-driver", O_RDONLY)) == -1)
            exit_sys("open");

        if (ioctl(fd, IOC_TEST1) == -1)
            exit_sys("ioctl");

        close(fd);

        return 0;
    }

    void exit_sys(const char *msg)
    {
        perror(msg);
        exit(EXIT_FAILURE);
    }

``test-sync2.c``

.. code-block:: c

    #include <stdio.h>
    #include <stdlib.h>
    #include <fcntl.h>
    #include <unistd.h>
    #include <sys/ioctl.h>
    #include "test-driver.h"

    void exit_sys(const char *msg);

    int main(void)
    {
        int fd;

        if ((fd = open("test-driver", O_RDONLY)) == -1)
            exit_sys("open");

        if (ioctl(fd, IOC_TEST2) == -1)
            exit_sys("ioctl");

        close(fd);

        return 0;
    }

    void exit_sys(const char *msg)
    {
        perror(msg);
        exit(EXIT_FAILURE);
    }

Mutex ile Binary Semaphore Arasındaki Farklar
---------------------------------------------

Peki mutex nesneleriyle binary semaphore'lar arasında ne fark vardır? İki nesne arasındaki tipik farklılıklar
şunlardır:

1. Mutex nesnelerinin sahipliği thread temelinde alınmaktadır. Dolayısıyla mutex nesnelerini hangi thread
   kilitlemişse kilidini aynı thread açmak zorundadır. Halbuki semaphore'larda ``up`` işlemleri herhangi
   bir thread tarafından yapılabilmektedir. Bu da semaphore'ların *üretici-tüketici problemi
   (producer-consumer problem)* gibi klasik senkronizasyon kalıplarında kullanılabilmesini sağlamaktadır.

2. Linux çekirdeğinde semaphore nesneleri spin yapmamaktadır. Bir kez semaphore sayacına bakılmakta, eğer
   sayaç sıfırsa hemen thread bloke edilmektedir. Halbuki mutex nesnelerinde *optimistic spinning* işlemi
   yapılmaktadır. Yani "kilit belki açılır" diye bloke biraz ertelenmektedir.

3. Mutex nesnelerinin kilidi alındığında çekirdek yüksek öncelikli bloke olmuş thread'lerin önceliklerini
   biraz yükseltmektedir. Ancak semaphore nesnelerinde bu yapılmamaktadır.


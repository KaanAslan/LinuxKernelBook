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

    #define DEFINE_SEMAPHORE(_name, _n)     \
        struct semaphore _name = __SEMAPHORE_INITIALIZER(_name, _n)

Buradaki ``__SEMAPHORE_INITIALIZER`` makrosu da şöyle tanımlanmıştır:

.. code-block:: c

    #define __SEMAPHORE_INITIALIZER(name, n)                        \
    {                                                               \
        .lock       = __RAW_SPIN_LOCK_UNLOCKED((name).lock),        \
        .count      = n,                                            \
        .wait_list  = LIST_HEAD_INIT((name).wait_list)              \
        __LAST_HOLDER_SEMAPHORE_INITIALIZER                         \
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

Spinlock Nesneleri
==================

Linux çekirdeklerinde belki de en yoğun kullanılan senkronizasyon nesneleri *spinlock* denilen nesnedir.
Spinlock nesneleri hiçbir zaman blokeye yol açmamaktadır. Bu nesnelerde lock yapılmak istendiğinde eğer
kilit başka bir akış tarafından zaten alınmışsa bir döngü içerisinde sürekli "acaba kilit açıldı mı?" diye
kilide bakılmaktadır. Spinlock nesnelerinin *meşgul döngü (busy loop)* oluşturduğuna dikkat ediniz. İlk
bakışta bu nesnelerin kullanılmasının önemli bir CPU zamanının harcanmasına yol açacağını düşünebilirsiniz.
Ancak bu nesneler çekirdek tasarımcıları tarafından zaten "çok uzun süre beklenmeyecek durumlarda"
kullanılmaktadır. Bu nesnelerin yanlış yerlerde kullanılması çekirdeğin çökmesine ve *deadlock* oluşumuna
yol açabilmektedir.

Spin işlemine duyulan gereksinim açıktır. Thread'in uykuya yatırılması ve uyandırılması belli bir zaman
kaybına yol açmaktadır. Spinlock nesneleri bu zaman kaybını elimine etmek için düşünülmüştür. Spinlock
nesneleri "doğru yerde kullanılması koşuluyla" çok önemli ve faydalı nesnelerdir. Çekirdeğin her yerinde
birkaç satırlık kritik kodları oluşturmak için spinlock kullanımıyla karşılaşabilirsiniz.

Spinlock nesnelerinde kilit alındığında aynı zamanda ilgili işlemcide ya da çekirdekte thread'ler arası geçiş
(context switch) kapatılmaktadır. Böylece kilit bırakılana kadar kodun kesilmemesi garanti edilmiş olur.
(Tabii birden çok CPU ya da çekirdek söz konusu olduğunda yalnızca ilgili CPU'daki ya da çekirdekteki
thread'ler arası geçiş kapatılmaktadır.) Eğer ilgili CPU ya da çekirdek thread'ler arası geçişe
kapatılmasaydı bu durumda başka bir thread işlemi kesebilir ve başka thread'ler aynı spinlock nesnesini
kilitlemeye çalıştığında tüm quantum süresi boyunca CPU'yu meşgul bırakabilirdi.

Spinlock nesneleri çok işlemcili ya da çok çekirdekli sistemlerde anlamlı nesnelerdir. Tek işlemcili ya
da tek çekirdekli sistemlerde spin yapmanın hiçbir anlamı yoktur. Örneğin tek işlemcili ya da tek
çekirdekli bir sistem söz konusu olsun. Bu sistemlerde hiçbir zaman zaten bir thread spinlock nesnesini
kilitli göremez. Çünkü spinlock'a girildiğinde zaten işlemci ya da çekirdek thread'ler arası geçişe
kapatılmaktadır. Spinlock ile korunan kritik kod bloğu da zaten hiç kesilmeden çalıştırılmaktadır. Bu
durumda her zaman zaten spinlock kilidini alan thread'in onu bırakacağı garanti edilmektedir. O halde
spinlock kullanımından asıl amaç başka bir işlemci ya da çekirdek kritik kod bloğuna girmişse o çıkana
kadar spin yapmaktır. Peki aşağıda açıklayacağımız çekirdek fonksiyonları hem tek işlemcili ya da tek
çekirdekli hem de çok işlemcili ya da çok çekirdekli sistemlerde çalıştığına göre, tek işlemcili ya da tek
çekirdekli sistemlerde spin işlemi nasıl devre dışı bırakılmaktadır? İşte çekirdek kodları bu durumda
``CONFIG_SMP`` konfigürasyon parametresine bakmaktadır. Sembolik kod olarak çok işlemcili ya da çok
çekirdekli sistemlerde spinlock fonksiyonları şu yapıdadır:

.. code-block:: c

    spin_lock(...)
    {
        disable_preemption();

        for (;;) {
            if (kilit açıldı mı)
                <kilidi al>
                break;
        }
    }

    spin_unlock(...)
    {
        <kilidi_serbest_bırak>

        enable_preemption();
    }

Oysa tek işlemcili ya da tek çekirdekli sistemlerde kilidin alınması şu hale gelmektedir:

.. code-block:: c

    spin_lock(...)
    {
        disable_preemption();
    }

    spin_unlock(...)
    {
        enable_preemption();
    }

Linux çekirdeğindeki spinlock işlemleri şöyle yürütülmektedir:

**1)** Spinlock nesnesi ``spinlock_t`` türü ile temsil edilmektedir. Spinlock nesnesi aşağıdaki gibi
tanımlanabilir:

.. code-block:: c

    static spinlock_t g_spinlock;

Güncel Linux çekirdeklerinde çok işlemcili ya da çok çekirdekli sistemlerde ``CONFIG_SMP``
konfigürasyon parametresi ``=y`` yapıldığı için ``spinlock_t`` yapısı şöyle bildirilmiştir:

.. code-block:: c

    typedef struct spinlock {
        struct rt_mutex_base    lock;
    #ifdef CONFIG_DEBUG_LOCK_ALLOC
        struct lockdep_map      dep_map;
    #endif
    } spinlock_t;

Tek işlemcili ya da tek çekirdekli sistemlerde (``CONFIG_SMP=n`` durumu) ise ``spinlock_t`` yapısı
yalnızca ``int`` eleman içerecek biçimdedir.

**2)** Spinlock nesnesine ilkdeğer ``DEFINE_SPINLOCK`` makrosuyla verilebilmektedir. Bu makro aynı zamanda yapı
nesnesini de tanımlar. Örneğin:

.. code-block:: c

    #include <linux/spinlock.h>

    static DEFINE_SPINLOCK(g_spinlock);

Buradaki ``DEFINE_SPINLOCK`` makrosu güncel çekirdeklerde şöyle tanımlanmıştır:

.. code-block:: c

    #define ___SPIN_LOCK_INITIALIZER(lockname)          \
    {                                                   \
        .raw_lock = __ARCH_SPIN_LOCK_UNLOCKED,          \
        SPIN_DEBUG_INIT(lockname)                       \
        SPIN_DEP_MAP_INIT(lockname) }

    #define __SPIN_LOCK_INITIALIZER(lockname)           \
        { { .rlock = ___SPIN_LOCK_INITIALIZER(lockname) } }

    #define __SPIN_LOCK_UNLOCKED(lockname)              \
        (spinlock_t) __SPIN_LOCK_INITIALIZER(lockname)

    #define DEFINE_SPINLOCK(x)  spinlock_t x = __SPIN_LOCK_UNLOCKED(x)

Tek işlemcili ya da tek çekirdekli sistemlerde (``CONFIG_SMP=n`` durumu) bu makro basit bir biçime
dönüşmektedir:

.. code-block:: c

    #define __SPIN_LOCK_UNLOCKED(lockname)  (spinlock_t) { 1 }
    #define DEFINE_SPINLOCK(x)  spinlock_t x = __SPIN_LOCK_UNLOCKED(x)

Spinlock nesnesine ``spin_lock_init`` makrosuyla da başlangıç değerleri verilebilmektedir. Güncel
çekirdeklerde bu makro şöyle bildirilmiştir:

.. code-block:: c

    #define spin_lock_init(_lock)                   \
    do {                                            \
        spinlock_check(_lock);                      \
        *(_lock) = __SPIN_LOCK_UNLOCKED(_lock);     \
    } while (0)

Makronun parametre olarak spinlock nesnesinin adresini aldığını görüyorsunuz. Örneğin:

.. code-block:: c

    static spinlock_t g_spinlock;
    /* ... */

    spin_lock_init(&g_spinlock);

**3)** Spinlock kilidini almak için aşağıdaki fonksiyonlar kullanılmaktadır:

.. code-block:: c

    #include <linux/spinlock.h>

    void spin_lock(spinlock_t *lock);
    void spin_lock_irq(spinlock_t *lock);
    void spin_lock_irqsave(spinlock_t *lock, unsigned long flags);
    void spin_lock_bh(spinlock_t *lock);

``spin_lock`` fonksiyonu klasik spin yapan fonksiyondur. Bu fonksiyon thread'ler arası geçişi (preemption
mekanizmasını) kapatır, ancak kesmeleri kapatmaz. Preemption işleminin kapatılması IRQ'ların (yani donanım
kesmelerinin) kapatıldığı anlamına gelmemektedir. İşte ``spin_lock_irq`` fonksiyonu o anda çalışılan
işlemcideki IRQ'ları da (yani donanım kesmelerini de) kapatarak kilidi almaktadır. Yani biz bu fonksiyonla
kilidi almışsak kilidi bırakana kadar donanım kesmeleri o işlemcide oluşmayacaktır. (Ancak diğer
işlemcilerde aynı IRQ oluşabilir ve kesme kodu aynı kilidi almaya çalışırsa spin işlemi yapılabilir.)
``spin_lock_irqsave`` fonksiyonu ise hem o anda çalışılan işlemcideki kesmeleri kapatır hem de işlemcinin
bayrak yazmacını da saklar. Aslında bu fonksiyonların bazıları makro olarak yazılmıştır. Örneğin
``spin_lock_irqsave`` aslında bir makrodur. Biz bu fonksiyonun ikinci parametresine nesne adresini geçmiyor
olsak da bu bir makro olduğu için ikinci parametrede verdiğimiz nesnenin içerisine IRQ durumları
yazılmaktadır. ``spin_lock_irqsave`` fonksiyonu ile IRQ durumunun ``flags`` değişkenine kaydedilmesinin
nedeni kilit bırakılırken IRQ durumunun kilit alınmadan önceki biçimde bırakılmasının sağlanması içindir.
(Örneğin ``spin_lock_irqsave`` fonksiyonundan önce zaten yerel kesmeler disable edilmişse kilidi bırakırken
yerel kesmelerin enable edilmemesi gerekir.) ``spin_lock_bh`` fonksiyonu ise yalnızca yazılım kesmelerini
kapatmaktadır.

**4)** Spinlock kilidini bırakmak için ``spin_unlock`` fonksiyonları kullanılmaktadır:

.. code-block:: c

    #include <linux/spinlock.h>

    void spin_unlock(spinlock_t *lock);
    void spin_unlock_irq(spinlock_t *lock);
    void spin_unlock_irqrestore(spinlock_t *lock, unsigned long flags);
    void spin_unlock_bh(spinlock_t *lock);

Lock fonksiyonlarının hepsinin birer unlock karşılığının olduğunu görüyorsunuz. Biz kilidi hangi lock
fonksiyonu ile almışsak o unlock fonksiyonu ile bırakmalıyız. Kritik kod bloğu ``spin_lock`` ile
``spin_unlock`` fonksiyonları arasında alınmalıdır. Örneğin:

.. code-block:: c

    spin_lock(&g_spinlock);
    ... 
    ...         <KRİTİK KOD BLOĞU> 
    ... 
    spin_unlock(&g_spinlock);

Ya da örneğin:

.. code-block:: c

    unsigned long irqstate;
    /* ... */

    spin_lock_irqsave(&g_spinlock, irqstate);
    ... 
    ...     <KRİTİK KOD BLOĞU> 
    ...
    spin_unlock_irqrestore(&g_spinlock, irqstate);

Yine kernel spinlock nesnelerinde de try'lı lock fonksiyonları bulunmaktadır:

.. code-block:: c

    #include <linux/spinlock.h>

    int spin_trylock(spinlock_t *lock);
    int spin_trylock_bh(spinlock_t *lock);

Bu fonksiyonlar eğer spinlock kilitliyse spin yapmazlar ve 0 ile geri dönerler. Eğer kilidi alırlarsa sıfır
dışı bir değerle geri dönerler. Böylece çekirdek programcısı eğer spinlock kilidi başka bir işlemci
tarafından alınmışsa başka işlemler yapabilmektedir.

simplefs Dosya Sisteminde Spinlock
----------------------------"------

Biz *simplefs* dosya sistemimizde kendi süper blok nesnemize yaptığımız *eşzamanlı (concurrent)* erişimlerde
kodumuz zarar görmesin diye spinlock nesnesi kullanmıştık. Çağırdığımız çekirdek fonksiyonları ise zaten
çekirdek nesnelerine erişirken kendi içlerinde spinlock nesnelerini kullanıyordu. Dolayısıyla bizim
simplefs dosya sisteminde yalnızca kendimize ilişkin nesneleri korumamız yetiyordu. Kodumuzun bu kısmını
anımsatmak istiyoruz:

.. code-block:: c

    static int simplefs_alloc_inode_num(struct super_block *sb)
    {
        struct simplefs_super_block *sfs_sb;
        struct simplefs_disk_super_block *sfs_sbd;
        int ino;

        /* ... */

        spin_lock(&sfs_sb->lock);

        if (sfs_sbd->free_inodes == 0) {
            spin_unlock(&sfs_sb->lock);
            return -ENOSPC;
        }

        ino = find_first_zero_bit(sfs_sb->inode_bitmap, sfs_sbd->inode_count);
        if (ino >= sfs_sbd->inode_count) {
            spin_unlock(&sfs_sb->lock);
            return -ENOSPC;
        }

        set_bit(ino, sfs_sb->inode_bitmap);
        sfs_sbd->free_inodes--;
        mark_buffer_dirty(sfs_sb->inode_bitmap_bh);
        mark_buffer_dirty(sfs_sb->sb_bh);

        spin_unlock(&sfs_sb->lock);

        /* ... */

        return ino;
    }

Spinlock nesnesini bir fonksiyon içerisinde kilitlediyseniz fonksiyondan geri dönmeden önce onun kilidini
açmayı unutmayınız. Yukarıdaki fonksiyonda da fonksiyondan çıkmadan önce spinlock kilidinin açıldığına
dikkat ediniz.

Spinlock ile Mutex Nesnelerinin Karşılaştırılması
----------------------------------------------------

Spinlock nesnelerinin "kısa sürecek kritik kodlar için" kullanılması uygundur. Aksi takdirde diğer işlemci
ya da çekirdekteki kilidi bekleyen thread'ler meşgul döngüde spin yaparak uzun süre beklerler; bu da
gereksiz CPU zamanının harcanmasına yol açar. Spinlock kilidi alındıktan sonra akışın bloke olmadan hızlı
bir biçimde kilidi geri bırakması gerekir. Spinlock kilidi alındıktan sonra bloke oluşması pek çok soruna
yol açabilmektedir. IRQ bağlamında (yani IRQ kesme kodları içerisinde) ``mutex`` gibi ``semaphore`` gibi
blokeye yol açabilecek senkronizasyon nesneleri kullanılmamalıdır. Bu tür durumlarda spinlock
kullanılmalıdır. Aşağıdaki tabloda spinlock kullanımı ile mutex kullanımı çeşitli bakımlardan
karşılaştırılmıştır.

.. image:: _static/spinlock-mutex-comparison.png
   :alt: Spinlock ile Mutex Karşılaştırması
   :align: center

Okuma Yazma Kilitleri (Readers-Writer Lock)
============================================

Diğer çok kullanılan senkronizasyon nesnelerinden biri de *okuma yazma kilitleri (readers-writer lock)*
denilen nesnelerdir. Önce bu nesnelere neden gereksinim duyulduğunu bir örnekle açıklamak istiyoruz.
Çekirdek kodlarında paylaşılan bir kaynak bulunuyor olsun. Örneğin bunun global bir bağlı liste (linked
list) olduğunu düşünelim. Bu bağlı listeye bir grup thread eleman (düğüm) ekliyor olsun, bir grup thread
de bu bağlı listeyi dolaşarak eleman arıyor olsun. Burada bağlı listede arama yapmak *okuma (read)*
işlemi gibi düşünülebilir. Çünkü bu işlem paylaşılan kaynakta (burada bağlı liste) bir durum değişikliğine
yol açmadığı için farklı thread'lerden aynı anda yürütülebilmektedir. Ancak bağlı listeye eleman ekleyen
thread bu işlem sırasında bağlı listenin düğümlerini değiştirdiği için tam o sırada başka bir thread de
aynı bağlı listeye ekleme yaparsa ya da ondan arama yaparsa bu durum çökmeye yol açabilir. Burada bağlı
listeye eleman ekleme bir *yazma (write)* işlemi olarak ele alınabilir. O halde bizim öyle bir kritik kod
bloğu oluşturmamız gerekir ki birden fazla okuma yapan thread bu kritik kod bloğuna bekleme yapmadan
girebilsin ancak bir thread okuma yaparken yazma yapan bir thread okuma yapan thread kritik kod bloğundan
çıkana kadar beklesin. Benzer biçimde eğer yazma yapan bir thread kritik kod bloğuna girmişse bu işlem
bitene kadar okuma yapan bir thread de kritik kod bloğuna giremesin. Aşağıda Thread-1 kritik kod bloğuna
girmişse Thread-2'nin kritik kod bloğuna girip girmeyeceği bir tablo biçiminde verilmiştir:

.. image:: _static/rwlock-access-table.png
   :alt: Okuma Yazma Kilidi Erişim Tablosu
   :align: center
   :width: 60%

Görüldüğü gibi bu mekanizma yalnızca eş zamanlı okumalar için kritik kod bloğuna girilmesine izin
vermektedir.

Böyle bir mekanizma tek başına mutex ya da semaphore nesneleriyle sağlanamaz. Aşağıdaki temsili koda
(pseudo code) dikkat ediniz:

.. code-block:: c

    static DEFINE_MUTEX(g_mutex);

    read()
    {
        mutex_lock(&g_mutex);
        /* okuma işlemi yapılıyor */
        mutex_unlock(&g_mutex);
    }

    write()
    {
        mutex_lock(&g_mutex);
        /* yazma işlemi yapılıyor */
        mutex_unlock(&g_mutex);
    }

Burada birden fazla okuma işlemi de blokeye yol açacaktır. Halbuki bizim istediğimiz birden fazla okumanın
kilide yakalanmadan yapılabilmesidir.

Linux çekirdeğinde readers/writer lock nesneleri spinlock mekanizmasıyla çalışmaktadır. Yani bu nesneler
thread'i bloke ederek uykuya yatırmazlar. Thread'ler arası geçişi (preemption) kapatarak meşgul bir
döngüde kilidin açılmasını beklerler. Yine bu nesnelerin de tek işlemcili ya da tek çekirdekli sistemlerde
bir kullanımı yoktur. Bu sistemlerde bu kilit fonksiyonları yalnızca thread'ler arası geçişi kapatıp
açmaktadır. (Yani kritik kod bloğunun kesilmeden çalıştırılmasını sağlamaktadır.)

Okuma yazma kilitleri ``rwlock_t`` türünden bir yapıyla temsil edilmektedir. Bu yapı güncel çekirdeklerde
şöyle bildirilmiştir:

.. code-block:: c

    typedef struct {
        struct rwbase_rt    rwbase;
        atomic_t            readers;
    #ifdef CONFIG_DEBUG_LOCK_ALLOC
        struct lockdep_map  dep_map;
    #endif
    } rwlock_t;

Okuma yazma kilit nesnelerinin yaratılması ``DEFINE_RWLOCK`` makrosuyla ya da ``rwlock_init`` fonksiyonuyla
yapılmaktadır. ``DEFINE_RWLOCK`` makrosu ``include/linux/rwlock_types.h`` dosyası içerisinde aşağıdaki
gibi bildirilmiştir:

.. code-block:: c

    #ifdef CONFIG_DEBUG_SPINLOCK
    #define __RW_LOCK_UNLOCKED(lockname)                            \
        (rwlock_t) {    .raw_lock = __ARCH_RW_LOCK_UNLOCKED,        \
                        .magic = RWLOCK_MAGIC,                      \
                        .owner = SPINLOCK_OWNER_INIT,               \
                        .owner_cpu = -1,                            \
                        RW_DEP_MAP_INIT(lockname) }
    #else
    #define __RW_LOCK_UNLOCKED(lockname)                            \
        (rwlock_t) {    .raw_lock = __ARCH_RW_LOCK_UNLOCKED,        \
                        RW_DEP_MAP_INIT(lockname) }
    #endif

    #define DEFINE_RWLOCK(x)    rwlock_t x = __RW_LOCK_UNLOCKED(x)

``rwlock_init`` fonksiyonunun parametrik yapısı da şöyledir:

.. code-block:: c

    #include <linux/rwlock.h>

    void rwlock_init(rwlock_t *lock);

Okuma yazma kilitlerinin kilidini alan ve kilidini bırakan fonksiyonlar şunlardır:

.. code-block:: c

    void read_lock(rwlock_t *lock);
    void read_lock_irq(rwlock_t *lock);
    void read_lock_irqsave(rwlock_t *lock, unsigned long flags);
    void read_lock_bh(rwlock_t *lock);

    void read_unlock(rwlock_t *lock);
    void read_unlock_irq(rwlock_t *lock);
    void read_unlock_irqrestore(rwlock_t *lock, unsigned long flags);
    void read_unlock_bh(rwlock_t *lock);

    void write_lock(rwlock_t *lock);
    void write_lock_irq(rwlock_t *lock);
    void write_lock_irqsave(rwlock_t *lock, unsigned long flags);
    void write_lock_bh(rwlock_t *lock);
    int  write_trylock(rwlock_t *lock);

    void write_unlock(rwlock_t *lock);
    void write_unlock_irq(rwlock_t *lock);
    void write_unlock_irqrestore(rwlock_t *lock, unsigned long flags);
    void write_unlock_bh(rwlock_t *lock);

Nesne ``read_lock`` fonksiyonlarıyla kilitlenmişse nesnenin açılması ``read_unlock`` fonksiyonlarıyla,
nesne ``write_lock`` fonksiyonlarıyla kilitlenmişse nesnenin açılması ``write_unlock`` fonksiyonlarıyla
yapılmalıdır. Örneğin okuma amaçlı kritik kod şöyle oluşturulabilir:

.. code-block:: c

    static DEFINE_RWLOCK(g_rwlock);
    /* ... */

    read_lock(&g_rwlock);
    ... 
    ...         <KRİTİK KOD BLOĞU> 
    ...
    read_unlock(&g_rwlock);

Yazma amaçlı kritik kod bloğu da şöyle oluşturulabilir:

.. code-block:: c

    write_lock(&g_rwlock);
    ...
    ...         <KRİTİK KOD BLOĞU> 
    ... 
    write_unlock(&g_rwlock);

Örneğin biz bu fonksiyonlarla okuma yazma işlemlerini aşağıdaki gibi senkronize edebiliriz:

.. code-block:: c

    static DEFINE_RWLOCK(g_rwlock);

    read()
    {
        read_lock(&g_rwlock);
        /* okuma işlemi yapılıyor */
        read_unlock(&g_rwlock);
    }

    write()
    {
        write_lock(&g_rwlock);
        /* yazma işlemi yapılıyor */
        write_unlock(&g_rwlock);
    }

Burada artık okuma yapmak isteyen thread ``read_lock`` fonksiyonu ile spinlock kilidini aldığında başka bir
thread bu kilidi ``write_lock`` ile alamaz ve spin yapmaya başlar. Ancak başka bir thread kilidi yine
``read_lock`` ile alabilir. Eğer bir thread kilidi ``write_lock`` ile almışsa başka bir thread kilidi
``read_lock`` ile de ``write_lock`` ile de alamaz ve spin yaparak bekler.

``read_lock`` ve ``write_lock`` fonksiyonlarının irq sonekli versiyonları spinlock konusunda belirttiğimiz
gibi akış kritik koda girdiğinde ilgili işlemci ya da çekirdeğin yerel kesmelerini kapatmaktadır. irqsave
sonekli fonksiyonlar yine önce IRQ durumunu ``flags`` değişkeninde saklayıp unlock işlemi sırasında IRQ
durumunu önceki duruma set etmektedir.

SMP ve NUMA Mimarileri
======================

Biz Linux çekirdeğindeki temel senkronizasyon nesnelerini tanıttık. Ancak çekirdek senkronizasyon
mekanizmasının özellikle çok işlemcili ya da çok çekirdekli sistemler söz konusu olduğunda pek çok
ayrıntısı da vardır. Burada bu ayrıntılar üzerinde duracağız.

Bugün çok işlemcili ya da çok çekirdekli sistemlerde işlemci ile bellek arasındaki bağlantı söz konusu
olduğunda iki mimari kullanılmaktadır: *SMP (Symmetric Multiprocessor) Mimarisi* ve *NUMA (Non-Unified
Memory Access) Mimarisi*.

SMP Mimarisi
------------

SMP mimarisinde tüm işlemci ya da çekirdekler aynı fiziksel RAM'e bağlıdır. Dolayısıyla bir işlemci ya da
çekirdek RAM'e erişirken diğeri o erişim bitene kadar beklemektedir. Tabii bu senkronizasyon donanım
tarafından sağlanmaktadır. SMP mimarisindeki RAM erişimini aşağıdaki şekille betimleyebiliriz:

.. image:: _static/smp-architecture.png
   :alt: SMP Mimarisi
   :align: center
   :width: 60%

SMP sisteminde bir CPU ya da çekirdek DRAM belleğe eriştiği zaman diğeri nano saniyeler mertebesinde
beklediği için tam bir paralel çalışma mümkün olamamaktadır. Tabii işlemcilerin ya da çekirdeklerin içsel
önbellekleri DRAM erişimini azaltmayı hedeflemektedir. Ancak işlemci içerisindeki önbellek mekanizmasının
da *önbellek tutarlılığı (cache coherency)* denilen sorunları vardır. Örneğin bir işlemci ya da çekirdek
DRAM bellekten belli bir yeri içsel önbelleğine çekmiş olsun. Şimdi o işlemci ya da çekirdek oraya bir
şey yazdığında diğer işlemcilerin ya da çekirdeklerin onu fark etmesi gerekir. İşte bunu sağlamak
için *önbellek tutarlılığına* ilişkin bazı mekanizmalar işletilmektedir. Biz burada önbellek protokolleri
üzerinde durmayacağız. Bunlar hakkındaki bilgileri başka kaynaklardan edinebilirsiniz.

NUMA Mimarisi
-------------

NUMA mimarisinde DRAM bellek bank'lara ayrılmıştır. Her işlemcinin ya da çekirdeğin ayrı bir bank'ı
vardır. Bunlar kendi bank'larına diğer bank'lardan daha hızlı erişebilmektedir. Çünkü bunlar kendi
bank'larına erişirken diğer CPU ya da çekirdekleri durdurmamaktadır. Bu nedenle bu mimarilerde belleğin
her bölgesine erişim aynı sürede yapılamamaktadır. *Non-unified* sözcüğü bunu anlatmaktadır. Bu mimariyi
aşağıdaki şekille betimleyebiliriz:

.. image:: _static/numa-architecture.png
   :alt: NUMA Mimarisi
   :align: center
   :width: 60%

SMP ve NUMA Mimarilerinin Avantaj ve Dezavantajları
----------------------------------------------------

SMP mimarisinin de NUMA mimarisinin de bazı avantajları ve dezavantajları vardır. Ancak kişisel
bilgisayarlarımızda yaygın olarak SMP mimarisi kullanılmaktadır.

**NUMA Mimarisinin Avantajları:**

- Daha yüksek ölçeklenebilirlik sunar (64+ işlemciye kadar ölçeklenebilir).
- Yerel bellek (kendi bank'ına) erişimleri çok hızlıdır (düşük gecikme).
- Bellek bant genişliği toplamda daha yüksektir (her çekirdek kendi belleğine erişir).
- Büyük ve paylaşımlı bellek sistemleri için daha uygundur.
- Bellek kapasitesi daha kolay arttırılabilir (düğüm başına bellek eklenebilir).
- Performansı artırmak için veri yerelliği (data locality) optimizasyonu yapılabilir.

**NUMA Mimarisinin Dezavantajları:**

- Programlama tarafı ve yönetimi daha karmaşıktır.
- Uzak bellek erişimleri (diğer bank'lara erişim) yavaştır (yerelden 2-3 kat daha yavaş olabilir).
- İşletim sisteminin ve uygulamaların *NUMA-farkında (NUMA-aware)* olması gerekir.
- Yanlış veri yerleşimi performansı ciddi şekilde düşürebilir.
- Donanım maliyeti daha yüksektir.
- Önbellek tutarlılık (cache consistency) mekanizmaları daha karmaşıktır.

**SMP Mimarisinin Avantajları:**

- Programlama modeli çok daha basittir.
- Tüm işlemciler ya da çekirdekler için bellek erişim gecikmesi aynıdır (tutarlı performans).
- İşletim sistemlerinin ve uygulamaların geliştirilmesi daha kolaydır.
- Donanım tasarımı nispeten daha basittir.
- Küçük sistemlerde (2-8 işlemci) daha verimli olabilir.
- Önbellek tutarlılık mekanizması daha basittir.

**SMP Mimarisinin Dezavantajları:**

- Ölçeklenebilirlik sınırlıdır (genellikle 8 işlemciden sonra verim düşer).
- Bellek veri yolu (memory bus) darboğaz oluşturabilir.
- Tüm işlemciler ya da çekirdekler aynı veri yolunu paylaştığı için trafik sıkışabilir.
- Bellek bant genişliği sınırlıdır (paylaşılan veri yolu kapasitesiyle sınırlı).
- Büyük sistemlerde performans ölçeklemesi zayıftır.
- Yüksek işlemci sayılarında veri yolu çakışmaları artar.

**Kullanım Senaryoları**

- **SMP:** Küçük sunucular, iş istasyonları, gömülü sistemler.
- **NUMA:** Büyük veritabanı sunucuları, HPC sistemleri, bulut sunucuları.
- **SMP:** Daha az sayıda thread çalıştıran uygulamalar.
- **NUMA:** Yüzlerce thread çalıştıran paralel uygulamalar.
- **SMP:** Bellek erişim modelinin basit olması gereken durumlar.
- **NUMA:** Bellek kapasitesi ve bant genişliğinin kritik olduğu durumlar.

**Modern Eğilim**

- Günümüzde çok işlemcili büyük çapta sunucuların çoğu NUMA mimarisi kullanır.
- Modern işletim sistemleri (Linux, Windows) NUMA optimizasyonlarına sahiptir.
- Bulut bilişimde NUMA performans için kritiktir.
- Sanallaştırma ortamlarında NUMA yapılandırması önemli bir optimizasyon alanıdır.

Linux çekirdeği hem SMP hem de NUMA mimarisini destekleyecek biçimde gerçekleştirilmiştir. Yani biz SMP
içeren sistemlerde de NUMA içeren sistemlerde de Linux'u kurduğumuzda Linux bunu fark etmekte ve o
mimariye özgü çalışmayı desteklemektedir. Genel olarak Linux çekirdeği (konfigürasyona da bağlıdır) SMP
sistemlerini sanki tek düğümden oluşan NUMA sistemleri gibi ele almaktadır.

Çok İşlemcili Sistemlerde Senkronizasyon Sorunları
====================================================

Çok işlemcili ya da çok çekirdekli sistemlerde senkronizasyon bakımından iki önemli sorun kaynağı vardır:

1. Aynı bellek bölgesine erişimde oluşan sorunlar.
2. Komutların yer değiştirmesi (instruction reordering) nedeniyle oluşan sorunlar.

Aynı Bellek Bölgesine Erişimde Oluşan Sorunlar
----------------------------------------------

Birden fazla işlemci ya da çekirdeğin aynı global değişkeni tesadüfen aynı zamanda güncellemeye çalıştığını
düşünelim. Ya da bir işlemci ya da çekirdek o global değişkeni güncellerken diğerinin onu okumaya çalıştığını
düşünelim. Yukarıda biz modern sistemlerde bir işlemci ya da çekirdeğin belleğe erişirken zaten diğerlerini
durdurduğunu belirtmiştik. Ancak Intel gibi bazı mimarilerde bu durdurma bazı durumlarda tüm makine komutu
süresince yapılmamaktadır. Intel ve 64 bit ARM işlemcileri bazı koşullarda belleğe erişim yapan makine
komutunu çalışırken veri yolunu birden fazla kez tutup bırakabilmektedir. Örneğin 32 bit Intel işlemcilerinde
aslında işlemci fiziksel belleğe hep 32 bit genişliğinde erişmektedir. Bu işlemciler bellekten 1 byte bile
okuyacak olsalar aslında 4 byte okuyup o 4 byte içerisinden o byte'ı ayrıştırmaktadır. İşte bu işlemcilerde
eğer 4 byte'lık nesneler hizalanmamışsa makine komutunun başından sonuna kadar veri yolu tutulmamaktadır.
Aşağıdaki gibi bir bellek içeriğinde işlemcinin 4'ün katlarına hizalanmamış olan yyyy byte'larına tek bir
makine komutuyla yazmak istediğini varsayalım:

.. image:: _static/memory-misaligned.png
   :alt: Memory misaligned
   :align: center
   :width: 20%

İşte bu biçimdeki hizalı olmayan erişimlerde işlemci makine komutunun sonuna kadar veri yolunu tutarak
diğer işlemcileri durdurmamaktadır. Performans artışını sağlamak için işlemci önce ``xxyy`` satırını
yazmakta, o sırada veri yolunu bırakmakta, sonra diğer ``yyxx`` satırını yazmaktadır. İşte tam bu sırada
diğer işlemci ya da çekirdek araya girerse buradaki hizalanmamış nesne içindeki değeri yanlış
okuyabilmektedir. Intel işlemcileri bunu yalnızca hizalanmamış veriler üzerinde yapmaktadır. Burada
hizalama demekle *her nesnenin kendi uzunluğunun katlarında bulunması durumunu* kastediyoruz. Örneğin
1 byte bir bilginin okunup yazılmasında anlattığımız çalışma sisteminde hiçbir sorun oluşmayacaktır:

.. image:: _static/memory-aligned2.png
   :alt: Memory aligned2
   :align: center
   :width: 20%

Ya da aşağıdaki 2 byte'lık bilginin okunup yazılmasında da bir sorun oluşmayacaktır:

.. image:: _static/memory-aligned1.png
   :alt: Memory aligned1
   :align: center
   :width: 20%

Ancak aşağıdaki 2 byte'lık bilginin okunup yazılmasında bir sorun oluşabilecektir:

.. image:: _static/memory-aligned1.png
   :alt: Memory misaligned2
   :align: center
   :width: 20%

Çünkü 32 bit Intel işlemcileri bellek okumalarını 4'ün katlarından dörder byte'lık verileri çekerek
yapmaktadır. Benzer biçimde 64 bit Intel işlemcileri de 4'ün katları yerine 8'in katlarıyla okuma ve yazma
yapmaktadır. Tabii bildiğiniz gibi C/C++ derleyicileri zaten default ayarlarında hizalama uygulamaktadır. Bu nedenle
yukarıda bahsettiğimiz sorun genellikle ortaya çıkmayacaktır.

Intel gibi CISC tarzı işlemcilerde read-modify-write içeren makine komutları da vardır. Örneğin
``INC mem`` makine komutu önce bellekteki değeri CPU içerisine çeker, artırımı orada yapıp sonucu
belleğe geri yazar. Read-modify-write komutları birden fazla işlemci ya da çekirdeğin bulunduğu
sistemlerde diğer işlemci ya da çekirdekler bağlamında atomik değildir.

Peki Intel'de hizalanmamış olan ya da read-modify-write içeren 
makine komutlarında  sistem programcısının ne yapması gerekir? İşte Intel işlemcilerini tasarlayanlar komutların önüne getirilebilen 
1 byte'lık LOCK önek komutu bulundurmuşlardırhizalanmamış olan yukarıdaki
gibi durumlarda sistem programcısının ne yapması gerekir? İşte Intel işlemcilerini tasarlayanlar komutların
önüne getirilebilen 1 byte'lık ``LOCK`` önek komutu bulundurmuşlardır. Eğer erişim bu ``LOCK`` önekiyle
yapılırsa ilgili işlemci ya da çekirdek makine komutunun sonuna kadar veri yolunu (data bus) diğer
işlemciler ya da çekirdekler erişmesin diye tutmaktadır. Tabii C'de ve C++'ta biz makine komutlarını
doğrudan kullanamayız ancak sembolik makine dilinde yazılmış fonksiyonları çağırabiliriz ya da
derleyicilerin sunduğu *inline assembly* özelliği ile taşınabilir olmayan bir biçimde C/C++ kodları ile
makine kodlarını bir arada kullanabiliriz. Linux çekirdeğinde mümkün olduğunca gcc derleyicisinin
*inline assembly* özelliği kullanılmıştır.

32 bit ARM işlemcilerinde (ARM V7) zaten bellek erişimlerinin hizalanmış olması zorunludur. Aksi takdirde
işlemci exception oluşturmaktadır. Ancak daha sonra 64 bit ARM işlemcileri (ARM V8) de hizalanmamış
nesneler üzerinde exception oluşturmadan işlem yapabilir hale getirilmiştir. 64 bit ARM işlemcilerinde bu
durumu ortadan kaldırmak için Intel'in ``LOCK`` önekinin işlevinin bir bakıma benzerini yapan özel
``LDREX`` (load exclusive) ve ``STREX`` (store exclusive) makine komutları bulunmaktadır.
Ayrıca ARMV8 ile ARM'a da bazı read-modify-write komutları da eklenmiştir.

Atomik İşlemler
===============

Peki çok işlemcili ya da çok çekirdekli sistemlerde *atomik işlem* ne anlama gelmektedir? Bilindiği gibi
atomik işlem demek "kesilmeden, bölünmeden, yani araya başka bir unsur girmeden tek parça halinde yapılan
işlem" demektir. Şimdi şu soruyu soralım: Bir işlemci ya da çekirdekte çalışan makine komutları atomik
midir? İşte bu durum işlemcilerde çeşitli unsurlara bağlı olarak değişebilmektedir. Yukarıda da
belirttiğimiz gibi örneğin Intel ve ARM64 V8 işlemcilerinde hizalanmamış bellek bölgelerine yapılan
erişimler atomik değildir. Çünkü bu işlemler yapılırken araya başka bir işlemci ya da çekirdek girip
yapılan işlemi kararsız bir biçimde görebilmektedir. Çok işlemcili ya da çok çekirdekli sistemlerde
atomiklik "bir işlem bir CPU'da yapılırken diğer CPU'ların da bu işlemin yan etkisini ya tamamen görmeleri
ya da hiç görmemeleri" biçiminde tanımlanabilir. Peki yukarıdaki hizalanmamış bellek erişimleri dışında
makine komutları bu yaptığımız tanıma göre atomik midir? Evet istisnai başka birkaç durum dışında makine
komutları genel olarak atomiktir.

Yukarıda da belirttiğimiz gibi Intel gibi CISC işlemcilerinde doğrudan bellek üzerinde işlem yapan read-modfy-write makine 
komutları bulunmaktadır. Örneğin bu işlemcilerde aşağıdaki gibi tek bir makine komutuyla belli bir adresteki değer 1
artırılabilmektedir:

.. code-block:: nasm

    INC mem

Peki Intel ailesine ilişkin bir işlemcide bu işlem atomik midir? İşte bu tür işlemcilerde
*read-modify-write* biçiminde gerçekleştirilen işlemlerde ilgili bellek adresi hizalanmış olsa bile işlem
birden fazla işlemci ya da çekirdek söz konusu olduğunda atomik değildir. Biz atomikliği yukarıda "bir
işlemcinin ya da çekirdeğin yaptığı işlemi diğeri ya tam olarak görecek ya da görmeyecek" biçiminde
tanımlamıştık. Bu makine komutunu örneğin iki işlemci aynı zaman dilimi içerisinde yapmaya çalışırsa
birinin belleğe yazdığı artırılmış değer diğeri tarafından ezilebilmektedir. Bu durumda da bellekteki
değer iki kez değil sanki bir kez artırılmış gibi bir durum oluşabilmektedir. İşte bu tür durumlar
işlemcilerin makine komutu bitene kadar veri yolunu kilitlemesiyle ya da buna benzer bir mekanizmayla
engellenmektedir. Intel işlemcilerinde ``LOCK`` öneki bu işlemi yapmaktadır:

.. code-block:: nasm

    LOCK INC mem

Atomiklik ile komutların yer değiştirmesi (instruction reordering) kavramlarını birbirine karıştırmayınız.
Komutların yer değiştirmesinde komutlar yine atomik olabilir. Ancak diğer bir işlemci ya da çekirdek
bunları farklı sıralarda yapılmış gibi görebilmektedir.

Bizim C'de tek bir operatör ile gerçekleştirdiğimiz ifadeler atomik davranış bakımından hiçbir garanti
oluşturmamaktadır. Örneğin:

.. code-block:: c

    ++g_count;

Burada ``g_count`` değişkeni 1 artırılmıştır. Ancak bu işlem örneğin Intel x86 kodu üreten derleyiciler
tarafından tek bir makine komutuyla ``LOCK`` öneki getirilerek yapılmak zorunda değildir. RISC mimarisi
için kod üreten derleyicilerde ise bu tür işlemler zaten tek bir makine komutuyla yapılamamaktadır.
Örneğin Intel x86 derleyicileri yukarıdaki gibi C'de tek bir operatörden oluşan ifade için aşağıdaki gibi
üç makine komutu üretebilmektedir:

.. code-block:: nasm

    MOV reg, g_count
    INC reg
    MOV g_count, reg

Kaldı ki x86 kodu üreten bir derleyici bunun için tek bir makine komutu üretse bile komuta ``LOCK`` öneki
getirmedikten sonra yine birden fazla işlemci ya da çekirdeğin bulunduğu durumda atomiklik
sağlanamamaktadır:

.. code-block:: nasm

    INC count

Burada veri yolu ``LOCK`` önekiyle kilitlenmedikten sonra birden fazla işlemcinin bu komutu tesadüfen aynı
zaman diliminde çalıştırması sonucunda artırım değeri yanlış oluşabilecektir.

C'de Atomik Değişkenler
-----------------------

Aslında C'deki basit birtakım işlemler için derleyicinin atomik kod üretmesi çeşitli biçimlerde
sağlanabilmektedir. Örneğin C11 ile C'ye ``_Atomic(type)`` biçiminde tür belirleyicisi ve ``_Atomic``
biçiminde tür niteleyicisi eklenmiştir. Eğer bir değişken bu ``_Atomic(type)`` tür belirleyicisi ya da
``_Atomic`` tür niteleyicisi ile tanımlanırsa derleyici o değişkenle yapılan işlemlerin atomik yapılmasını
(örneğin ``LOCK`` önekleriyle yapılmasını) kendi sağlamaktadır. Örneğin:

.. code-block:: c

    _Atomic int g_count;

Yukarıda da belirttiğimiz gibi C11'de ``_Atomic`` tür niteleyicisinin yanı sıra ``_Atomic`` tür
belirleyicisi de bulunmaktadır. ``_Atomic`` tür belirleyicisi parantezli biçimde kullanılmaktadır.
Örneğin:

.. code-block:: c

    _Atomic(int) g_count;

C11 ile C'ye sokulan ``_Atomic`` niteleyicisi ve tür belirleyicisi *isteğe bağlı (optional)* bir
özelliktir. Derleyicilerin bunu desteklemesi zorunlu değildir. Derleyicinin bu özelliği destekleyip
desteklemediği derleme aşamasında ``__STDC_NO_ATOMICS__`` önceden tanımlanmış sembolik sabitiyle
belirlenebilmektedir.

Artık biz ``++g_count`` gibi bir işlemi yaptığımızda derleyici bunu yapacak atomik kodu kendisi
üretecektir. Ayrıca C11 ile eklenen ``<stdatomic.h>`` dosyasında aşağıdaki ``typedef`` bildirimleri de
bulunmaktadır:

.. code-block:: c

    typedef atomic_bool    _Atomic _Bool;
    typedef atomic_char    _Atomic char;
    typedef atomic_schar   _Atomic signed char;
    typedef atomic_uchar   _Atomic unsigned char;
    typedef atomic_short   _Atomic short;
    typedef atomic_ushort  _Atomic unsigned short;
    typedef atomic_int     _Atomic int;
    typedef atomic_uint    _Atomic unsigned int;
    typedef atomic_long    _Atomic long;
    typedef atomic_ulong   _Atomic unsigned long;
    typedef atomic_llong   _Atomic long long;
    typedef atomic_ullong  _Atomic unsigned long long;
    /* ... */

``_Atomic`` tür niteleyicisi Microsoft C derleyicileri tarafından desteklenmemektedir. C11 standartlarına
göre ``_Atomic`` niteleyicisi gerçek sayı türleriyle, göstericilerle ve yapı türleriyle de
kullanılabilmektedir. Ancak derleyici atomikliği tek bir makine komutuyla sağlayamadığı durumda kendi
içerisindeki senkronizasyon nesnelerini de kullanabilmektedir. Derleyiciler arasında bu konuda işlevsel
farklılıklar ve birtakım kusurlar bulunabilmektedir.

Ayrıca C11'den daha eski zamanlarda da C derleyicileri atomik işlemler için *built-in* (ya da *intrinsic*
de denilmektedir) fonksiyonlar bulunduruyordu. Örneğin atomik işlemler gcc tarafından sağlanan *built-in*
``__atomic_xxx`` önekli fonksiyonlar tarafından yapılabilmektedir. Microsoft derleyicileri de aynı amaçla
``InterlockedXXX`` fonksiyonlarını bulundurmaktadır.

C++'ta da ``<atomic>`` başlık dosyası içerisinde bildirilmiş olan ``atomic`` isimli sınıf şablonu ile
atomik işlemler yapılabilmektedir. Örneğin:

.. code-block:: cpp

    atomic<int> count;

Ancak Linux çekirdeği yukarıda bahsettiğimiz ``_Atomic`` tür niteleyicisini ve gcc derleyicilerinin
sağladığı *built-in* ``__atomic_xxx`` fonksiyonlarını kullanmamaktadır. Bunun en önemli nedeni çekirdeğin
derleyicinin versiyonundan ve yeteneğinden bağımsız biçimde pek çok platformu destekleyecek biçimde
yazılmak istenmesidir. Atomik işlemler çekirdek içerisindeki fonksiyonlarla gerçekleştirilmektedir.
Çekirdek geliştirmesi yapan ve aygıt sürücü yazan sistem programcıları da bu mekanizmayı kullanmalıdır.

Linux Çekirdeğinde Atomik İşlemler
----------------------------------

Linux çekirdeklerinde atomik işlemler ``atomic_t``, ``atomic64_t`` ve ``atomic_long_t`` isimli türler
kullanılarak yapılmaktadır. Bu türler birer yapı belirtir. Bu yapılar ``include/linux/types.h`` içerisinde
şöyle bildirilmiştir:

.. code-block:: c

    /* include/linux/types.h */

    typedef struct {
        int counter;
    } atomic_t;

    #ifdef CONFIG_64BIT
    typedef struct {
        s64 counter;
    } atomic64_t;
    #endif

    typedef struct {
        long counter;
    } atomic_long_t;

Yeni çekirdeklere ``atomic_long_t`` türü de eklenmiştir. `atomic_long_t`` türü ``include/linux/atomic/atomic_long.h`` 
dosyası içerisinde diğer türlerle ``typedef`` edilmiş durumdadır:

.. code-block:: c

    #ifdef CONFIG_64BIT
    typedef atomic64_t atomic_long_t;
    /* ... */
    #else
    typedef atomic_t atomic_long_t;
    /* ... */
    #endif

``atomic_t`` türündeki atomik değişken ``int`` türünden, ``atomic64_t`` türündeki atomik değişken ise
``long long`` türündendir. ``atomic_long_t`` türündeki atomik değişkenin türü de o sistemdeki ``long``
türünün uzunluğuna bağlı olarak değişebilmektedir. Bu türlerin neden yapılarla sarmalandığını merak
edebilirsiniz. Bunun en önemli nedeni atomik işlemler yapan çekirdek fonksiyonlarına yanlışlıkla başka
bir türün parametre olarak geçilmesinin engellenmek istenmesidir. Örneğin eğer ``atomic_t`` türü ``int``
olarak ``typedef`` edilseydi ``atomic_t`` türünden bir değişkene doğrudan ``int`` bir değer atanabilirdi.
Aynı zamanda bu atomik temsilin daha okunabilir olacağı düşünülmüştür. Örneğin:

.. code-block:: c

    atomic_t count;

    count++;                /* HATA: invalid operands to binary ++ */
    count = count + 1;      /* HATA: invalid operands to binary + */

Atomik türden bir nesneye pratik biçimde ilkdeğer vermek için makrolar bulundurulmuştur. Örneğin:

.. code-block:: c

    static atomic_t      my_counter          = ATOMIC_INIT(0);
    static atomic64_t    my_long_counter     = ATOMIC64_INIT(1000);
    static atomic_long_t my_platform_counter = ATOMIC_LONG_INIT(-1);

Bu makrolar aslında küme parantezleri oluşturup yapının ``counter`` elemanına değer atanmasını
sağlamaktadır. Örneğin ``ATOMIC_INIT`` makrosu şöyle bildirilmiştir:

.. code-block:: c

    #define ATOMIC_INIT(i)      { (i) }

Ancak yerel değişken söz konusu ise bu biçimde ilkdeğer verme atomikliği bozabilmektedir. Çünkü
derleyiciler yerel değişkenlere de makine komutlarıyla değer atamaktadır. Atomik değişkenlere daha sonra
değer atamak için ``atomic_set`` fonksiyonu kullanılmaktadır. Güncel çekirdeklerde ``atomic_set``
fonksiyonu inline biçimde şöyle bildirilmiştir:

.. code-block:: c

    static __always_inline void
    atomic_set(atomic_t *v, int i)
    {
        instrument_atomic_write(v, sizeof(*v));
        raw_atomic_set(v, i);
    }

Görüldüğü gibi fonksiyonun birinci parametresi ``atomic_t`` türünden nesnenin adresini, ikinci parametresi
ise buna atanacak değeri almaktadır. Buradaki asıl işlem platforma göre değişebilen ``raw_atomic_set``
tarafından yapılmaktadır. Fonksiyondaki ``instrument_atomic_write`` çağrısı çekirdek geliştirme süreci
için debug amaçlı bulunmaktadır. Normal olarak bu çağrı koddan çıkartılmaktadır. ``atomic64_t`` türü için
de ``atomic64_set`` isimli fonksiyon bulundurulmuştur:

.. code-block:: c

    static __always_inline void
    atomic64_set(atomic64_t *v, s64 i)
    {
        instrument_atomic_write(v, sizeof(*v));
        raw_atomic64_set(v, i);
    }

Benzer biçimde ``atomic_long_t`` türü için de ``atomic_long_set`` fonksiyonu bulundurulmuştur:

.. code-block:: c

    static __always_inline void
    atomic_long_set(atomic_long_t *v, long i)
    {
        instrument_atomic_write(v, sizeof(*v));
        raw_atomic_long_set(v, i);
    }

Şimdi ``atomic_set`` fonksiyonunun çağırdığı ``raw_atomic_set`` fonksiyonuna bakalım:

.. code-block:: c

    static __always_inline void
    raw_atomic_set(atomic_t *v, int i)
    {
        arch_atomic_set(v, i);
    }

Burada ``arch_atomic_set`` fonksiyonu işlemciye bağlı olarak değişebilecek asıl işlemi yapan
fonksiyondur. Derlemenin yapıldığı işlemci modeli neyse ``arch/<işlemci_türü>/include/asm/atomic.h``
içerisindeki ``arch_atomic_set`` fonksiyonu çağrılmaktadır. ``arch_atomic_set`` bazı mimariler için
makro olarak bazı mimariler için inline fonksiyon olarak yazılmıştır. Örneğin Intel x86 işlemcileri için
``arch/x86/include/asm/atomic.h`` içerisindeki bu fonksiyon şöyle yazılmıştır:

.. code-block:: c

    static __always_inline void arch_atomic_set(atomic_t *v, int i)
    {
        __WRITE_ONCE(v->counter, i);
    }

Buradaki ``__WRITE_ONCE`` makrosu ise şöyle yazılmıştır:

.. code-block:: c

    #define __WRITE_ONCE(x, val)                        \
    do {                                                \
        *(volatile typeof(x) *)&(x) = (val);            \
    } while (0)

Burada görüldüğü gibi erişim ``volatile`` olarak yapılmıştır. Yani yazma işleminin doğrudan bellek
erişimi ile yapılması istenmiştir. Yukarıdaki makroda aklınıza şu sorular gelebilir:

- Nesne hizalanmamışsa yukarıdaki atama işlemi atomik olur mu?
- ``volatile`` erişim, erişimin atomik yapılmasını garanti eder mi?

Nesne hizalanmamışsa yukarıdaki atama tek makine komutuyla yapılsa bile atomik olmaz. Ancak Linux
çekirdeğindeki tüm nesneler her zaman zaten hizalıdır. Yani bu garanti zaten vardır. Yukarıdaki
``volatile`` erişim için gcc'nin tek makine komutu üreteceği de bilinmektedir. gcc ``volatile`` atama
işlemlerini her zaman tek makine komutuyla yapmaktadır. Ayrıca yukarıdaki işlemde ileride ele alacağımız
bir bellek bariyerinin kullanılmadığına dikkatinizi çekmek istiyoruz. Bellek bariyerleri bir grup makine
komutunun sıralamasını garanti etmek için kullanılmaktadır. Atomiklik ise bir işlemin araya girilmeden,
kesilmeden tek parça bir işlem olarak yapılması anlamına gelmektedir.

Yukarıdaki akış Linux çekirdeğinde çok karşılaşılan bir kalıptır. İşlemler işlemci bağımsız fonksiyonlar
çağrılarak yapılır. Ancak belli bir aşamadan sonra işlemciye ilişkin ``arch`` dizini içerisindeki
fonksiyonlar ya da makrolar devreye girer. Bazen yalnızca bazı işlemciler için özel işlemlerin yapılması
söz konusu olabilmektedir. Bu durumda ilgili fonksiyonlar ya da makrolar o işlemciler için yazılır,
diğerleri için de *generic* bir tanımlama yapılır. Bu tür kodlarda isminde "generic" geçen dosyalar
görürseniz şaşırmayınız. Bunlar adeta "geri kalan işlemcilerin hepsi için" anlamına gelmektedir. Atomik
fonksiyonlardaki çağırma dizgesi tipik olarak şöyledir:

.. code-block:: none

    atomic_xxx ---> raw_atomic_xxx ---> arch_atomic_xxx (işlemciye özgü fonksiyon ya da makro)

Atomik Okuma ve Artırım Fonksiyonları
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Atomik türlerden atomik biçimde değer okumak için read fonksiyonları kullanılmaktadır:

.. code-block:: c

    int atomic_read(const atomic_t *v);
    s64 atomic64_read(const atomic64_t *v);
    long atomic_long_read(const atomic_long_t *v);

Tabii bu değer okuma işlemi de tek bir işlemle yani başka bir işlemcinin araya girmesi engellenerek
yapılmaktadır. ``atomic_read`` fonksiyonu şöyle yazılmıştır:

.. code-block:: c

    static __always_inline int
    atomic_read(const atomic_t *v)
    {
        instrument_atomic_read(v, sizeof(*v));
        return raw_atomic_read(v);
    }

Buradaki ``instrument_atomic_read`` fonksiyonu çekirdek geliştirmesi sırasında debug amaçlı
çağrılmaktadır. Normal çekirdek derlemelerinde bu çağrı koddan çıkartılmaktadır. ``raw_atomic_read``
fonksiyonu şöyle tanımlanmıştır:

.. code-block:: c

    static __always_inline int
    raw_atomic_read(const atomic_t *v)
    {
        return arch_atomic_read(v);
    }

``arch_atomic_read`` fonksiyonunun Intel x86 gerçekleştirimi şöyledir:

.. code-block:: c

    static __always_inline int arch_atomic_read(const atomic_t *v)
    {
        /*
         * Note for KASAN: we deliberately don't use READ_ONCE_NOCHECK() here,
         * it's non-inlined function that increases binary size and stack usage.
         */
        return __READ_ONCE((v)->counter);
    }

``__READ_ONCE`` makrosu da şöyle oluşturulmuştur:

.. code-block:: c

    #define __READ_ONCE(x)  (*(const volatile __unqual_scalar_typeof(x) *)&(x))

Burada değişkenin adresi alınarak bu adres ``volatile`` bir adrese dönüştürülmüş ve yukarıda
belirttiğimiz gibi ``volatile`` erişim yapılmıştır. Fonksiyonun kullanımına şöyle bir örnek
verebiliriz:

.. code-block:: c

    atomic_t g_counter = ATOMIC_INIT(100);
    /* ... */

    int value = atomic_read(&g_counter);    /* atomik okuma */

Atomik artırımlar ve eksiltimler için şu fonksiyonlar bulundurulmuştur:

.. code-block:: c

    void atomic_inc(atomic_t *v);       /* v++ */
    void atomic_dec(atomic_t *v);       /* v-- */

    void atomic64_inc(atomic64_t *v);
    void atomic64_dec(atomic64_t *v);

    void atomic_long_inc(atomic_long_t *v);
    void atomic_long_dec(atomic_long_t *v);

Bu fonksiyonlar artırımın atomik bir biçimde yapılmasını garanti etmektedir. Intel'de atomik bellek
artırımları ``LOCK`` öneki getirilmiş tek makine komutuyla yapılabilmektedir. Ancak 32 bitlik ARM gibi
RISC işlemcilerinde bu işlemler bir döngü içerisinde özel makine komutlarıyla yapılmaktadır.
``atomic_inc`` fonksiyonu güncel çekirdeklerde şöyle yazılmıştır:

.. code-block:: c

    static __always_inline void
    atomic_inc(atomic_t *v)
    {
        instrument_atomic_read_write(v, sizeof(*v));
        raw_atomic_inc(v);
    }

``raw_atomic_inc`` fonksiyonu da şöyle yazılmıştır:

.. code-block:: c

    static __always_inline void
    raw_atomic_inc(atomic_t *v)
    {
    #if defined(arch_atomic_inc)
        arch_atomic_inc(v);
    #else
        raw_atomic_add(1, v);
    #endif
    }

Her mimaride 1 artırma yapan makine komutu olmadığı için yukarıdaki kodda bir kontrolün yapıldığını
görüyorsunuz. ``raw_atomic_add`` fonksiyonu da şöyle yazılmıştır:

.. code-block:: c

    static __always_inline void
    raw_atomic_add(int i, atomic_t *v)
    {
        arch_atomic_add(i, v);
    }

Burada artık işlemciye özgü fonksiyon çağrılmıştır. Intel x86 mimarisi için bu fonksiyon şöyledir:

.. code-block:: c

    static __always_inline void arch_atomic_add(int i, atomic_t *v)
    {
        asm_inline volatile(LOCK_PREFIX "addl %1, %0"
                : "+m" (v->counter)
                : "ir" (i) : "memory");
    }

Makine komutunun önüne ``LOCK`` öneki getirilmiş olduğuna dikkat ediniz.

Artırma yapan atomik fonksiyonların artırılmış yeni değeri veren biçimleri de vardır:

.. code-block:: c

    int atomic_inc_return(atomic_t *v);
    int atomic_dec_return(atomic_t *v);

    s64 atomic64_inc_return(atomic64_t *v);
    s64 atomic64_dec_return(atomic64_t *v);

    long atomic_long_inc_return(atomic_long_t *v);
    long atomic_long_dec_return(atomic_long_t *v);

Örneğin çekirdek kodlarında ya da aygıt sürücülerde aşağıdaki gibi bir referans sayacı
oluşturulabilir:

.. code-block:: c

    struct my_object {
        atomic_t refcount;
        /* ... */
    };

    struct my_object *create_object(void)
    {
        struct my_object *obj;

        obj = kzalloc(sizeof(*obj), GFP_KERNEL);
        if (!obj)
            return NULL;

        atomic_set(&obj->refcount, 1);

        return obj;
    }

    void get_object(struct my_object *obj)
    {
        atomic_inc(&obj->refcount);
        /* ... */
    }

    void put_object(struct my_object *obj)
    {
        int new_count;

        if (atomic_dec_return(&obj->refcount) == 0) {
            /* kaynaklar boşaltılıyor */
        }
        /* ... */
    }

Bellekteki atomik nesneye değer eklemek ve onun içerisindeki değeri eksiltmek için de şu fonksiyonlar
bulundurulmuştur:

.. code-block:: c

    void atomic_add(int i, atomic_t *v);    /* v += i */
    void atomic_sub(int i, atomic_t *v);    /* v -= i */

    void atomic64_add(s64 a, atomic64_t *v);
    void atomic64_sub(s64 a, atomic64_t *v);

    void atomic_long_add(long i, atomic_long_t *v);
    void atomic_long_sub(long i, atomic_long_t *v);

Bunların artırılmış ya da eksiltilmiş değerle geri dönen biçimleri de vardır:

.. code-block:: c

    int atomic_add_return(int i, atomic_t *v);
    int atomic_sub_return(int i, atomic_t *v);

    s64 atomic64_add_return(s64 a, atomic64_t *v);
    s64 atomic64_sub_return(s64 a, atomic64_t *v);

    long atomic_long_add_return(long i, atomic_long_t *v);
    long atomic_long_sub_return(long i, atomic_long_t *v);

Artırım ve eksiltim işlemlerinde artırılmış ya da eksiltilmiş değerle değil de eski değerle geri dönen
fetch'li biçimleri de vardır:

.. code-block:: c

    int  atomic_fetch_add(int i, atomic_t *v);
    int  atomic_fetch_sub(int i, atomic_t *v);

    s64  atomic64_fetch_add(s64 i, atomic64_t *v);
    s64  atomic64_fetch_sub(s64 i, atomic64_t *v);

    long atomic_long_fetch_add(long i, atomic_long_t *v);
    long atomic_long_fetch_sub(long i, atomic_long_t *v);

Atomik işlemler için ``xchg`` fonksiyonları da bulunmaktadır:

.. code-block:: c

    int atomic_xchg(atomic_t *v, int new);
    s64 atomic64_xchg(atomic64_t *v, s64 new);
    long atomic_long_xchg(atomic_long_t *v, long new);

Bu fonksiyonlar *read-modify-write* denilen atama işlemini yapmaktadır. Yani bu fonksiyonlar atomik bir
biçimde bellekteki nesneye değer atayıp onun eski değerini geri döndürmektedir. ``atomic_xchg``
fonksiyonu şöyle yazılmıştır:

.. code-block:: c

    static __always_inline int
    atomic_xchg(atomic_t *v, int new)
    {
        kcsan_mb();
        instrument_atomic_read_write(v, sizeof(*v));
        return raw_atomic_xchg(v, new);
    }

``raw_atomic_xchg`` fonksiyonu da şöyle yazılmıştır:

.. code-block:: c

    static __always_inline int
    raw_atomic_xchg(atomic_t *v, int new)
    {
    #if defined(arch_atomic_xchg)
        return arch_atomic_xchg(v, new);
    #elif defined(arch_atomic_xchg_relaxed)
        int ret;
        __atomic_pre_full_fence();
        ret = arch_atomic_xchg_relaxed(v, new);
        __atomic_post_full_fence();
        return ret;
    #else
        return raw_xchg(&v->counter, new);
    #endif
    }

Buradaki ``arch_atomic_xchg`` fonksiyonu da Intel x86 işlemcileri için şöyle yazılmıştır:

.. code-block:: c

    static __always_inline int arch_atomic_xchg(atomic_t *v, int new)
    {
        return arch_xchg(&v->counter, new);
    }

Bundan sonra da Intel'deki ``XCHG`` makine komutu kullanılarak işlem yapılmıştır.

ARM gibi RISC işlemcilerinde atomik işlemlerin nasıl yapıldığını izleyen paragraflarda açıklayacağız.
``atomic_set`` fonksiyonlarının bir değer geri döndürmediğine, ``atomic_xchg`` fonksiyonlarının ise eski
değeri geri döndürdüğüne dikkat ediniz. Ayrıca ``atomic_xchg`` fonksiyonları işlemlerin başına ve sonuna
bellek bariyerleri de yerleştirmektedir. (Intel x86 işlemcilerinde ``XCHG`` makine komutu zaten atomiktir
yani ``LOCK`` uygulanmış gibidir. Dolayısıyla bu işlemcilerde bellek bariyerine gerek kalmamaktadır.)

Aslında çekirdekte atomik ``xchg`` fonksiyonunun dışında herhangi bir nesneye atomik değer atayan genel
bir ``xchg`` makrosu da bulundurulmuştur. Bu makronun birinci parametresi nesnenin bellek adresini,
ikinci parametresi ise ona aktarılacak değeri almaktadır. Makro atomik bir biçimde bu değeri nesneye
yerleştirirken onun önceki değerini de geri döndürmektedir:

.. code-block:: c

    #define xchg(ptr, new)  /* arch-specific */

Bu genel makro herhangi bir temel tamsayı türüyle çalışabilmektedir.

Compare-Exchange (Compare-And-Swap) Fonksiyonları
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Özellikle senkronizasyon nesnelerinin gerçekleştirilmesinde kullanılan, İngilizce genellikle
*compare-exchange* ya da *compare-and-swap (CAS)* biçiminde ifade edilen önemli bir mekanizma vardır.
İşlemciler bu mekanizmanın gerçekleştirilebilmesi için özel makine komutları bulundurmaktadır. Bu
mekanizma Linux çekirdeğinde atomik fonksiyonlar biçiminde oluşturulmuştur:

.. code-block:: c

    int atomic_cmpxchg(atomic_t *v, int old, int new);
    s64  atomic64_cmpxchg(atomic64_t *v, s64 old, s64 new);
    long atomic_long_cmpxchg(long *v, long old, long new);

Ayrıca çekirdekte genel bir ``cmpxchg`` makrosu da bulunmaktadır. Bu genel makro herhangi bir temel
tamsayı türüyle çalışabilmektedir:

.. code-block:: c

    #define cmpxchg(ptr, old, new)  /* ... */

*Compare-exchange* mekanizması şu işlemin yapılmasına yol açmaktadır: *Eğer bellekteki bir nesne
içerisinde bulunan değer benim belirttiğim değerle aynıysa o zaman onun yerine şu değeri yaz.* Tabii bu
işlem atomik bir biçimde yapılmaktadır. Örneğin bir nesne içerisinde 0 değeri bulunuyor olsun. Biz de bu
mekanizmayla şu işlemi atomik olarak yapabiliriz: *Eğer nesne içerisinde 0 varsa onu 1 yap.* Burada bir
koşulun yani karşılaştırmanın (compare) olduğuna dikkat ediniz. Bu örneğimizde nesne içerisinde 0 yoksa
işlem başarısız olacaktır, ancak 0 varsa başarılı olacaktır. Buradaki karşılaştırma ve atama atomik bir
biçimde yani tek bir işlemmiş gibi yapılmaktadır. *Compare-exchange* işleminin mantıksal temsili şöyle
ifade edilebilir:

.. code-block:: c

    int cmpxchg(int *ptr, int old_val, int new_val)     /* dikkat: bu temsili bir koddur */
    {
        int current = *ptr;

        if (current == old_val)
            *ptr = new_val;     /* Eşitse güncelle */

        return current;         /* Eski değeri döndür */
    }

Tabii tüm işlem aslında tek bir makine komutuyla kesilmeden yapılmaktadır. Fonksiyonların hedeflenen
nesnenin önceki değeriyle geri döndüğüne dikkat ediniz.

*Compare-exchange* mekanizması senkronizasyon nesnelerinin gerçekleştiriminde kullanılan bir mekanizmadır.
Örneğin manuel bir spinlock gerçekleştirimi yapacak olalım:

.. code-block:: c

    static atomic_t g_flag = ATOMIC_INIT(0);
    /* ... */

    preempt_disable();

    while (atomic_read(&g_flag) == 1)
        ;
    atomic_set(&g_flag, 1);
    ... 
    ...         <KRİTİK KOD BLOĞU> 
    ...
    atomic_set(&g_flag, 0);

    preempt_enable();

Buradaki sorun ``g_flag`` değişkeni 0 ise onun 1 yapılması sırasında başka bir işlemcideki kodun açık
pencere bularak kritik kod bloğuna girebilmesidir:

.. code-block:: c

    while (atomic_read(&g_flag) == 1)
        ;

    /* ---> DİKKAT: BURADA AÇIK BİR PENCERE VAR! */

    atomic_set(&g_flag, 1);

İşte *compare-exchange* mekanizması bu pencerenin oluşumunu engellemektedir. Çünkü bu mekanizma atomik
yürütülmektedir:

.. code-block:: c

    preempt_disable();

    while (atomic_cmpxchg(&g_flag, 0, 1) != 0)
        ;
    ...
    ...         <KRİTİK KOD BLOĞU>
    ... 
    atomic_set(&g_flag, 0);

    preempt_enable();

Yukarıdaki döngüye dikkat ediniz. ``cmpxchg`` fonksiyonları nesnenin önceki değeriyle geri dönmektedir.
Buradaki spinlock gerçekleştirimini gerçeğine biraz daha benzetebiliriz:

.. code-block:: c

    typedef struct {
        atomic_t lock;
    } spinlock_t;

    #define SPINLOCK_INIT   {.lock = ATOMIC_INIT(0)}

    static inline void spin_lock_init(spinlock_t *lock)
    {
        atomic_set(&lock->lock, 0);
    }

    static inline void spin_lock(spinlock_t *lock)
    {
        preempt_disable();
        while (atomic_cmpxchg(&lock->lock, 0, 1) != 0) {
            cpu_relax();
        }
        smp_mb();
    }

    static inline void spin_unlock(spinlock_t *lock)
    {
        smp_mb();
        atomic_set(&lock->lock, 0);
        preempt_enable();
    }

    static inline int spin_trylock(spinlock_t *lock)
    {
        preempt_disable();
        if (atomic_cmpxchg(&lock->lock, 0, 1) == 0) {
            smp_mb();
            return 1;
        }
        preempt_enable();

        return 0;
    }

Bu gerçekleştirim biraz daha gerçeğe uygundur. ``smp_mb`` bariyer fonksiyonunu izleyen paragraflarda ele
alacağız. ``cpu_relax`` işlemi CPU'da bir duraklama yaratmaktadır. Bu sürekli dönme durumlarında CPU'nun
güç tüketimini azaltıcı bir etki yaratmaktadır. Intel x86 mimarisinde bu fonksiyon ``PAUSE`` makine
komutunu, ARM işlemcilerinde ise ``YIELD`` makine komutunu oluşturmaktadır. Eski sistemlerde ``NOP``
komutları da benzer etkileri yaratabilmektedir.

Peki *compare-exchange* biçiminde bir mekanizma olmasaydı ne olurdu? İşte bu tür durumlarda çok
işlemcili ya da çok çekirdekli sistemlerdeki senkronizasyon nesnelerinin gerçekleştirilmesi mümkün
olmazdı. *Compare-exchange* işlemleri işlemcilerdeki özel makine komutlarıyla gerçekleştirilmektedir.
Bu makine komutlarına sahip olmayan işlemcilerde bu mekanizma oluşturulamamaktadır.

Biz kitabımızda *compare-exchange* yerine *compare-and-swap* terimini ya da doğrudan CAS kısaltmasını da
kullanacağız.

Koşullu Atomik İşlemler
~~~~~~~~~~~~~~~~~~~~~~~

Linux çekirdeğinde bir koşula bağlı olarak atomik artırma ve eksiltme gibi işlemleri yapan atomik
fonksiyonlar da vardır. ``atomic_add_unless`` fonksiyonu bir koşul sağlamadığında artırma yapmaktadır.
Fonksiyonun parametrik yapısı şöyledir:

.. code-block:: c

    bool atomic_add_unless(atomic_t *v, int a, int u);

Bu fonksiyon ``v`` içerisindeki değer ``u``'ya eşit değilse ``v`` içerisindeki değeri ``a`` kadar
artırmaktadır. Fonksiyonun yaptığı işin temsili (pseudo) kodu şöyledir:

.. code-block:: c

    if (atomic_read(v) != u) {
        atomic_add(a, v);
        return 1;           /* Başarılı */
    }
    return 0;               /* Değer u idi, ekleme yapılmadı */

Tabii yukarıdaki kod yalnızca temsili bir koddur. Yukarıdaki işlemler başka bir işlemci araya girmeden
atomik bir biçimde yapılmaktadır.

Örneğin çekirdek içerisinde belli bir sayaç belli bir değerden daha fazla artırılamayacak olsun. Bu işlem
``atomic_add_unless`` fonksiyonu ile kolay bir biçimde yapılabilir:

.. code-block:: c

    #define MAX_CONNECTIONS     1000

    static atomic_t connection_count = ATOMIC_INIT(0);

    int try_new_connection(void)
    {
        /* 1000'e ulaşmadıysa artır */
        if (!atomic_add_unless(&connection_count, 1, MAX_CONNECTIONS)) {
            printk(KERN_WARNING "Max connections reached!\n");
            return -EBUSY;
        }

        return 0;
    }

Burada görüldüğü gibi sayaç değeri 1000 değilse 1 artırılmaktadır. Eğer sayaç değeri 1000'e gelmişse
artırım yapılmamakta ve fonksiyon 0 değeri ile geri dönmektedir. Bu fonksiyonun koşullu biçimde 1
artıran biçimi de vardır:

.. code-block:: c

    bool atomic_inc_not_zero(atomic_t *v);

Bu fonksiyonun temsili (pseudo) kodu da şöyledir:

.. code-block:: c

    if (atomic_read(v) != 0) {
        atomic_inc(v);
        return 1;       /* Başarılı */
    }
    return 0;           /* Değer 0 idi, artırma yapılmadı */

Test-And-Set Atomik İşlemleri
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Çekirdekte atomik türlerle *test-and-set* işlemlerini yapan bir grup fonksiyon da bulunmaktadır. Bu
işlemler de yine işlemcilerin bulundurduğu özel makine komutlarıyla yapılabilmektedir:

.. code-block:: c

    int atomic_dec_and_test(atomic_t *v);
    int atomic_inc_and_test(atomic_t *v);
    int atomic_sub_and_test(int i, atomic_t *v);
    int atomic_add_negative(int i, atomic_t *v);

``atomic_dec_and_test`` fonksiyonu atomik değişkendeki değeri 1 eksiltir ve sonucun 0 olup olmadığına
bakar. Eğer değer 0 olmuşsa 1, olmamışsa 0 geri döndürmektedir. ``atomic_inc_and_test`` fonksiyonu ise
atomik değişkendeki değeri 1 artırır, eğer artırılmış değer sıfırsa 1, sıfır değilse 0 geri döndürür.
Bu fonksiyon negatif değerden sıfıra geçişi tespit etmek için kullanılmaktadır. ``atomic_sub_and_test``
değişkendeki değeri belli miktarda eksiltip sonucun 0 olup olmadığına bakmaktadır. Eğer eksiltilmiş
değer 0 ise fonksiyon 1 değerine, değilse 0 değerine geri dönmektedir. ``atomic_add_negative``
fonksiyonu ise atomik değişkene belli bir değeri ekleyip sonucun hâlâ negatif olup olmadığına
bakmaktadır. Eğer sonuç negatifse fonksiyon 1 değerine, negatif değilse 0 değerine geri dönmektedir.

Atomik Bit İşlemleri
~~~~~~~~~~~~~~~~~~~~

Linux çekirdeklerinde atomik bir biçimde bir nesnenin bitleri üzerinde işlem yapan fonksiyonlar da
bulundurulmuştur. Bu fonksiyonlar ilgili işlemcideki özel makine komutlarını kullanmaktadır. Bu işlemler
*read-modify-write* biçimindedir. Intel işlemcilerinin bellek üzerinde doğrudan bit işlemlerini yapan
makine komutlarına sahip olduğunu anımsayınız. Intel işlemcilerinde bu makine komutlarının başına ``LOCK``
öneki getirilmesi yeterli olmaktadır. Ancak ARM gibi RISC işlemcilerinde bu tür işlemler izleyen
paragraflarda açıklayacağız gibi özel load/store komutlarını kullanarak bir döngü ile yapılabilmektedir.
Atomik bit işlemleri için güncel çekirdeklerde farklı mimarilerde farklı inline fonksiyonlar ya da
makrolar bulundurulmuştur. Bu fonksiyonların ya da makroların parametrik yapıları şöyledir:

.. code-block:: c

    void set_bit(int nr, volatile unsigned long *addr);
    void clear_bit(int nr, volatile unsigned long *addr);
    void change_bit(int nr, volatile unsigned long *addr);

    int test_and_set_bit(int nr, volatile unsigned long *addr);
    int test_and_clear_bit(int nr, volatile unsigned long *addr);
    int test_and_change_bit(int nr, volatile unsigned long *addr);

    int test_bit(int nr, const volatile unsigned long *addr);

Örneğin ``set_bit`` işlemi aşağıdaki fonksiyon ile yapılmaktadır:

.. code-block:: c

    static __always_inline void set_bit(long nr, volatile unsigned long *addr)
    {
        instrument_atomic_write(addr + BIT_WORD(nr), sizeof(long));
        arch_set_bit(nr, addr);
    }

Burada asıl işlemin ``arch_set_bit`` tarafından yapıldığını görüyorsunuz. Bu fonksiyon da çeşitli
işlemciler için ayrı ayrı yazılmıştır. Tabii daha önceden belirttiğimiz gibi bir grup işlemci aynı
özelliğe sahipse bunların *generic* biçimleri de vardır. Intel x86 işlemcileri için buradaki
``arch_set_bit`` fonksiyonu şöyle yazılmıştır:

.. code-block:: c

    static __always_inline void
    arch_set_bit(long nr, volatile unsigned long *addr)
    {
        if (__builtin_constant_p(nr)) {
            asm_inline volatile(LOCK_PREFIX "orb %b1,%0"
                : CONST_MASK_ADDR(nr, addr)
                : "iq" (CONST_MASK(nr))
                : "memory");
        } else {
            asm_inline volatile(LOCK_PREFIX __ASM_SIZE(bts) " %1,%0"
                : : RLONG_ADDR(addr), "Ir" (nr) : "memory");
        }
    }

Burada *inline assembly* sentaksıyla doğrudan bellek üzerinde ``LOCK`` öneki kullanılarak bit set işlemi
yapılmıştır.

Yukarıdaki atomik bit fonksiyonlarının parametrelerinin ``unsigned long *`` türünden olduğuna dikkat
ediniz. Her ne kadar parametreler bu türdense de bu fonksiyonlar ``unsigned int`` türü için de tür
dönüştürmesi uygulanarak kullanılabilir.

Şimdi de bu fonksiyonların işlevlerini açıklayalım. ``set_bit`` fonksiyonu bir nesnenin diğer bitlerine
dokunmadan belli bir bitini atomik bir biçimde 1 yapmak için, ``clear_bit`` fonksiyonu 0 yapmak için
kullanılmaktadır. ``change_bit`` fonksiyonu ise yine atomik bir biçimde nesnenin diğer bitlerine
dokunmadan belli bir bitini 1 ise 0, 0 ise 1 yapmaktadır.

``test_and_xxx`` fonksiyonları işlemi yapmakla birlikte ilgili bitin eski durumunu da geri
döndürmektedir. Örneğin ``test_and_set_bit`` fonksiyonu diğer bitlere dokunmadan belli bir biti atomik
olarak set eder ve eski değeri geri döndürür. Bu fonksiyonu *compare-exchange* fonksiyonuna
benzetebilirsiniz. Yani bu fonksiyon adeta ilgili bitteki değer 0 ise onu 1 yapmaktadır. Tabii yukarıda
da belirttiğimiz gibi genellikle bu işlemler için işlemcinin özel makine komutlarından faydalanılmaktadır.
Bu makine komutlarının içsel işleyişleri farklı olabilmektedir. ``test_and_clear_bit`` ve
``test_and_change_bit`` fonksiyonları da benzer biçimde eski değeri geri döndürmektedir. ``test_bit``
fonksiyonu ise belli bir bitin durumunu atomik bir biçimde elde etmek için kullanılmaktadır. Aşağıda bu
fonksiyonların işlevleri tablo biçiminde verilmiştir:

.. image:: _static/atomic-bit-ops.png
   :alt: Atomik Bit Fonksiyonları
   :align: center
   :width: 70%

Atomik bit fonksiyonları bit maskelerinden oluşan bayraklı nesnelerdeki bit bayraklarını set ya da clear
etmek için kullanılmaktadır. Örneğin:

.. code-block:: c

    unsigned long *flags_addr = /* bellek tabanlı aygıt adresi */;

    /* Flag bit pozisyonları */
    #define FLAG_DEVICE_READY       0
    #define FLAG_DMA_ENABLED        1
    #define FLAG_INTERRUPT_ENABLED  2
    #define FLAG_LOW_POWER_MODE     3
    #define FLAG_ERROR_STATE        4

    /* Flag'leri ayarla */
    void device_init(void)
    {
        set_bit(FLAG_DEVICE_READY, flags_addr);     /* Aygıtı hazır olarak işaretle */
        set_bit(FLAG_DMA_ENABLED, flags_addr);      /* DMA'yı etkinleştir */
    }

    /* Flag kontrolü */
    int is_device_ready(void)
    {
        return test_bit(FLAG_DEVICE_READY, flags_addr);
    }

    /* Flag temizle */
    void disable_dma(void)
    {
        clear_bit(FLAG_DMA_ENABLED, flags_addr);
    }

    /* Flag tersine çevir */
    void toggle_interrupt(void)
    {
        change_bit(FLAG_INTERRUPT_ENABLED, flags_addr);
    }

Burada bir aygıtı programlayan bazı fonksiyonlar bulunmaktadır. Aygıtın çeşitli bitleri çeşitli
durumları temsil etmektedir. Tabii bu aygıta *bellek tabanlı (memory mapped)* biçimde erişilmektedir.
Yukarıdaki fonksiyonlar da bu aygıtın çeşitli bitleriyle atomik işlemler yapmaktadır.

``test_and_xxxx`` fonksiyonları genellikle bitleri kilit olarak ele alındığı spinlock işlemlerinde
kullanılmaktadır. Örneğin:

.. code-block:: c

    #define LOCK_BIT    0

    static unsigned long lock_word = 0;

    void my_lock(void)
    {
        /* Bit 0 set olana kadar dene */
        preempt_disable();

        while (test_and_set_bit(LOCK_BIT, &lock_word)) {   /* spin işlemi */
            cpu_relax();
        }

        preempt_enable();

        /* Kilit alındı */
    }

    void my_unlock(void)
    {
        /* Bit 0'ı temizle */
        clear_bit(LOCK_BIT, &lock_word);
    }

Burada ``my_lock`` fonksiyonu belli bir bit üzerinde o bit 1 olduğu sürece spin yaparak beklemektedir.

Komutların Yer Değiştirmesi
===========================

İşlemciler biri diğerini etkilemeyen makine komutlarının sırasını değiştirerek çalıştırabilmektedir. 
Örneğin:

.. code-block:: none

    LOAD reg1, [mem1]
    LOAD reg2, [mem2]

Burada belleğin iki farklı bölgesindeki değerler işlemcinin farklı iki yazmacına çekilmiştir. Bu makine
komutlarının hangisinin önce yapıldığı sonuç üzerinde etkili olmayacaktır. İşte modern işlemciler kodun
çalışmasını hızlandırmak için bu komutları derleyicinin yazdığı sırada değil farklı sıralarda
yapabilmektedir. Bu duruma İngilizce *out of order execution* denilmektedir. Örneğin yukarıdaki makine
komutları işlemci tarafından aşağıdaki sırada da yapılabilecektir:

.. code-block:: none

    LOAD reg2, [mem2]
    LOAD reg1, [mem1]

Tabii işlemciler birbirleriyle ilişkili olan makine komutlarının sırasını değiştirmezler. Örneğin:

.. code-block:: none

    LOAD reg1, [mem]
    LOAD reg2, reg1

Ya da örneğin:

.. code-block:: none

    LOAD [mem], reg1
    LOAD reg2, [mem]

Bu makine komutlarının yer değiştirmesi programın yanlış çalışmasına yol açacağından işlemci bunları yer
değiştirmez. Ancak maalesef birden fazla CPU ya da çekirdek söz konusu olduğunda diğer çekirdekler
birbirine bağlı bazı işlemleri bile farklı sıralarda görebilmektedir. Komutların yer değiştirmesinin
gözlemlenebilir etkisi çok işlemcili ya da çok çekirdekli sistemlerde ortaya çıkmaktadır. Bu konunun
ayrıntılarını *bellek bariyerleri (memory barriers)* konusu içerisinde ele alacağız.

Burada "mademki çalışan kodu etkilemiyor o zaman sorun nerede?"*" diye düşünebilirsiniz. Ancak işte birden
fazla işlemci ya da çekirdeğin bulunduğu sistemlerde bu komut yer değiştirmesi (daha doğru bir ifadeyle
görünürlüğün yer değiştirmesi) bazı sorunlara yol açabilmektedir.

İşlemcilerin komutları farklı sıralarda yapıyormuş gibi görünmesinin nedenlerinden biri *boru hattı
(pipeline) mekanizmasıdır*. İşlemci komutları boru hattı kuyruğuna göndermekte, bu kuyrukta işlemler
daha küçük evrelere (phases) ayrılmakta ve bu evreler mümkün olduğu kadar eşzamanlı biçimde
yapılmaktadır. Ancak salt bu evrelere ayırma işlemi tek başına komutların bitirme sırasını değiştirmez;
basit, tek yola sahip bir boru hattında komutlar girdikleri sırayla çıkar. Bitirme sırasının değişmesi,
genellikle boru hattına eklenen ek mekanizmalardan kaynaklanır: örneğin çarpma veya bölme gibi işlemler
için ayrı ve daha gecikmeli yürütme birimleri bulunması ya da işlemcinin operandı hazır olan komutu,
önündeki bekleyen bir komutu atlayarak çalıştırdığı gerçek *sıra-dışı yürütme (out-of-order execution)*
mekanizmasıdır. Bu durumda önce kuyruğa gönderilen bir makine komutu, sonra gönderilen başka bir
komuttan daha sonra işlemini bitirebilir. İşlemcilerin boru hattı mekanizması oldukça ilginç ve detaylı
bir mekanizmadır. Biz burada bu mekanizmanın ayrıntıları üzerinde durmayacağız. Ancak bütün bunların bir
sonucu olarak, aynı çekirdek içinde birbirleriyle ilişkili olmayan makine komutları sanki farklı
sıralarda yapılıyormuş gibi bir etki oluşabilmektedir.

Çok işlemcili ya da çok çekirdekli sistemlerde ise, birbirleriyle ilişkili (bağımlı) komutların bile
diğer çekirdekler tarafından farklı sırada görünmesi söz konusu olabilir. Bunun nedeni boru hattı
mekanizması değildir; tamamen ayrı ve daha önemli bir konudur. Her çekirdek, belleğe yazma işlemini
hemen tamamlamak yerine önce kendi *yazma tamponuna (store buffer)* yazar, tampon arka planda cache'e
ve oradan da *önbellek tutarlılık (cache coherency)* protokolü üzerinden diğer çekirdeklere yansıtır. Eğer
işlemci mimarisi *zayıf bellek tutarlılık modeli (weak memory consistency model)* kullanıyorsa, bu
tamponun yansıtılma sırası program sırasıyla aynı olmak zorunda değildir; dolayısıyla bir çekirdeğin
ardışık iki yazması, başka bir çekirdeğe ters sırada görünebilir. 

İşlemciler komutları evrelere bölüp çalıştırırken genel olarak her cycle'da bir evreyi çalıştırmaktadır.
Böylece her cycle'da boru hattında sonraki komutların evreleri de yapılmaktadır. Bu durum özellikle
basit, tek yola sahip RISC işlemcilerinde, hazard oluşmadığı sürece her cycle'da bir makine komutunun
tamamlanmasını sağlayabilmektedir.

Ayrıca işlemciler daha karmaşık komutları kendi içerisinde de parçalara ayırabilmektedir. Bunlara da
işlemci terminolojisinde genel olarak *mikrokod (microcode)* denilmektedir. Mikrokodları *işlemcinin
kendi içindeki yazılımı* gibi de düşünebilirsiniz. Örneğin aşağıdaki gibi bir makine komutu söz konusu
olsun:

.. code-block:: none

    ADD R1, R2

Bu komut işlemci tarafından alt işlemlere ayrılmaktadır. Örneğin:

1. R1'i oku
2. R2'yi oku
3. ALU'da topla
4. Sonucu R1'e yaz

Mikrokodlar daha çok CISC işlemcilerine özgüdür. RISC işlemcileri komutları mikrokodlara bölerek işlem
yapmaz; tek bir lojik devreyle bütünsel bir biçimde işlemleri yapar. Tabii bu sırada komutlar evrelere
ayrılarak yukarıda belirttiğimiz gibi kendi içlerinde pipeline mekanizması eşliğinde çalıştırılmaktadır.

Konuyu derinleştirmeden önce bazı önemli terimlerin ne anlam ifade ettiğini açıklayalım:

.. image:: _static/memory-ordering-terms.png
   :alt: Bellek Sıralaması ile İlgili Terimler
   :align: center
   :width: 70%

Modern işlemcilerde işlemlerin "programdaki sırası", "çalışma sırası" ve "görünürlük sırası" farklı
olabilmektedir. Örneğin:

.. code-block:: c

    data = 42;
    ready = 1;

Burada ``STORE`` işlemleri birbirinden farklı yerlere yapıldığı için işlemci bunları değişik sırada
yapabilmekte ya da farklı işlemciler ve çekirdekler bunları farklı sıralarda yapılıyormuş gibi
görebilmektedir. Yani burada diğer bir işlemci ya da çekirdek ``ready`` değerini 1 olarak gördüğünde
``data`` değerinin o anda 42 olması zorunlu değildir.

Ancak maalesef birden fazla işlemci ya da çekirdeğin bulunduğu sistemlerde birbirleri ile ilişkili
komutları bile başka çekirdekler değişik sırada yapılıyormuş gibi görebilmektedir. Örneğin ``a`` ve
``b``'nin önceki değerleri 0 olsun. Bir işlemci ya da çekirdekte aşağıdaki işlemlerin yapıldığını
varsayalım:

.. code-block:: c

    a = 1;
    b = a;

Diğer bir işlemci ya da çekirdek ``b``'de 1 gördüğü halde ``a``'da 0 görebilmektedir.

İşlemcilerin birbirinden bağımsız ``LOAD``/``STORE`` komutları için kendi içlerinde uyguladıkları dört
farklı *çalıştırma sıralaması (execution reordering)* vardır: Load/Load, Load/Store, Store/Store ve
Store/Load.

.. image:: _static/reordering-types.png
   :alt: Dört Temel Yeniden Sıralama Türü
   :align: center
   :width: 70%

Yukarıdaki dört yer değiştirme her türlü işlemci tarafından uygulanmamaktadır. Örneğin Intel işlemcileri
yalnızca Store/Load işlemlerinin yerlerini değiştirebilmektedir. Diğer işlemlerde yer değiştirme
yapmamaktadır. Ancak genel olarak RISC işlemcileri yukarıdaki dört yer değiştirmeyi de yapabilmektedir.
Aşağıda bazı yaygın işlemcilerin hangi yer değiştirmeleri yaptığını tablo biçiminde veriyoruz:

.. image:: _static/reordering-arch-table.png
   :alt: İşlemci Mimarilerine Göre Yeniden Sıralama Türleri
   :align: center
   :width: 60%

Genel olarak diğer işlemciler söz konusu olduğunda görünürlük sıralaması üç biçimde olabilmektedir:

1. **Sequential Consistency (SC):** Bu modelde komutlar her işlemci ya da çekirdekte program sırasında
   gözükür.

2. **Total Store Order (TSO):** Bu modelde yalnızca Store/Load program sırası değiştirilebilmekte ve
   diğer işlemci ya da çekirdekler yalnızca Store/Load işlemlerini farklı sıralarda yapılıyormuş gibi
   görebilmektedir. Intel x86 işlemci ailesi bu modeli kullanmaktadır.

3. **Relaxed (Weak) Memory Ordering:** Bu modelde yukarıda belirttiğimiz dört grup işlemin de program
   sırası değiştirilebilmektedir. Diğer işlemciler ve çekirdekler bunları farklı sıralarda
   görebilmektedir. ARM, RISC-V, PowerPC gibi işlemciler bu modeli kullanmaktadır.

Komutların yer değiştirmesi aslında derleyici tarafından da yapılan bir optimizasyon etkinliğidir. 
Derleyiciler de komutlar daha hızlı çalışsın diye birbirleriyle ilişkisi olmayan makine komutlarının 
yerlerini değiştirebilmektedir. Ancak senkronizasyon sorunlarını oluşturan ana unsur derleyiciden ziyade 
işlemci tarafından yapılan komut yer değiştirmesidir. Zaten bildiğiniz gibi derleyiciler optimizasyon 
aşamasında programcının yazdığı deyimleri de eğer mümkünse elimine edebilmektedir. Örneğin:

.. code-block:: c

    a = 10;
    a = 20;

Burada derleyici ``a = 10`` deyimini tamamen elimine edebilir. Çünkü bu deyim kaldırıldığında programın
gözlemlenebilir davranışında bir değişiklik oluşmayacaktır. Ancak işlemciler böyle bir eliminasyonu
yapmazlar. İşlemciler yalnızca komut çalıştırması sırasında basit birtakım iyileştirmeler yapabilmektedir.

Bellek Bariyerleri
==================

*Bellek bariyerleri (memory barriers)* bir işlem yapılmadan önce diğer işlemlerin yapılmış
olduğunu garanti etmek amacıyla oluşturulan mekanizmalardır. Bellek bariyerleri uygun yerlerde
kullanılmazsa çok işlemcili ya da çok çekirdekli sistemlerde çalışan kodlarda böcekler oluşabilmektedir.
Aşağıdaki koda dikkat ediniz:

.. code-block:: c

    /* Thread 1 */

    data = 42;
    ready = 1;

    /* Thread 2 */

    while (ready == 0)
        ;
    use(data);

Burada kodu yazan sistem programcısı *ready = 1 ise kesinlikle data = 42 olacağını* varsaymıştır.
Çünkü ``data`` ataması ``ready`` atamasından önce yapılmıştır. Dolayısıyla Thread 2'de ``ready == 1``
olduğunda ``data == 42`` olacağı sanılmaktadır. Ancak burada bir ihmal söz konusudur. Derleyici ya da
işlemci ``data`` ve ``ready`` değişkenleri birbirlerinden bağımsız olduğu için bu atamaları yer
değiştirebilmekte ya da başka bir işlemci ya da çekirdek bunları farklı sıralarda yapılıyormuş gibi
görebilmektedir. Bu atamalar yer değiştirildiğinde aşağıdaki durum oluşacaktır:

.. code-block:: c

    /* Thread 1 */

    ready = 1;
    /* ---> Dikkat! diğer işlemcideki kod bu arada çalışabilir */
    data = 42;

    /* Thread 2 */

    while (ready == 0)
        ;
    use(data);

Artık sorun kolaylıkla anlaşılabilir. Diğer işlemci ya da çekirdek ``ready = 1`` durumu oluştuğunda
``use`` işlemine girebilir. Bu durumda ``data`` değişkeni eski değeriyle kullanılacaktır. İşte sistem
programcısının *görünürlük sırasının (visibility order)* değişebileceğini göz önünde bulundurarak bu
tür durumlara önlem alması gerekir. Bu tür önlemler *bellek bariyerleri (memory barriers)* denilen
mekanizmalarla alınmaktadır.

Burada bir noktaya dikkatinizi çekmek istiyoruz. Derleyici de işlemci kendi akışlarında bağımsız
olmayan komutları yer değiştirmemektedir. Örneğin:

.. code-block:: c

    data = 42;
    use(data);

Buradaki işlemi yürüten işlemci ya da çekirdekte bu sıra korunmaktadır. Buradaki sorun başka işlemci
ya da çekirdeklerin bu işlemleri sanki farklı sıralarda yapılıyormuş gibi görmesidir. Buna da
*görünürlük sırası (visibility order)* denildiğini anımsayınız.

Biz yukarıdaki örnekte yalnızca peş peşe iki işlemin çalışma sırası ve görünürlük sırası üzerinde
örnek verdik. Aslında bu durum yalnızca peş peşe gelen iki makine komutu için söz konusu değildir.
Peş peşe gelen ikiden fazla makine komutunda da çalışma sırası ve görünürlük sırası değişebilmektedir.


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

Kritik Kod Blokları (Critical Sections)
=======================================

Çekirdek kodlarında senkronizasyon uygulamaya neden gerek vardır? Tıpkı kullanıcı
modundaki çok thread'li uygulamalarda olduğu gibi bir akış çekirdek içerisinde
paylaşılan bir veri yapısı üzerinde işlem yaparken bir biçimde thread'ler arası
geçiş ya da kesme olayı söz konusu olduğunda başka bir akış da bu paylaşılan veri
yapısını kullanmak isterse bu veri yapısı bozulabilmektedir. Tabii çok çekirdekli
sistemlerde farklı çekirdeklerdeki thread'ler de çekirdek içerisindeki ortak veri
yapıları üzerinde eş zamanlı işlemler yapabilmektedir. Örneğin çekirdek kodunun bir
bağlı listeye eleman eklediğini varsayalım. Tam bu işlemin ortalarında bir yerde
thread'ler arası geçiş oluşursa ya da başka bir çekirdekteki thread de aynı bağlı
liste üzerinde işlem yapmaya çalışırsa tüm veri yapısı bozulabilecektir.

Çekirdek senkronizasyonunda en önemli kavram *kritik kod (critical section)* denilen
kavramdır. Başından sonuna kadar tek bir akış tarafından işletilmesi gereken kodlara
*kritik kod* denilmektedir. Kritik kod kavramını atomiklikle karıştırmayınız.
Atomiklik *bir işlem yapılırken thread'ler arası geçiş ya da kesme mekanizması
yoluyla* işlemin kesintiye uğramaması anlamına gelmektedir. Bir akış çekirdekteki
bir *kritik kod*'a girdiğinde akış *preemption*'dan dolayı kesintiye uğrayabilir.
Ancak bu durumda bile başka bir akış kesintiye uğramış olan akış işini bitirene kadar
kritik koda girmemelidir. Yani kritik koda girmiş olan bir akışın kesintiye uğraması
biçiminde bir koşul yoktur.

Çekirdek kodları kullanıcı modundaki kodlar gibi değildir. Çekirdek kodları aynı
zaman diliminde pek çok akış tarafından iç içe geçecek biçimde çalıştırılabilmektedir.
Bu nedenle çekirdek tasarımında ve aygıt sürücü yazımında senkronizasyon her zaman
göz önüne alınmalıdır. Maalesef senkronizasyon sorunlarının tespit edilmesi oldukça
zor olabilmektedir. Çünkü senkronizasyon problemlerinin oluşturduğu böceklerin
*reproduce* edilmesi oldukça zordur.

Çekirdek içerisindeki *kritik kod* bloklarının önemli bir bölümü birden fazla akışın
paylaşılan bir veri yapısına erişilmesi nedeniyle oluşturulmaktadır. Örneğin aynı
hash tablosuna birden fazla prosesin çağırdığı sistem fonksiyonları eleman ekleyebilir.
Bu durumda bu hash tablosunun böyle erişimlerde *serialize* edilmesi gerekir. Ancak
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

Manuel Kritik Kod Bloklarının Oluşturulmasında Sorunlar
-------------------------------------------------------

Kritik kodlar ancak özel makine komutları kullanılarak oluşturulabilmektedir.
Aşağıdaki gibi basit bir mantıkla kritik kod oluşturulamaz:

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

Bu biçimdeki manuel kritik kod oluşturma girişiminin iki sorunu vardır:

1. Bekleme bloke edilerek değil meşgul bir döngüde (busy loop) yapılmaktadır.
   Yani bir thread kritik kod içerisindeyse diğeri CPU zamanı harcayarak meşgul
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
   thread kritik koda girebilir.

İşte bu sakıncayı ortadan kaldırmak için özel makine komutlarından
faydalanılmaktadır. Bugün bilgisayar sistemlerinde birden fazla işlemci ya da çekirdek
bulunabildiği için kritik kod oluşturan sistem programcılarının bunlara dikkat
etmesi gerekir. Linux'un çekirdek kodlarında zaten çeşitli senaryolar için
kullanılabilecek senkronizasyon nesneleri hazır biçimde bulunmaktadır. Bu bölümde
biz bu senkronizasyon nesnelerini ele alacağız. Bölümün sonlarına doğru da bu
senkronizasyon nesnelerinin oluşturulabilmesi için gereken makine komutları hakkında
bilgiler vereceğiz.

İşletim sistemindeki senkronizasyon nesnelerini temelde iki gruba ayırabiliriz:

1) Blokeye yol açan senkronizasyon nesneleri
2) Blokeye yol açmayan senkronizasyon nesneleri

Blokeye yol açan senkronizasyon nesneleri çalışmakta olan kodun çalışmasına ara vererek ileride ele alacağımız
*bekleme kuyruklarında (wait queue)* bekletildiği yani göreli olarak uzun süre beklemeye yol açan senkronizasyon
nesneleridir. Blokeye yol açmayan senkronizasyon nesneleri ise akışın bekletilmediği senkronizasyon nesneleridir.
Bunları da kendi aralarında iki kısma ayırabiliriz. Bunların bir bölümü okuma sırasında döngü içerisinde spin
yaparak beklemeyi sağlamaktadır. Diğer bölümü ise modern *lock-free* veri yapılarından oluşmaktadır.

Bu bölümde açıklayacağımız çekirdek senkronizasyon nesnelerini kullanıcı modundaki thread senkronizasyonunda
kullanılan senkronizasyon nesneleri ile karıştırmayınız. Kullanıcı modundaki senkronizasyon nesneleri kullanıcı
modundaki thread'leri senkronize etmek için bulundurulmuştur. Oysa bu bölümde göreceğimiz senkronizasyon nesneleri
-isimleri benzer olsa da- çekirdek kodlarının senkronizasyonunda kullanılmaktadır. Tabii kullanıcı modundaki
senkronizasyon nesnelerinin bir bölümü aslında burada açıklayacağımız çekirdekteki senkronizasyon nesneleri
kullanılarak yazılmıştır.

Mutex Nesneleri
===============

Kritik kod oluşturmak için en çok kullanılan senkronizasyon nesnelerinden biri *mutex (mutual exclusion)*
denilen nesnelerdir. (UNIX/Linux sistemlerinde kullanıcı modundan kullanılabilecek mutex nesneleri de
vardır. Yukarıda belirttiğimiz gibi biz burada çekirdeğin içerisinde bulunan mutex nesneleri üzerinde
duracağız.) Mutex nesneleri Linux çekirdeğine 2.6 versiyonlarıyla eklenmiştir. Bundan önce mutex işlemleri
ikili semaphore'larla yapılıyordu.

Çekirdeğin mutex mekanizması kullanım bakımından kullanıcı modundaki mutex mekanizmasına çok
benzemektedir. Çekirdek mutex nesnelerinin yine thread temelinde sahipliği vardır. Çekirdek mutex
nesneleri thread'i bloke edip onu bekleme kuyruklarında bekletebilmektedir.

Mutex mekanizması şöyle işletilmektedir: Önce global düzeyde ya da çekirdeğin heap sisteminde bir mutex
nesnesi yaratılır. Kritik koda girişte bu mutex nesnesinin sahipliği ele geçirilmeye çalışılır. Mutex'in
sahipliğinin ele geçirilmesine *mutex'in kilitlenmesi (mutex lock)* de denilmektedir. Eğer mutex'in
sahipliği ele geçirilirse (yani mutex kilitlenirse) sahiplik bırakılana kadar (yani kilit bırakılana kadar)
başka bir thread kritik koda giremez. Mutex'in sahipliğini almaya çalışan thread mutex kilitli ise bloke
olarak mutex kilidi açılana kadar bekler. Mutex'in sahipliğini almış olan thread kritik koddan çıkarken
mutex'in sahipliğini bırakır (yani mutex'in kilidini açar). Böylece blokede bekleyen thread'lerden biri
mutex'in sahipliğini alarak kritik koda girer. Kritik kod tipik olarak şöyle oluşturulmaktadır:

.. code-block:: c

    mutex_lock(...);
    ...
    ...    <KRİTİK KOD>
    ...
    mutex_unlock(...);

Akışlardan biri ``mutex_lock`` fonksiyonuna geldiğinde eğer mutex kilitlenmemişse mutex'i kilitler ve
kritik koda giriş yapar. Eğer mutex zaten kilitlenmişse ``mutex_lock`` fonksiyonunda thread bloke edilir
ve bekleme kuyruğuna alınır. Kritik koda girmiş olan akış ``mutex_unlock`` fonksiyonu ile mutex nesnesinin
kilidini bırakır. Böylece nesneyi bekleyen thread'lerden biri nesnenin sahipliğini alarak mutex'i
kilitler. Birden fazla akışın ``mutex_lock`` fonksiyonunda bloke edilmesi durumunda mutex'in kilidi
açıldığında bunlardan hangisinin mutex kilidini alarak kritik koda gireceği konusunda bir garanti
verilmemektedir. (İlk bloke olan akışın mutex kilidini alarak kritik koda gireceğini düşünebilirsiniz,
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

Mutex Nesnelerinin Tanımlanması ve İlkDeğer Verilmesi
-----------------------------------------------------

Mutex nesnesi ``mutex`` isimli bir yapıyla temsil edilmektedir. Sistem programcısı bu yapı türünden
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

Mutex Nesnelerinin Kilitlenmesi (mutex_lock)
--------------------------------------------

Mutex nesnesini kilitlemek için ``mutex_lock`` fonksiyonu kullanılır:

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

Mutex Nesnelerinin  Kilidinin Bırakılması (mutex_unlock)
--------------------------------------------------------

Mutex nesnesinin kilidini bırakmak için (nesneyi unlock etmek için) ``mutex_unlock`` fonksiyonu
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

Çekirdeğin mutex nesneleri *özyinelemeli (recursive)* değildir. Yani thread bir mutex nesnesini
kilitlemişse aynı mutex nesnesini kilitlemeye çalışırsa *deadlock* oluşur.

Mutex Kullanımına Örnek
-----------------------

Aşağıda mutex mekanizmasının çalışmasına ilişkin bir örnek verilmiştir. Burada aygıt sürücü için iki *ioctl*
kodu oluşturulmuştur. ``IOCTL_TEST1`` kodunda mutex'in sahipliği alınıp 30 saniye beklenmektedir.
``IOCTL_TEST2`` kodunda ise bekleme yapılmadan mutex'in sahipliği alınmak istenmiştir. Test için önce
*test-sync1* programını sonra da başka bir terminalde *test-sync2* programını çalıştırmalısınız.
Mesajları *dmesg* komutuyla inceleyebilirsiniz.
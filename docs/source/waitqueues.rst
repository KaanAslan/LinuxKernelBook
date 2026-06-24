===================
Bekleme Kuyrukları
===================

Bu bölümde önce bekleme kuyruklarının (wait queues) genel yapısını açıklayacağız. Sonra da
thread'lerin çalışma kuyruğundan (run queue) bekleme kuyruklarına nasıl aktarıldığı (yani
thread'lerin nasıl bloke edildiği) ve yeniden nasıl çalışır duruma getirildiği (yani blokenin nasıl
çözüldüğü) konuları üzerinde duracağız. *Çizelgeleyici (scheduler)* alt sistem başka bir bölümde
ayrıntılarıyla ele alınacaktır.

Linux çekirdek programcılarının bloke işlemleri ile ilgili olan şu süreçler hakkında bilgi sahibi
olması gerekir:

- Bekleme kuyruklarının veri yapısı nasıldır?
- Bekleme kuyrukları nasıl oluşturulup nasıl yok edilmektedir?
- Çalışma kuyruklarından bekleme kuyruklarına aktarım (yani bloke işlemi) nasıl yapılmaktadır?
- Bekleme kuyruklarından çalışma kuyruklarına aktarım (yani blokenin çözülmesi) nasıl
  yapılmaktadır?
- Bekleme kuyrukları üzerinde işlem yapan çekirdek fonksiyonları bu işlemleri nasıl
  yapmaktadır?

Tabii Linux'un ilk versiyonlarında bu süreçler oldukça basit kodlarla gerçekleştirilmişti. Ancak
zaman içerisinde sinekten yağ çıkartma noktasına gelindi ve bu işlemler de gittikçe iyileştirildi.
Bunun sonucu olarak da kodlar biraz daha karmaşık hale geldi.

Çalışma Kuyrukları ve Thread'lerin Çizelgelenmesi
=================================================

Linux çekirdeklerinde çizelgeleyici (scheduler) alt sistem zaman içerisinde birkaç kere önemli ölçüde
değiştirilmiştir. Mevcut Linux çekirdeklerinde sistemdeki her işlemci ya da çekirdek için ayrı bir
*çalışma kuyruğu (run queue)* bulundurulmaktadır. Yani her işlemci ya da çekirdek kendi çalışma
kuyruğundaki thread'leri çizelgelemektedir. Çalışma temel olarak *zaman paylaşımlı (time sharing)* biçimde
yapılmaktadır. Yani sıradaki thread CPU'ya atanır, belli bir süre çalıştırılır, sonra thread'in
çalışmasına ara verilir ve kuyruktaki yeni thread CPU'ya atanır. Bu işlem böyle devam ettirilir. Bir
thread'in parçalı çalışma süresine *quantum süresi (time quantum)* denilmektedir. Thread'lerin quantum
süreleri aynı olmak zorunda değildir. Bu konunun ayrıntılarını çizelgeleyici alt sistemin ele alındığı
bölümde açıklayacağız. Aşağıda güncel çekirdeklerdeki çizelgeleme işlemlerini bir şekille betimliyoruz:

.. image:: _static/scheduler-run-queue.png
   :alt: Çizelgeleyici ve Çalışma Kuyruğu
   :align: center
   :width: 80%

Çalışma kuyruğundaki bir thread'e çalışma sırası geldiğinde o thread CPU'ya atanıp belli bir süre
çalıştırılır. Bu süre dolduğunda bir sonraki turda kalınan yerden çalışmaya devam edebilmesi için
thread çalışma kuyruğuna geri bırakılır. Bir thread'in çalışmasına ara verilip çalışma kuyruğundaki
diğer thread'in CPU'ya atanması sürecine *bağlamsal geçiş (context switch)*, (bağlamsal geçiş terimi 
yerine *task switch* terimi de kullanılabilmektedir), thread'in quantum süresi bittiğinde CPU'dan 
alınması işlemine de *koparma (preemption)* denilmektedir. (*Preemption* İngilizcede "zorla ele geçirmek, 
el koymak" gibi anlamlara gelmektedir. Biz *preemption* yerine Türkçe "koparma" sözücüğünü de kullanacağız.) 
Bağlamsal geçiş donanım kesmeleriyle yapılmaktadır. Genel amaçlı bilgisayar donanımlarında periyodik kesme 
üreten *zamanlayıcı (timer)* devreler bulunmaktadır. Zamanlayıcı devreleri yoluyla oluşturulan kesmeler belli bir 
sayıya geldiğinde çizelgeleyici o anda çalışmakta olan kodu herhangi bir noktasında keserek çalışmaya ara verebilmektedir.

Thread'lerin çalışmasına ara verilmesi ve çalışmanın kalınan yerden devam ettirilmesi aslında zor bir
işlem değildir. Thread'in o andaki tüm konumu aslında CPU yazmaçlarının içerisindeki değerlerden
oluşmaktadır. Bağlamsal geçiş sırasında CPU yazmaçlarının içerisindeki değerler thread'in
``task_struct`` alanına kaydedilmektedir. Thread CPU'ya atanırken de bu kaydedilmiş bilgiler oradan
alınarak yeniden CPU yazmaçlarına aktarılmaktadır. Tabii tüm bu işlemler bir zaman kaybına da yol
açmaktadır. Eğer quantum süresi çok kısa tutulursa çok bağlamsal geçiş oluşur ve *birim zamanda yapılan
iş miktarı (throughput)* düşer. Eğer bağlamsal geçiş çok uzun tutulursa bu durumda da interaktivite
azalır. Bir thread işletim sistemi tarafından bir CPU'nun çalışma kuyruğuna atandığında onun hep o kuyrukta
kalması garanti değildir. Zaman içerisinde (tıpkı süper marketlerdeki kasa kuyruklarında
olduğu gibi) kuyruklar arasında dengesizlikler oluşabilmektedir. Bu durumda işletim sistemi dengeyi
sağlamak için thread'leri daha boş olan bir CPU'nun çalışma kuyruğuna taşıyabilmektedir.

Thread'lerin Bloke Olması
-------------------------

Bir thread uzun sürebilecek dışsal olayları CPU zamanı harcayarak beklemez. Bu tür durumlarda thread'ler CPU'nun 
çalışma kuyruğundan çıkartılarak *bekleme kuyrukları (wait queues)* denilen kuyruklarda bekletilmektedir. Bu sürece 
*thread'in bloke olması* denilmektedir. Örneğin ``read`` POSIX fonksiyonuyla bir dosyadan okuma yapmak isteyelim. 
Anımsanacağı gibi ``read`` fonksiyonu ``sys_read`` sistem fonksiyonunu çağırmaktadır. Bu fonksiyon da önce okunacak 
yerin sayfa önbelleğinde (page cache) olup olmadığına bakmaktadır. Okunacak yer page cache içerisindeyse thread bloke olmadan
okuma yapılır. Ancak okunacak yer sayfa önbelleğinde değilse disk okumaları yavaş olduğu için thread
bloke edilir, çalışma kuyruğundan çıkartılarak bir bekleme kuyruğunda bekletilir. Disk okuması
gerçekleştiğinde thread yeniden çalışma kuyruğuna yerleştirilmektedir. Spinlock ve readers/writer lock
nesneleri dışındaki senkronizasyon nesnelerinde de eğer kilit kapalıysa lock işlemini yapmaya çalışan
thread'ler benzer biçimde bloke edilmektedir. ``sleep`` gibi fonksiyonlar da yine blokeye yol açmaktadır.
Örneğin:

.. code-block:: c

    sleep(10);

Burada thread'in 10 saniye bekletilmesi istenmiştir. İşte işletim sistemi bu bekleme sırasında CPU
zamanı harcamasın diye thread'i çalışma kuyruğundan çıkartır ve bekleme kuyruğuna alır. 10 saniye
süre geçince de onu yeniden çalışma kuyruğuna yerleştirir. Böylece thread hiç CPU zamanı harcamadan
10 saniye bekletilmiş olur.

Thread'lerin Yaşam Döngüsü
--------------------------

Bir thread'in yaşam döngüsü yalın bir biçimde şöyle betimlenebilir:

.. image:: _static/thread-lifecycle.png
   :alt: Thread Yaşam Döngüsü
   :align: center
   :width: 75%

Buradaki *Running* thread'in CPU'ya atanmış ve çalışmakta olduğu, *Ready* ise thread'in çalışma kuyruğunda 
bulunduğunu ve sonraki quantum'u beklediği anlamına gelmektedir. Thread dışsal bir olay nedeniyle bloke olduğunda 
bekleme kuyruklarına alınır. Şeklimizdeki *Waiting* ise thread'in bekleme kuyruğunda beklediğini belirtmektedir. 
Dışsal olay gerçekleştiğinde thread'in blokesi çözülüp yeniden çalışma kuyruğuna yerleştirilmektedir. Tabii buradaki 
şekil oldukça sadeleştirilmiş bir şekildir. Örneğin thread'in sonlanması başka biçimlerde de gerçekleşebilmektedir.

IO Yoğun ve CPU Yoğun Thread'ler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bir thread CPU'ya atandığında eğer quantum süresinin çok azını kullanıp hemen bloke olarak uykuya
dalıyorsa bu biçimdeki thread'lere *IO yoğun (IO bound)* thread'ler denilmektedir. Sistemde çok
sayıda IO yoğun thread'in bulunması CPU'yu önemli ölçüde meşgul etmeyeceği için ciddi bir yavaşlamaya
da yol açmayacaktır. Uygulama programlarının büyük çoğunluğundaki thread'ler IO yoğun biçimdedir.
Örneğin:

.. code-block:: c

    double val;
    /* ... */

    for (;;) {
        printf("Bir deger sayi giriniz:");
        fflush(stdout);
        scanf("%lf", &val);
        if (val == 0)
            break;
        printf("%f\n", val);
    }

Buradaki thread'in CPU kullanım oranı çok düşüktür. Çünkü biraz çalışıp hemen bloke olmaktadır. Eğer
bir thread CPU'ya atandığında quantum süresinin büyük bölümünü hiç bloke olmadan kullanıyorsa bu tür
thread'lere *CPU yoğun (CPU bound)* thread'ler denilmektedir. Genellikle matematiksel hesaplar yapan
thread'ler CPU yoğun olma eğilimindedir. Sistemde çok sayıda CPU yoğun thread'in bulunması ciddi
yavaşlamalara yol açabilmektedir. Örneğin:

.. code-block:: c

    long long count = 0;
    /* ... */

    for (long long i = 0; i < 100000000000; ++i)
        if (i % 7 == 0)
            ++count;

    printf("%lld\n", count);

Buradaki thread CPU yoğundur. Çünkü kendisine verilen quantum süresini hiç bloke olmadan sonuna kadar
kullanmaktadır. Programınızdaki thread'lerin CPU kullanım sürelerini çeşitli utility programlarla
gözlemleyebilirsiniz. Örneğin ``htop`` programı (``top`` programının biraz daha gelişmiş bir
versiyonudur) ve ``perf`` programı ile thread'lerinizin CPU kullanımlarını görebilirsiniz.

Bekleme Kuyruğuklarına İlişkin Veri Yapıları ve Çekirdek Temel Fonksiyonları
============================================================================

Linux çekirdeklerinde bekleme kuyruklarının genel yapısı zaman içerisinde pek değişmemiştir. Biz
burada doğrudan çekirdeğin güncel versiyonlarını temel alacağız. Çekirdeğin güncel versiyonlarında
bekleme kuyrukları bir bağlı liste biçiminde organize edilmiştir. Bu bağlı listenin kök düğümü
``include/linux/wait.h`` dosyasındaki ``wait_queue_head`` isimli bir yapıda tutulmaktadır. Bu yapı
aynı zamanda ``wait_queue_head_t`` ismiyle de typedef edilmiştir:

.. code-block:: c

    struct wait_queue_head {
        spinlock_t       lock;      /* listeyi koruyan spinlock kilidi */
        struct list_head head;      /* bağlı listenin kök düğümü */
    };
    typedef struct wait_queue_head wait_queue_head_t;

Buradaki ``lock`` elemanı bağlı liste işlemleri yapılırken eş zamanlı erişimlerde kuyruğu korumak
için bulundurulmuştur. ``head`` elemanı ise kök düğümü belirtmektedir.

``wait_queue_head`` bağlı listesi elemanları ``wait_queue_entry`` türünden olan düğümleri
tutmaktadır. Başka bir deyişle ``wait_queue_head`` yapısı aslında ``wait_queue_entry`` nesnelerini
tutan bir bağlı listedir. ``wait_queue_entry`` yapısı şöyle bildirilmiştir:

.. code-block:: c

    struct wait_queue_entry {
        unsigned int        flags;
        void               *private;
        wait_queue_func_t   func;
        struct list_head    entry;
    };

Yapıdaki ``flags`` elemanı bitsel biçimde temsil edilen bayrakları tutmaktadır. Bu bayraklar bekleme
kuyruğunu işleten algoritmalar tarafından set edilip kullanılmaktadır. İzleyen paragraflarda bu
bayraklar hakkında bilgiler vereceğiz. Yapının ``private`` elemanı her ne kadar ``void`` bir
göstericiyse de aslında tipik olarak bekleme kuyruğundaki thread'in ``task_struct`` nesne adreslerini
tutmaktadır. (Veri yapısı genel tasarlanmıştır; bazı durumlarda bu eleman başka nesneleri de
gösterebilmektedir.) Yapının ``func`` elemanı thread uyandırılacağı zaman çağrılacak uyandırma
fonksiyonun adresini tutmaktadır. Veri yapısı genel olduğu için çokbiçimli etki yaratmak amacıyla
fonksiyon göstericisinden faydalanılmıştır. Yapının ``entry`` elemanı sonraki düğümün yerini
göstermektedir.

.. image:: _static/wait-queue-list.png
   :alt: Bekleme Kuyruğu Bağlı Listesi
   :align: center

Çekirdek içerisinde thread'i bekleme kuyruklarına bir düğüm olarak yerleştiren ve oradan çıkartarak
yine çalışma kuyruklarına yerleştiren daha yüksek seviyeli çekirdek fonksiyonları oluşturulmuştur.
Bu yüksek seviyeli fonksiyonlar export edildikleri için çekirdek modülleri ve aygıt sürücüler
tarafından kullanılabilmektedir.


Bir bekleme kuyruğunu boş bir biçimde oluşturmak için ``DECLARE_WAIT_QUEUE_HEAD`` makrosu
kullanılmaktadır. Bu makro ``include/linux/wait.h`` dosyası içerisinde bildirilmiştir. Makroya
tanımlanacak olan ``wait_queue_head`` yapısı türünden değişkenin ismi verilmektedir. Örneğin:

.. code-block:: c

    static DECLARE_WAIT_QUEUE_HEAD(g_wq);

Bu örnekte bizim bekleme kuyruğumuzun ismi ``g_wq`` biçimindedir. Tabii bekleme kuyrukları
genellikle static ömürlü olmaktadır. Yani tipik olarak global bir değişken olarak oluşturulmaktadır.
``DECLARE_WAIT_QUEUE_HEAD`` makrosu şöyle tanımlanmıştır:

.. code-block:: c

    #define __WAIT_QUEUE_HEAD_INITIALIZER(name) {                   \
        .lock   = __SPIN_LOCK_UNLOCKED(name.lock),                  \
        .head   = LIST_HEAD_INIT(name.head) }

    #define DECLARE_WAIT_QUEUE_HEAD(name)                           \
        struct wait_queue_head name = __WAIT_QUEUE_HEAD_INITIALIZER(name)

Buradan görüldüğü gibi ``DECLARE_WAIT_QUEUE_HEAD`` makrosu açık bir kilitle boş bir bağlı liste
oluşturmaktadır. ``DECLARE_WAIT_QUEUE_HEAD`` makrosu nesneyi ilk değer vererek tanımlamak için
kullanılmaktadır. Dinamik olarak tahsis edilmiş bekleme kuyruklarına ilk değerlerin verilebilmesi
için ``include/linux/wait.h`` dosyasındaki ``init_waitqueue_head`` makrosu kullanılmaktadır. Bu
makro güncel çekirdeklerde şöyle yazılmıştır:

.. code-block:: c

    #define init_waitqueue_head(wq_head)                            \
        do {                                                        \
            static struct lock_class_key __key;                     \
                                                                    \
            __init_waitqueue_head((wq_head), #wq_head, &__key);     \
        } while (0)

Buradaki ``__init_waitqueue_head`` fonksiyonu ``kernel/sched/wait.c`` dosyası içerisinde aşağıdaki
gibi tanımlanmıştır:

.. code-block:: c

    void __init_waitqueue_head(struct wait_queue_head *wq_head, const char *name,
                               struct lock_class_key *key)
    {
        spin_lock_init(&wq_head->lock);
        lockdep_set_class_and_name(&wq_head->lock, key, name);
        INIT_LIST_HEAD(&wq_head->head);
    }

Görüldüğü gibi burada da spinlock ve bağlı liste ilk durumuna getirilmiştir. Buradaki
``lockdep_set_class_and_name`` fonksiyonu debug amaçlı çağrılmaktadır. Normal bir çekirdek
derlemesinde ``CONFIG_LOCKDEP`` konfigürasyon parametresi 'y' yapılmadığı için zaten önişlemci
tarafından bu çağrı koddan çıkartılmaktadır. Fonksiyon aygıt sürücüler içerisinde şöyle
kullanılabilir:

.. code-block:: c

    static wait_queue_head_t g_wq;
    /* ... */

    init_waitqueue_head(&g_wq);
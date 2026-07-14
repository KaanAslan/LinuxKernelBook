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

Bekleme Kuyruklarına İlişkin Veri Yapıları ve Temel Çekirdek Fonksiyonları
==========================================================================

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
tutan bir bağlı listedir. ``wait_queue_entry`` yapısı şöyle tanımlanmıştır:

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
   :width: 80%

Çekirdek içerisinde thread'i bekleme kuyruklarına bir düğüm olarak yerleştiren ve oradan çıkartarak
yine çalışma kuyruklarına yerleştiren daha yüksek seviyeli çekirdek fonksiyonları oluşturulmuştur.
Bu yüksek seviyeli fonksiyonlar export edildikleri için çekirdek modülleri ve aygıt sürücüler
tarafından kullanılabilmektedir.

Bekleme Kuyruklarının Yaratılması
---------------------------------

Bir bekleme kuyruğunu boş bir biçimde oluşturmak için ``DECLARE_WAIT_QUEUE_HEAD`` makrosu
kullanılmaktadır. Bu makro ``include/linux/wait.h`` dosyası içerisinde tanımlanmıştır. Makroya
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
derlemesinde ``CONFIG_LOCKDEP`` konfigürasyon parametresi ``'y'`` yapılmadığı için zaten önişlemci
tarafından bu çağrı koddan çıkartılmaktadır. Fonksiyon aygıt sürücüler içerisinde şöyle
kullanılabilir:

.. code-block:: c

    static wait_queue_head_t g_wq;
    /* ... */

    init_waitqueue_head(&g_wq);

Thread'lerin Uykuya Yatırılması: wait_event Makroları
-----------------------------------------------------

Bir thread çalışırken kendisini bekleme kuyruğuna yerleştirmektedir. Yani çekirdek tasarımında bir
thread'in başka bir thread'i bekleme kuyruklarına yerleştirmesi gibi bir durum uygun olmadığı
gerekçesiyle doğrudan mümkün hale getirilmemiştir. Yani bir thread "tamam şimdi artık benim uyumam
gerekir" diyerek kendini uyutmaktadır. Thread'in uyandırılması ise tek bir thread'in uyandırılması
biçiminde değil bekleme kuyruğundaki bir grup thread'in uyandırılması biçiminde yapılmaktadır. Yani
uyandırma işlemi aslında thread temelinde değil bekleme kuyruğu temelinde yapılmaktadır. Bu duruma
işletim sistemleri terminolojisinde İngilizce *thundering herd (gürüldeyen sürü)* denilmektedir. Bu
terim bir ahır kapısı açıldığında sürünün gürültülü bir biçimde hep beraber dışarı çıkması
çağrışımından hareketle uydurulmuştur. İzleyen paragraflarda görüleceği gibi *exclusive uyandırma*
denilen bir uyandırma biçimi de vardır. Bu uyandırma biçiminde nispeten daha az sayıda thread
uyandırılmaktadır.

Bir thread'in bekleme kuyruğuna yerleştirilip uykuya yatırılması aşağıdaki çekirdek makroları
tarafından yapılmaktadır:

.. code-block:: c

    wait_event(wq_head, condition);
    wait_event_interruptible(wq_head, condition);
    wait_event_killable(wq_head, condition);
    wait_event_timeout(wq_head, condition, timeout);
    wait_event_interruptible_timeout(wq_head, condition, timeout);
    wait_event_interruptible_exclusive(wq_head, condition);

Bu makroların birinci parametreleri bekleme kuyruğunu temsil eden ``wait_queue_head`` türünden yapı
nesnesini almaktadır. (Makroya nesnenin adresinin değil kendisinin parametre olarak geçirildiğini
vurgulamak istiyoruz. Zaten makro gerektiğinde kendisi adres alma işlemini yapmaktadır.) Makroların
ikinci parametreleri *uyandırma koşulunu* belirtmektedir. Yukarıda da belirttiğimiz gibi aslında,
exclusive özelliğini göz ardı edersek, bekleme kuyruğundaki tüm thread'ler uyandırılmaktadır.
Ancak bu uyandırma sonrasında koşul sağlanmıyorsa uyandırılan thread'ler yeniden uykuya
yatırılmaktadır. Buradaki koşul tipik olarak global değişkenlere dayalı olarak oluşturulmaktadır.
Örneğin ``g_flag`` isminde bir global değişkenimiz olsun. Biz de koşulu ``g_flag != 0`` biçiminde
oluşturabiliriz. Bu durumda ``g_flag`` değişkeni 0 ise biz uyandırma işlemini uygulasak bile
thread'ler önce uyandırılacak, koşul sağlanmadığı için yeniden uykuya dalacaktır. Makroların
``timeout`` parametresine sahip versiyonları koşul sağlanmasa bile en kötü olasılıkla belli bir süre
sonra thread'lerin uyandırılmasını sağlamaktadır. Bekleme kuyruğuna yerleştirilen thread'lerin bir
sinyal geldiğinde uyandırılabilmesi için beklemenin ``interruptible`` biçimde yapılması gerekir.
``killable`` olan bekleme fonksiyonu ise yalnızca ``SIGKILL`` sinyaline yanıt vermektedir.

wait_event Makrolarının Gerçekleştirimleri
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``wait_event`` makrosu güncel çekirdeklerde ``include/linux/wait.h`` dosyası içerisinde aşağıdaki
gibi yazılmıştır:

.. code-block:: c

    #define wait_event(wq_head, condition)              \
    do {                                                \
        might_sleep();                                  \
        if (condition)                                  \
            break;                                      \
        __wait_event(wq_head, condition);               \
    } while (0)

Buradaki ``might_sleep`` makrosu debug amaçlı bulundurulmuştur. Eğer ``CONFIG_DEBUG_ATOMIC_SLEEP``
konfigürasyon parametresi açık değilse bu makro hemen hemen boş gibidir. Burada daha uykuya
yatırmadan koşulun kontrol edildiğine dikkat ediniz. Yani aslında koşul zaten sağlanıyorsa uyuma
gerçekleşmemektedir. Kodda asıl uykuya yatırma işlemini ``__wait_event`` makrosu yapmaktadır. Bu
makro da güncel çekirdeklerde üç alt tireli başka bir makroyu çalıştırmaktadır:

.. code-block:: c

    #define __wait_event(wq_head, condition)                                    \
        (void)___wait_event(wq_head, condition, TASK_UNINTERRUPTIBLE,           \
                            0, 0, schedule())

İşte thread'i bekleme kuyruğuna yerleştiren asıl makro budur:

.. code-block:: c

    #define ___wait_event(wq_head, condition, state, exclusive, ret, cmd)       \
    ({                                                                          \
        __label__ __out;                                                        \
        struct wait_queue_entry __wq_entry;                                     \
        long __ret = ret;   /* explicit shadow */                               \
                                                                                \
        init_wait_entry(&__wq_entry, exclusive ? WQ_FLAG_EXCLUSIVE : 0);        \
        for (;;) {                                                              \
            long __int = prepare_to_wait_event(&wq_head, &__wq_entry, state);   \
                                                                                \
            if (condition)                                                      \
                break;                                                          \
                                                                                \
            if (___wait_is_interruptible(state) && __int) {                     \
                __ret = __int;                                                  \
                goto __out;                                                     \
            }                                                                   \
                                                                                \
            cmd;                                                                \
                                                                                \
            if (condition)                                                      \
                break;                                                          \
        }                                                                       \
        finish_wait(&wq_head, &__wq_entry);                                     \
    __out: __ret;                                                               \
    })

Bekleme işleminin nasıl gerçekleştiğini ve uyanmanın nasıl yapıldığını anlayabilmek için bu makronun
üzerinde biraz durmamız gerekiyor. Makroda bekleme kuyruğunun elemanı olan ``wait_queue_entry``
nesnesinin yerel bir biçimde tanımlandığına dikkat ediniz. Bekleme kuyrukları genellikle global
düzeyde oluşturuluyor olsa da onun düğümleri olan nesneler genellikle yerel biçimde stack'te oluşturulmaktadır.
Bunun bir sakıncası yoktur. Çünkü uyanma durumunda zaten bu stack'teki nesne otomatik biçimde
boşaltılacaktır. Böylece gereksiz bir heap tahsisatı yapılmamaktadır. Stack'te yaratılan yerel
``wait_queue_entry`` nesnesine ilk değer aşağıdaki gibi verilmiştir:

.. code-block:: c

    init_wait_entry(&__wq_entry, exclusive ? WQ_FLAG_EXCLUSIVE : 0);

Burada *exclusive bekleme* kontrol edilmiş ve duruma göre yapının ``flags`` elemanına
``WQ_FLAG_EXCLUSIVE`` bayrağı yerleştirilmiştir. Bu fonksiyon da ``kernel/sched/wait.c`` dosyası
içerisinde şöyle tanımlanmıştır:

.. code-block:: c

    void init_wait_entry(struct wait_queue_entry *wq_entry, int flags)
    {
        wq_entry->flags   = flags;
        wq_entry->private = current;
        wq_entry->func    = autoremove_wake_function;
        INIT_LIST_HEAD(&wq_entry->entry);
    }
    EXPORT_SYMBOL(init_wait_entry);

Oluşturulan ve ilk değer verilen ``wait_queue_entry`` nesnesinin bekleme kuyruğuna yerleştirilmesi
``kernel/sched/wait.c`` dosyasındaki ``prepare_to_wait_event`` fonksiyonu tarafından yapılmaktadır:

.. code-block:: c

    long prepare_to_wait_event(struct wait_queue_head *wq_head,
                               struct wait_queue_entry *wq_entry, int state)
    {
        unsigned long flags;
        long ret = 0;

        spin_lock_irqsave(&wq_head->lock, flags);
        if (signal_pending_state(state, current)) {
            list_del_init(&wq_entry->entry);
            ret = -ERESTARTSYS;
        } else {
            if (list_empty(&wq_entry->entry)) {
                if (wq_entry->flags & WQ_FLAG_EXCLUSIVE)
                    __add_wait_queue_entry_tail(wq_head, wq_entry);
                else
                    __add_wait_queue(wq_head, wq_entry);
            }
            set_current_state(state);
        }
        spin_unlock_irqrestore(&wq_head->lock, flags);

        return ret;
    }
    EXPORT_SYMBOL(prepare_to_wait_event);

Bu fonksiyonun thread'i *çalışma kuyruğundan (run queue)* çıkartmadığına, yalnızca ilgili bekleme
kuyruğuna eklediğine dikkat ediniz. ``__wait_event`` makrosunda ``prepare_to_wait_event`` çağrısından
sonra yeniden koşul kontrol edilmiştir. Çünkü bu arada koşul sağlanmış da olabilir:

.. code-block:: c

    if (condition)
        break;

Buradaki ``break`` akışı döngünün dışına çıkartmaktadır. Bekleme kuyruğundan thread'in çıkartılması
döngünün sonundaki ``finish_wait`` fonksiyonu tarafından yapılmaktadır. Daha sonra ``__wait_event``
makrosunda ``___wait_is_interruptible`` makrosu çağrılıp ``prepare_to_wait_event`` fonksiyonun geri
dönüş değeri kontrol edilmiştir:

.. code-block:: c

    if (___wait_is_interruptible(state) && __int) {
        __ret = __int;
        goto __out;
    }

Şimdi artık thread bekleme kuyruğuna eklenmiştir, ancak henüz çalışma kuyruğundan çıkartılmamıştır
ve thread hâlâ CPU'da çalışmaktadır. İşte son darbe ``schedule`` fonksiyonu tarafından vurulmaktadır.
``schedule`` çağrısı ``__wait_event`` makrosuna ``cmd`` parametresi yoluyla geçilmiştir. Dolayısıyla
``__wait_event`` makrosunun içerisinde bulunan aşağıdaki çağrı aslında ``schedule`` fonksiyonun
çağrılmasını sağlamaktadır:

.. code-block:: c

    cmd;

``schedule`` fonksiyonunu çizelgeleyici alt sistemini incelerken ele alacağız. Ancak bu fonksiyon
kabaca şunları yapmaktadır:

- Çalışmakta olan thread'in yazmaç bilgilerini ``task_struct`` alanına aktarır.
- Gerekiyorsa thread'i çalışma kuyruğundan çıkartır.

İşte thread'in konumunun saklanması ``schedule`` fonksiyonu içerisinde yapılmaktadır. Dolayısıyla
aslında thread uykudan ``schedule`` fonksiyonun içerisinden uyanacaktır. Yani uyandırma gerçekleştiğinde
çalışma aşağıdaki okla gösterilen noktadan devam edecektir:

.. code-block:: c

    #define ___wait_event(wq_head, condition, state, exclusive, ret, cmd)       \
    ({                                                                          \
        __label__ __out;                                                        \
        struct wait_queue_entry __wq_entry;                                     \
        long __ret = ret;   /* explicit shadow */                               \
                                                                                \
        init_wait_entry(&__wq_entry, exclusive ? WQ_FLAG_EXCLUSIVE : 0);        \
        for (;;) {                                                              \
            long __int = prepare_to_wait_event(&wq_head, &__wq_entry, state);   \
                                                                                \
            if (condition)                                                      \
                break;                                                          \
                                                                                \
            if (___wait_is_interruptible(state) && __int) {                     \
                __ret = __int;                                                  \
                goto __out;                                                     \
            }                                                                   \
                                                                                \
            cmd;                                                                \
                                                                                \
    /* -----> uyandırılan thread çalışmasına buradan devam eder! */             \
                                                                                \
            if (condition)                                                      \
                break;                                                          \
        }                                                                       \
        finish_wait(&wq_head, &__wq_entry);                                     \
    __out: __ret;                                                               \
    })

Burada uyanma sonrasında koşulun sağlanıp sağlanmadığına bakılmıştır. Eğer koşul sağlanıyorsa
döngüden çıkılmıştır. Ancak koşul sağlanmıyorsa döngü yine başa saracak ve thread yeniden
uyuyacaktır. Döngüden çıkıldığında ``finish_wait`` fonksiyonunun çağrıldığını görüyorsunuz:

.. code-block:: c

    finish_wait(&wq_head, &__wq_entry);

Bu fonksiyon thread'i bekleme kuyruğundan çıkarmaktadır. Burada bir noktaya dikkat ediniz. İzleyen
paragraflarda ele alacak olduğumuz thread'i uyandıran ``wake_up`` makroları thread'i bekleme
kuyruğundan da çıkarmaktadır. Dolayısıyla yukarıda okla gösterdiğimiz yerden akış devam ettiğinde
thread bekleme kuyruğunda değildir. Tabii koşul sağlanıyorsa zaten bekleme kuyruğunda olmayan
thread'in kuyruktan da çıkartılmaması gerekir. ``finish_wait`` içerisinde bu kontrol uygulanmıştır.
Yani ``finish_wait`` içerisinde eğer thread kuyruktan zaten çıkartılmışsa kuyruktan çıkartma işlemi
yapılmamaktadır.

.. code-block:: c

    void finish_wait(struct wait_queue_head *wq_head, struct wait_queue_entry *wq_entry)
    {
        unsigned long flags;

        __set_current_state(TASK_RUNNING);
        /*
         * We can check for list emptiness outside the lock
         * IFF:
         *  - we use the "careful" check that verifies both
         *    the next and prev pointers, so that there cannot
         *    be any half-pending updates in progress on other
         *    CPU's that we haven't seen yet (and that might
         *    still change the stack area.
         * and
         *  - all other users take the lock (ie we can only
         *    have _one_ other CPU that looks at or modifies
         *    the list).
         */
        if (!list_empty_careful(&wq_entry->entry)) {   /* burada kontrol uygulanmış */
            spin_lock_irqsave(&wq_head->lock, flags);
            list_del_init(&wq_entry->entry);
            spin_unlock_irqrestore(&wq_head->lock, flags);
        }
    }
    EXPORT_SYMBOL(finish_wait);

O halde özetlersek ``wait_event`` fonksiyonu çağrıldığında şunlar gerçekleşmektedir:

1. Daha uykuya yatırma girişiminden önce hemen koşul kontrol edilmektedir.

2. Thread yeni bir düğüm yaratılarak bekleme kuyruğuna eklenmektedir. Ancak henüz bağlamsal geçiş
   yapılmadan koşul yeniden kontrol edilmekte ve sinyal durumu dikkate alınmaktadır.

3. Thread uyandırıldığında zaten uyandıran taraf onu bekleme kuyruğundan çıkarmaktadır.

4. Thread uyandırıldığında koşul sağlanıyorsa artık kesin uyandırılmıştır, sağlanmıyorsa yeniden
   uykuya yatırılmaktadır.

``wait_event_interruptible`` ve ``wait_event_killable`` makroları aslında taban ``___wait_event``
makrosunu çağırmaktadır. Bunlar thread'in durumunu da uygun biçimde ayarlamaktadır.
``wait_event_interruptible`` makrosu ``include/linux/wait.h`` dosyası içerisinde şöyle yazılmıştır:

.. code-block:: c

    #define wait_event_interruptible(wq_head, condition)                    \
    ({                                                                      \
        int __ret = 0;                                                      \
        might_sleep();                                                      \
        if (!(condition))                                                   \
            __ret = __wait_event_interruptible(wq_head, condition);         \
        __ret;                                                              \
    })

Burada ``__wait_event_interruptible`` makrosunun çağrıldığını görüyorsunuz:

.. code-block:: c

    #define __wait_event_interruptible(wq_head, condition)                  \
        ___wait_event(wq_head, condition, TASK_INTERRUPTIBLE, 0, 0,         \
                schedule())

Görüldüğü gibi burada thread'in durumu ``TASK_INTERRUPTIBLE`` yapılmaktadır.

``wait_event_killable`` makrosu da benzer biçimde yazılmıştır:

.. code-block:: c

    #define wait_event_killable(wq_head, condition)                         \
    ({                                                                      \
        int __ret = 0;                                                      \
        might_sleep();                                                      \
        if (!(condition))                                                   \
            __ret = __wait_event_killable(wq_head, condition);              \
        __ret;                                                              \
    })

Burada ``__wait_event_killable`` makrosunun çağrıldığını görüyorsunuz:

.. code-block:: c

    #define __wait_event_killable(wq, condition)                            \
        ___wait_event(wq, condition, TASK_KILLABLE, 0, 0, schedule())

Tek farklı olan yer thread'in durumunun ``TASK_KILLABLE`` olarak set edilmesidir.

``wait_event_timeout`` ve ``wait_event_interruptible_timeout`` makroları *zaman aşımlı (timeout)*
bekleme yapmaktadır. Zaman aşımlı bekleme demek en kötü olasılıkla bloke çözülmese bile belli süre
geçtiğinde beklemenin sonlanması demektir. Bu makroların ayrıca jiffy türünden bir zaman aşımı
parametresine de sahip olduğuna dikkat ediniz:

.. code-block:: c

    wait_event_timeout(wq_head, condition, timeout);
    wait_event_interruptible_timeout(wq_head, condition, timeout);

``wait_event_timeout`` makrosu ``include/linux/wait.h`` dosyası içerisinde şöyle yazılmıştır:

.. code-block:: c

    #define wait_event_timeout(wq_head, condition, timeout)                 \
    ({                                                                      \
        long __ret = timeout;                                               \
        might_sleep();                                                      \
        if (!___wait_cond_timeout(condition))                               \
            __ret = __wait_event_timeout(wq_head, condition, timeout);      \
        __ret;                                                              \
    })

Burada da önce koşulun sağlanıp sağlanmadığına bakılmış, koşul zaten sağlanıyorsa doğrudan
çıkılmıştır. Buradaki ``___wait_cond_timeout`` makrosu da şöyle yazılmıştır:

.. code-block:: c

    #define ___wait_cond_timeout(condition)                 \
    ({                                                      \
        bool __cond = (condition);                          \
        if (__cond && !__ret)                               \
            __ret = 1;                                      \
        __cond || !__ret;                                   \
    })

Burada koşul sağlanıyorsa ya da zaman aşımı sıfırsa makro 1 değerini üretmektedir.
``wait_event_timeout`` makrosunda koşul sağlanmıyorsa ``__wait_event_timeout`` makrosu
çağrılmaktadır. Bu makro da şöyle yazılmıştır:

.. code-block:: c

    #define __wait_event_timeout(wq_head, condition, timeout)           \
        ___wait_event(wq_head, ___wait_cond_timeout(condition),         \
                TASK_UNINTERRUPTIBLE, 0, timeout,                       \
                __ret = schedule_timeout(__ret))

Bu makro da yukarıda incelediğimiz ``___wait_event`` makrosunu çağırmaktadır. Burada
``___wait_event`` makrosunun parametrelerinin daha değişik geçildiğine dikkat ediniz. Örneğin artık
``schedule`` fonksiyonu yerine ``schedule_timeout`` fonksiyonu çağrılmaktadır. Ayrıca makroda koşulun
``___wait_cond_timeout(condition)`` biçiminde oluşturulduğuna da dikkat ediniz. Böylece aslında
uyandırılan thread koşul sağlanıyorsa ya da koşul sağlanmıyorsa fakat zaman aşımı dolmuşsa yeniden
uykuya dalmayacak, akışına devam edecektir. Burada kritik önemdeki fonksiyon ``schedule_timeout``
fonksiyonudur. Bu fonksiyon ``kernel/time/sleep_timeout.c`` dosyasında şöyle yazılmıştır:

.. code-block:: c

    signed long __sched schedule_timeout(signed long timeout)
    {
        struct process_timer timer;
        unsigned long expire;

        switch (timeout) {
        case MAX_SCHEDULE_TIMEOUT:
            /*
             * These two special cases are useful to be comfortable
             * in the caller. Nothing more. We could take
             * MAX_SCHEDULE_TIMEOUT from one of the negative value
             * but I'd like to return a valid offset (>=0) to allow
             * the caller to do everything it want with the retval.
             */
            schedule();
            goto out;
        default:
            /*
             * Another bit of PARANOID. Note that the retval will be
             * 0 since no piece of kernel is supposed to do a check
             * for a negative retval of schedule_timeout() (since it
             * should never happens anyway). You just have the printk()
             * that will tell you if something is gone wrong and where.
             */
            if (timeout < 0) {
                pr_err("%s: wrong timeout value %lx\n", __func__, timeout);
                dump_stack();
                __set_current_state(TASK_RUNNING);
                goto out;
            }
        }

        expire = timeout + jiffies;

        timer.task = current;
        timer_setup_on_stack(&timer.timer, process_timeout, 0);
        timer.timer.expires = expire;
        add_timer(&timer.timer);
        schedule();
        timer_delete_sync(&timer.timer);

        /* Remove the timer from the object tracker */
        timer_destroy_on_stack(&timer.timer);

        timeout = expire - jiffies;

    out:
        return timeout < 0 ? 0 : timeout;
    }
    EXPORT_SYMBOL(schedule_timeout);

Burada neler yapılmaktadır? Aslında fonksiyonun ana noktası şudur: fonksiyon ``schedule``
fonksiyonu ile bağlamsal geçişi oluşturmadan önce bir zamanlayıcı kurar. Bu zamanlayıcının süresi
dolduğunda thread uyandırılır. Yani sonuçta ``wait_event_timeout`` makrosu ile uykuya yatırılan
thread başka bir akış tarafından uyandırılmasa bile bu timer mekanizması yoluyla uyandırılmaktadır.

``wait_event_timeout`` makrosu kalan ``jiffy`` süresine geri dönmektedir. Jiffy konusu ileride ele
alınacaktır.

``wait_event_timeout`` fonksiyonu özetle aşağıdaki gibi çalışmaktadır:

1. Daha uykuya yatırma girişiminden önce koşul ve zaman aşımı kontrol edilmektedir. Koşul
   sağlanıyorsa ya da zaman aşımı zaten dolmuş durumdaysa (yani zaman aşımı parametresi 0
   girilmişse) hiç uyuma girişiminde bulunulmaz.

2. Thread bekleme kuyruğuna yazılır ancak bekleme bir timer kurularak sağlanır. Dolayısıyla blokenin
   çözülmesi için zaman aşımının dolması ya da uyandırıldığında koşulun sağlanması gerekmektedir.

3. Eğer thread uyandırılırsa yine koşula ve zaman aşımına bakılır. Koşul sağlanıyorsa ya da zaman
   aşımı dolmuşsa thread bekleme kuyruğundan çıkartılarak bloke çözülür.

``wait_event_interruptible_timeout`` makrosunun ``wait_event_timeout`` makrosundan farkı bir sinyal
oluştuğunda da blokenin çözülmesidir. Makro şöyle yazılmıştır:

.. code-block:: c

    #define wait_event_interruptible_timeout(wq_head, condition, timeout)       \
    ({                                                                          \
        long __ret = timeout;                                                   \
        might_sleep();                                                          \
        if (!___wait_cond_timeout(condition))                                   \
            __ret = __wait_event_interruptible_timeout(wq_head,                 \
                            condition, timeout);                                \
        __ret;                                                                  \
    })

``__wait_event_interruptible_timeout`` makrosu da şöyle yazılmıştır:

.. code-block:: c

    #define __wait_event_interruptible_timeout(wq_head, condition, timeout)     \
        ___wait_event(wq_head, ___wait_cond_timeout(condition),                 \
                TASK_INTERRUPTIBLE, 0, timeout,                                 \
                __ret = schedule_timeout(__ret))

Buradaki tek farkın thread'in durumunun ``TASK_INTERRUPTIBLE`` olarak set edilmesi olduğuna dikkat
ediniz.

Şimdi de ``wait_event_interruptible_exclusive`` makrosu üzerinde duralım.
``wait_event_interruptible_exclusive`` makrosu bekleme kuyruğuna yerleştirilen ``wait_queue_entry``
nesnesinin ``flags`` elemanını exclusive durumu belirtmek amacıyla ``WQ_FLAG_EXCLUSIVE`` biçiminde
set etmektedir. Makro ``include/linux/wait.h`` dosyası içerisinde şöyle yazılmıştır:

.. code-block:: c

    #define wait_event_interruptible_exclusive(wq, condition)                   \
    ({                                                                          \
        int __ret = 0;                                                          \
        might_sleep();                                                          \
        if (!(condition))                                                       \
            __ret = __wait_event_interruptible_exclusive(wq, condition);        \
        __ret;                                                                  \
    })

Buradaki ``__wait_event_interruptible_exclusive`` makrosu da şöyle yazılmıştır:

.. code-block:: c

    #define __wait_event_interruptible_exclusive(wq, condition)                \
        ___wait_event(wq, condition, TASK_INTERRUPTIBLE, 1, 0,                 \
                schedule())

Burada ``___wait_event`` makrosunun dördüncü parametresine 1 geçildiğine dikkat ediniz. Bu parametre
makroda kontrol edilmekte ve bu parametreye dayalı olarak exclusive bekleme için ``wait_queue_entry``
nesnesinin ``flags`` elemanı ``WQ_FLAG_EXCLUSIVE`` biçiminde set edilmektedir.

Exclusive uyuma ve uyandırma izleyen paragraflarda ele alacağız.

Şimdi thread'lerin uykuya yatırılmasına bir örnek verelim. Bir aygıt sürücü içerisinde bir tampondan
bilgi okuyacak olalım. Ancak tamponda bilgi yoksa okuma yapan thread bilgi tampona gelene kadar
uykuya yatırılarak bekletilecek olsun. Aygıt sürücümüzün ``read`` fonksiyonunu şöyle yazabiliriz:

.. code-block:: c

    static wait_queue_head_t g_wq;
    static char g_buf[1024];
    atomic_t g_len = ATOMIC_INIT(0);
    /* ... */

    static ssize_t generic_read(struct file *filp, char *buf, size_t size, loff_t *off)
    {
        size_t esize;

        if (wait_event_interruptible(g_wq, atomic_read(&g_len) > 0) != 0)
            return -ERESTARTSYS;   

        esize = size < atomic_read(&g_len) ? size : atomic_read(&g_len);
        if (copy_to_user(buf, g_buf, esize) != 0)
            return -EFAULT;

        return esize;
    }

Buradaki koşula dikkat ediniz: ``atomic_read(&g_len) > 0``. Tampona yazma yapan taraf yazma
yaptıktan sonra yazılan karakter sayısını ``g_len`` değişkenine yerleştirdikten sonra uyandırma
işlemini yapmalıdır. Böylece uyandırılan thread koşulun sağlandığını görecek ve bloke çözülecektir.
Bloke çözülünce de tampondaki bilgi kullanıcı alanına ``copy_to_user`` fonksiyonu ile
kopyalanmaktadır. Ancak burada dikkat edilmesi gereken bir nokta vardır. Birden fazla thread ``read``
fonksiyonunu çağırıp bloke olduğunda bunların hepsi uyanacak ve aynı tamponu okuyacaktır. Eğer bu
tamponun tek bir thread tarafından okunup tüketilmesini istiyorsanız ek bir kilit kullanarak başka
bir döngü içerisinde bu işlemi yapmalısınız. Kodda koşulun atomik bir biçimde oluşturulduğuna da
dikkat ediniz. Aslında pek çok durumda ``atomic_read`` yerine ``READ_ONCE`` gibi volatile erişim
yeterli olmaktadır. Ancak eğer birden fazla thread uyandırılıyorsa güvenli olan yaklaşım koşulun
atomik bir biçimde oluşturulmasıdır.

Burada bir noktaya daha dikkatinizi çekmek istiyoruz. wait_event_interruptible makrosu sinyal dolayısıyla 
başarısız olabilir. Bu durumda sistem fonksiyonlarının yeniden çalıştırılabilirliğini sağlamak için 
onun çağrıldığı fonksiyonu -ERESTARTSYS errno değeri ile geri döndürmek gerekir:

.. code-block:: c

    if (wait_event_interruptible(g_wq, atomic_read(&g_len) > 0) != 0)
        return -ERESTARTSYS;   

Thread'lerin Uykudan Uyandırılması: wake_up Makroları
-----------------------------------------------------

Şimdi de bekleme kuyruğundaki thread'lerin nasıl uyandırıldığı üzerinde duralım. Bunun için Linux
çekirdeklerinde ``include/linux/wait.h`` dosyası içerisinde bir grup ``wake_up`` makrosu
bulundurulmuştur:

.. code-block:: c

    #define wake_up(x)                          __wake_up(x, TASK_NORMAL, 1, NULL)
    #define wake_up_nr(x, nr)                   __wake_up(x, TASK_NORMAL, nr, NULL)
    #define wake_up_all(x)                      __wake_up(x, TASK_NORMAL, 0, NULL)
    #define wake_up_locked(x)                   __wake_up_locked((x), TASK_NORMAL, 1)
    #define wake_up_all_locked(x)               __wake_up_locked((x), TASK_NORMAL, 0)
    #define wake_up_sync(x)                     __wake_up_sync(x, TASK_NORMAL)

    #define wake_up_interruptible(x)            __wake_up(x, TASK_INTERRUPTIBLE, 1, NULL)
    #define wake_up_interruptible_nr(x, nr)     __wake_up(x, TASK_INTERRUPTIBLE, nr, NULL)
    #define wake_up_interruptible_all(x)        __wake_up(x, TASK_INTERRUPTIBLE, 0, NULL)
    #define wake_up_interruptible_sync(x)       __wake_up_sync((x), TASK_INTERRUPTIBLE)

Bu makroların hepsinin birinci parametreleri ``wait_queue_head`` türünden bekleme kuyruğu nesnesinin
adresini almaktadır. (``wait_event`` makrolarında adres alma işlemi makro tarafından yapılmaktadır.
Ancak ``wake_up`` makroları adres istemektedir.) Bunların ``_nr``'li versiyonlarının da olduğunu
görüyorsunuz.

wakeup Makrolarının Gerçekleştirimleri
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``wake_up`` makrolarının çoğunun ortak bir biçimde aslında ``__wake_up`` fonksiyonunu çağırdığına
dikkat ediniz. ``__wake_up`` fonksiyonu ``kernel/sched/wait.c`` dosyası içerisinde şöyle
yazılmıştır:

.. code-block:: c

    int __wake_up(struct wait_queue_head *wq_head, unsigned int mode,
                  int nr_exclusive, void *key)
    {
        return __wake_up_common_lock(wq_head, mode, nr_exclusive, 0, key);
    }
    EXPORT_SYMBOL(__wake_up);

Bu fonksiyonun da ortak bir biçimde ``__wake_up_common_lock`` isimli fonksiyonu çağırdığını
görüyorsunuz. Bu fonksiyon da şöyle yazılmıştır:

.. code-block:: c

    static int __wake_up_common_lock(struct wait_queue_head *wq_head, unsigned int mode,
                int nr_exclusive, int wake_flags, void *key)
    {
        unsigned long flags;
        int remaining;

        spin_lock_irqsave(&wq_head->lock, flags);
        remaining = __wake_up_common(wq_head, mode, nr_exclusive, wake_flags, key);
        spin_unlock_irqrestore(&wq_head->lock, flags);

        return nr_exclusive - remaining;
    }

Bu fonksiyon da ``__wake_up_common`` fonksiyonunu çağırmaktadır. İşte asıl işlemler bu
``__wake_up_common`` fonksiyonu içerisinde yapılmaktadır:

.. code-block:: c

    static int __wake_up_common(struct wait_queue_head *wq_head, unsigned int mode,
                int nr_exclusive, int wake_flags, void *key)
    {
        wait_queue_entry_t *curr, *next;

        lockdep_assert_held(&wq_head->lock);

        curr = list_first_entry(&wq_head->head, wait_queue_entry_t, entry);

        if (&curr->entry == &wq_head->head)
            return nr_exclusive;

        list_for_each_entry_safe_from(curr, next, &wq_head->head, entry) {
            unsigned flags = curr->flags;
            int ret;

            ret = curr->func(curr, mode, wake_flags, key);
            if (ret < 0)
                break;
            if (ret && (flags & WQ_FLAG_EXCLUSIVE) && !--nr_exclusive)
                break;
        }

        return nr_exclusive;
    }

Bu fonksiyonda şunlar yapılmaktadır:

1. Önce bekleme kuyruğuna ilişkin bağlı listenin ilk düğümü elde edilmiştir:

.. code-block:: c

    curr = list_first_entry(&wq_head->head, wait_queue_entry_t, entry);

2. Eğer kuyruk boşsa yapacak bir şey yoktur ve hemen geri dönülmüştür:

.. code-block:: c

    if (&curr->entry == &wq_head->head)
        return nr_exclusive;

3. Eğer kuyruk boş değilse kuyruk dolaşılmış ve ``wait_queue_entry`` yapısı içerisindeki uyandırma
yapan ``func`` isimli elemandaki callback fonksiyon çağrılmıştır:

.. code-block:: c

    list_for_each_entry_safe_from(curr, next, &wq_head->head, entry) {
        unsigned flags = curr->flags;
        int ret;

        ret = curr->func(curr, mode, wake_flags, key);
        if (ret < 0)
            break;
        if (ret && (flags & WQ_FLAG_EXCLUSIVE) && !--nr_exclusive)
            break;
    }

Yani burada bağlı listedeki thread'ler uyandırılmaktadır. Ancak exclusive beklemeye ilişkin bir
ayrıntı da ele alınmıştır.

Bekleme kuyruklarında bazı thread'ler ``wait_event`` fonksiyonlarının exclusive versiyonlarıyla
kuyruğa yerleştirilmiş olabilir. Örneğin:

.. code-block:: none

    T1 ---> T2 ---> T3 ---> T4(E) ---> T5 ---> T6(E) ---> T7 ---> T8(E) ---> NULL

Burada exclusive bekleyen thread'ler (E) ile belirtilmiştir. Bir thread'in exclusive bekleyip
beklemediği yukarıda da belirttiğimiz gibi ``wait_queue_entry`` yapısının ``flags`` elemanından
anlaşılmaktadır. İşte ``wake_up`` makrolarının ``_nr``'li biçimleri (yani ``wake_up_nr`` ve
``wake_up_interruptible_nr``) belli sayıda exclusive thread'i uyandırmak için kullanılmaktadır.
Örneğin biz uyandırmayı ``wake_up_nr(g_wq, 2)`` çağrısı ile yapalım. Bu durumda bu makro çağrısı
2 tane exclusive thread'i uyandırmak amacındadır. Ancak bu ``_nr``'li makrolar bağlı listenin
başından itibaren 2 tane exclusive uyandırma yapana kadar exclusive bekleme yapmayanları da
uyandırmaktadır. Yukarıdaki kuyrukta ``wake_up_nr(g_wq, 2)`` çağrısını yaptığımızda yalnızca T4
ve T6 thread'leri uyandırılmayacak; T1, T2, T3, T4, T5, T6 thread'leri uyandırılacaktır. Yani
n tane exclusive thread'in uyandırılması şöyle yapılmaktadır: "listenin başından başla, n tane
exclusive uyandırma yapana kadar hepsini uyandırarak ilerle".

Bu bilgi eşliğinde yukarıdaki bağlı listenin dolaşılması kodu şimdi size daha anlamlı gelecektir.
Dolaşım yapan döngünün içerisindeki ``if`` deyimine dikkat ediniz:

.. code-block:: c

    if (ret && (flags & WQ_FLAG_EXCLUSIVE) && !--nr_exclusive)
        break;

Burada aslında yukarıda açıkladığımız işlem yapılmaktadır. Yani her exclusive thread uyandırıldığında
``nr_exclusive`` değişkeni 1 eksiltilmekte ve bu değişken 0'a geldiğinde döngü sonlandırılmaktadır.

Thread'i bekleme kuyruğundan çıkartarak uyandıran ``curr->func(curr, mode, wake_flags, key)``
çağrısındaki callback fonksiyon ``kernel/sched/wait.c`` dosyası içerisinde şöyle tanımlanmıştır:

.. code-block:: c

    int autoremove_wake_function(struct wait_queue_entry *wq_entry, unsigned mode, int sync, void *key)
    {
        int ret = default_wake_function(wq_entry, mode, sync, key);

        if (ret)
            list_del_init_careful(&wq_entry->entry);

        return ret;
    }
    EXPORT_SYMBOL(autoremove_wake_function);

Burada önce ``default_wake_function`` isimli fonksiyon çağrılmış sonra da thread'e ilişkin
``wait_queue_entry`` nesnesi bağlı listeden çıkartılmıştır.

``wake_up`` makrosuyla ``wake_up_nr`` makrosu arasındaki farka dikkat ediniz:

.. code-block:: c

    #define wake_up(x)              __wake_up(x, TASK_NORMAL, 1, NULL)
    #define wake_up_nr(x, nr)       __wake_up(x, TASK_NORMAL, nr, NULL)

Bunlar aynı fonksiyonu çağırmaktadır. Ancak ``__wake_up`` fonksiyonunun ``nr_exclusive``
parametresine ``wake_up`` fonksiyonu 1 değerini geçirirken ``wake_up_nr`` fonksiyonu ``nr``
değerini geçirmektedir. ``nr_exclusive`` parametresinin *en az kaç exclusive bekleyen thread'i
uyandırana kadar kuyruktakileri uyandırmaya devam edeyim?* anlamına geldiğini yukarıda
açıklamıştık. O halde ``wake_up`` makrosu işlemini ilk exclusive bekleyen thread'i uyandırdığında
sonlandırmaktadır. ``wake_up_nr`` makrosu ise ``nr`` tane exclusive thread'i uyandırdığında
işlemini sonlandırmaktadır. İşte ``wake_up_all`` makrosu da *kuyruktaki bütün thread'leri uyandır*
anlamına gelmektedir. Bu makro ``__wake_up`` fonksiyonunu şöyle çağırmaktadır:

.. code-block:: c

    #define wake_up_all(x)          __wake_up(x, TASK_NORMAL, 0, NULL)

Burada fonksiyonun ``nr_exclusive`` parametresine 0 geçildiğine dikkat ediniz. Fonksiyonun kodunu
dikkatle incelerseniz bu parametre 0 geçildiğinde tüm thread'lerin uyandırıldığını görebilirsiniz:

.. code-block:: c

    /* ... */

    if (ret && (flags & WQ_FLAG_EXCLUSIVE) && !--nr_exclusive)
        break;

    /* ... */

Burada ``nr_exclusive`` değeri 0 ise eksiltmeyle en büyük pozitif değer haline gelecek ve döngü
çalışmaya devam edecektir.

Eğer kuyrukta hiç exclusive bekleme yapan thread yoksa ``wake_up``, ``wake_up_nr`` ve
``wake_up_all`` çağrıları arasında işlevsel bir fark kalmamaktadır.

``wake_up`` makrolarının ``locked`` ekli iki biçimi de vardır:

.. code-block:: c

    #define wake_up_locked(x)           __wake_up_locked((x), TASK_NORMAL, 1)
    #define wake_up_all_locked(x)       __wake_up_locked((x), TASK_NORMAL, 0)

Bu ``locked`` ekli biçimler bekleme kuyruğundaki spinlock nesnesinin kilidini almadan uyandırma
işlemini yapmaktadır. Çünkü bazı durumlarda kilit zaten alınmış olabilir. Bu durumda kilidin
alınmadan işleme devam edilmesi gerekir. (Aksi takdirde *kilitlenme (deadlock)* durumu
oluşabilecektir.) ``wake_up_locked`` fonksiyonu ``nr_exclusive`` parametresine 1 geçilerek,
``wake_up_all_locked`` fonksiyonu ise 0 geçilerek çağrılmaktadır. Dolayısıyla ``wake_up_locked``
tek bir exclusive bekleme yapan thread'i uyandırdıktan sonra, ``wake_up_all_locked`` ise tüm
thread'leri uyandırdıktan sonra işlemini sonlandırmaktadır.

``wake_up_sync`` makrosu uyandırma işlemi sırasında uyandırılan thread'in bu uyandırmayı yapan
thread'i CPU'dan koparmasını engellemektedir. (Uyandırılan thread'ler eğer yüksek bir önceliğe sahipse hemen 
kopararak (preemption'a yol açarak) CPU'ya atanabilmektedir. Bu makro bunu engellemektedir.) Makro
şöyle yazılmıştır:

.. code-block:: c

    #define wake_up_sync(x)      __wake_up_sync(x, TASK_NORMAL)

Buradaki ``__wake_up_sync`` fonksiyonu da şöyle yazılmıştır:

.. code-block:: c

    void __wake_up_sync(struct wait_queue_head *wq_head, unsigned int mode)
    {
        __wake_up_sync_key(wq_head, mode, NULL);
    }
    EXPORT_SYMBOL_GPL(__wake_up_sync);  /* For internal use only */

Bu fonksiyon da ortak ``__wake_up_common_lock`` fonksiyonunu çağırmaktadır:

.. code-block:: c

    void __wake_up_sync_key(struct wait_queue_head *wq_head, unsigned int mode, void *key)
    {
        if (unlikely(!wq_head))
            return;

        __wake_up_common_lock(wq_head, mode, 1, WF_SYNC, key);
    }
    EXPORT_SYMBOL_GPL(__wake_up_sync_key);

Tabii ``locked`` uyandırmalarda zaten spinlock kilidi alındığı için ve bu spinlock da *koparma (preemption)*
mekanizmasını kapattığı için uyandırma işlemi zaten kesilmeyecektir. Ancak uyandırılan thread başka
bir CPU'nun kuyruğunda da olabilir.

``wake_up`` makrolarının da interruptible biçimleri vardır:

.. code-block:: c

    #define wake_up_interruptible(x)            __wake_up(x, TASK_INTERRUPTIBLE, 1, NULL)
    #define wake_up_interruptible_nr(x, nr)     __wake_up(x, TASK_INTERRUPTIBLE, nr, NULL)
    #define wake_up_interruptible_all(x)        __wake_up(x, TASK_INTERRUPTIBLE, 0, NULL)
    #define wake_up_interruptible_sync(x)       __wake_up_sync((x), TASK_INTERRUPTIBLE)

Bu makrolar aslında ``__wake_up`` ve ``__wake_up_sync`` fonksiyonlarını ``TASK_INTERRUPTIBLE``
thread durum argümanıyla çağırmaktadır. Thread'in durumunu belirten ``TASK_XXX`` bayraklarını
çizelgeleyiciyi anlattığımız bölümde ele alacağız. interruptible ``wake_up`` makrolarının
diğerlerinden tek farkı thread durum bilgisi yalnızca ``TASK_INTERRUPTIBLE`` olanları
uyandırmasıdır. Halbuki interruptible olmayan ``wake_up`` makroları hem ``TASK_UNINTERRUPTIBLE``
hem de ``TASK_INTERRUPTIBLE`` durumuna ilişkin thread'leri uyandırmaktadır. Normal olarak bir
thread uykuya interruptible olan ``wait_event`` makrolarıyla yatırılmışsa uyandırılmasının da
interruptible ``wake_up`` fonksiyonlarıyla yapılması uygun olur. Çünkü bu durumda eğer bekleme
kuyruğunda ``TASK_UNINTERRUPTIBLE`` thread'ler varsa onlar uyandırılmayacaktır. interruptible
olarak uyutulan thread'lerin interruptible olmayan ``wake_up`` makrolarıyla uyandırılmasında bir
sorun oluşmaz ancak amaç dikkate alındığında gereksiz uyandırmalar da yapılacaktır.

Bekleme Kuyruklarına İlişkin Yalın Bir Örnek
--------------------------------------------

Şimdi de thread'lerin uyutulması ve uyandırılması işlemine bir aygıt sürücü yoluyla basit bir örnek
verelim. Aygıt sürücümüzde bir tampon olsun. Eğer bu tampon boşsa ``read`` işlemini yapan thread
uykuda bekletilsin. Bu tampona ``write`` fonksiyonu ile yazma yapan thread uyuyan thread'leri
uyandırsın. Böyle bir aygıt sürücünün ``read`` fonksiyonu şöyle yazılabilir:

.. code-block:: c

    static wait_queue_head_t g_wq;
    static char g_buf[TEXT_BUFFER_SIZE];
    static atomic_t g_len = ATOMIC_INIT(0);
    /* ... */

    static ssize_t generic_read(struct file *filp, char *buf, size_t size, loff_t *off)
    {
        size_t esize;

        if (wait_event_interruptible(g_wq, atomic_read(&g_len) > 0) != 0)
            return -ERESTARTSYS;   

        esize = size < atomic_read(&g_len) ? size : atomic_read(&g_len);
        if (copy_to_user(buf, g_buf, esize) != 0)
            return -EFAULT;
        atomic_set(&g_len, 0);

        return esize;
    }

Burada interruptible biçimde bloke oluşturulmuştur. Blokenin çözülme koşulu ``g_len > 0``
biçimindedir. İşin başında ``g_len = 0`` olduğu için ``read`` fonksiyonunda bloke oluşacaktır.
Bloke çözüldüğünde okunmak istenen miktarla tampondaki miktar karşılaştırılmış, bunlardan hangisi
küçükse o miktarda okuma yapılmıştır. ``copy_to_user`` fonksiyonunun çekirdek modundan prosesin
bellek alanına kopyalama yaptığını anımsayınız. Aktarım sonrasında ``g_len`` değişkeni yine 0
değerine çekilmiştir. Böylece sonraki ``read`` işleminde tampon tüketildiği için yeniden bloke
oluşacaktır. Ancak bu kod birden fazla ``read`` işleminin aynı anda yapıldığı durumda ya da read 
işlemi ile write işleminin eşzamanlı yapıldığı durumda senkronizasyon sorununa yol açabilecektir. 
Eğer tamponun tek bir thread tarafından tüketilmesi fakat diğer thread'lerin bekletilmesi gerekiyorsa 
``mutex`` gibi (``spinlock`` da olabilir) ek bir kilit mekanizmasının da kullanılması gerekir. İzleyen
paragraflarda bu sorunun üzerinde duracağız.

Aygıt sürücünün ``read`` fonksiyonunda bloke olan thread'lerin blokesi aygıt sürücünün ``write``
fonksiyonunda çözülmektedir:

.. code-block:: c

    static ssize_t generic_write(struct file *filp, const char *buf, size_t size, loff_t *off)
    {
        size_t esize;

        esize = size < TEXT_BUFFER_SIZE ? size : TEXT_BUFFER_SIZE;

        if (copy_from_user(g_buf, buf, esize) != 0)
            return -EFAULT;

        atomic_set(&g_len, esize);
        wake_up_interruptible(&g_wq);

        return esize;
    }

Burada önce tampona yazma yapılmış daha sonra tamponu bekleyen thread'ler
``wake_up_interruptible`` makrosuyla uyandırılmıştır. Uyandırma işleminden önce koşulun
sağlanması gerektiğine dikkat ediniz. Bu nedenle örneğimizde önce ``g_len`` değişkenine atama
yapılıp sonra uyandırma işlemi yapılmıştır.

Aygıt sürücünün kodlarını bütünsel biçimde aşağıda veriyoruz. Derleme işlemini şöyle yapabilirsiniz:

.. code-block:: c

    $ make file=wait-driver

Aşağıdaki gibi yükleyebilirsiniz:

.. code-block:: c

    $ sudo ./load wait-driver

Farklı terminallerden önce ``wait-driver-test-read.c`` programını sonra da ``wait-driver-test-rwrite.c`` programını 
çalıştırıp durumu gözlemleyebilirsiniz:

.. code-block:: c

    $ ./wait-driver-test-read

.. code-block:: c

    $ ./wait-driver-test-write
 
Test bitince aygıt sürücüyü çekirdekten şöyle çıkartabilirsiniz:

.. code-block:: c

     $ sudo ./unload wait-driver

``wait-driver.c``

.. code-block:: c

    #include <linux/module.h>
    #include <linux/kernel.h>
    #include <linux/fs.h>
    #include <linux/cdev.h>
    #include <linux/wait.h>

    MODULE_LICENSE("GPL");
    MODULE_AUTHOR("Kaan Aslan");
    MODULE_DESCRIPTION("Wait-Driver");

    static int generic_open(struct inode *inodep, struct file *filp);
    static int generic_release(struct inode *inodep, struct file *filp);
    static ssize_t generic_read(struct file *filp, char *buf, size_t size, loff_t *off);
    static ssize_t generic_write(struct file *filp, const char *buf, size_t size, loff_t *off);

    static dev_t g_dev;
    static struct cdev *g_cdev;
    static struct file_operations g_fops = {
        .owner = THIS_MODULE,
        .open = generic_open,
        .read = generic_read,
        .write = generic_write,
        .release = generic_release
    };

    #define TEXT_BUFFER_SIZE    4096

    static wait_queue_head_t g_wq;
    static char g_buf[TEXT_BUFFER_SIZE];
    static atomic_t g_len = ATOMIC_INIT(0);

    static int __init generic_init(void)
    {
        int result;

        printk(KERN_INFO "wait-driver module initialization...\n");

        if ((result = alloc_chrdev_region(&g_dev, 0, 1, "wait-driver")) < 0) {
            printk(KERN_INFO "cannot alloc char driver!...\n");
            return result;
        }

        if ((g_cdev = cdev_alloc()) == NULL) {
            printk(KERN_INFO "cannot allocate cdev!...\n");
            return -ENOMEM;
        }

        g_cdev->owner = THIS_MODULE;
        g_cdev->ops = &g_fops;

        if ((result = cdev_add(g_cdev, g_dev, 1)) < 0) {
            unregister_chrdev_region(g_dev, 1);
            printk(KERN_ERR "cannot add device!...\n");
            return result;
        }

        init_waitqueue_head(&g_wq);

        return 0;
    }

    static void __exit generic_exit(void)
    {
        cdev_del(g_cdev);
        unregister_chrdev_region(g_dev, 1);

        printk(KERN_INFO "wait-driver module exit...\n");
    }

    static int generic_open(struct inode *inodep, struct file *filp)
    {
        printk(KERN_INFO "wait-driver opened...\n");

        return 0;
    }

    static int generic_release(struct inode *inodep, struct file *filp)
    {
        printk(KERN_INFO "wait-driver closed...\n");

        return 0;
    }

    static ssize_t generic_read(struct file *filp, char *buf, size_t size, loff_t *off)
    {
        size_t esize;

        if (wait_event_interruptible(g_wq, atomic_read(&g_len) > 0) != 0)
            return -ERESTARTSYS;   

        esize = size < atomic_read(&g_len) ? size : atomic_read(&g_len);
        if (copy_to_user(buf, g_buf, esize) != 0)
            return -EFAULT;
        atomic_set(&g_len, 0);

        return esize;
    }

    static ssize_t generic_write(struct file *filp, const char *buf, size_t size, loff_t *off)
    {
        size_t esize;

        esize = size < TEXT_BUFFER_SIZE ? size : TEXT_BUFFER_SIZE;

        if (copy_from_user(g_buf, buf, esize) != 0)
            return -EFAULT;

        atomic_set(&g_len, esize);
        wake_up_interruptible(&g_wq);

        return esize;
    }

    module_init(generic_init);
    module_exit(generic_exit);

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

``wait-driver-test-read.c``

.. code-block:: c

    #include <stdio.h>
    #include <stdlib.h>
    #include <fcntl.h>
    #include <unistd.h>

    void exit_sys(const char *msg);

    int main(void)
    {
        int fd;
        char buf[4096];
        ssize_t result;

        if ((fd = open("wait-driver", O_RDONLY)) == -1)
            exit_sys("open");

        printf("Buffer empty, thread is sleeping...\n");

        if ((result = read(fd, buf, 10)) == -1)
            exit_sys("read");
        buf[result] = '\0';

        printf("%s\n", buf);

        close(fd);

        return 0;
    }

    void exit_sys(const char *msg)
    {
        perror(msg);
        exit(EXIT_FAILURE);
    }

``wait-driver-test-write.c``

.. code-block:: c

    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <fcntl.h>
    #include <unistd.h>

    #define TEXT_BUFFER_SIZE    4096

    void exit_sys(const char *msg);

    int main(void)
    {
        int fd;
        char buf[TEXT_BUFFER_SIZE];
        char *str;
        ssize_t result;

        if ((fd = open("wait-driver", O_WRONLY)) == -1)
            exit_sys("open");

        printf("Enter text:");
        fgets(buf, TEXT_BUFFER_SIZE, stdin);
        if ((str = strchr(buf, '\n')) != NULL)
            *str = '\0';

        if (write(fd, buf, strlen(buf)) == -1)
            exit_sys("write");

        close(fd);

        return 0;
    }

    void exit_sys(const char *msg)
    {
        perror(msg);
        exit(EXIT_FAILURE);
    }

Yalnızca Tek Bir Thread'in Uyandırılması
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bekleme kuyruğunda bir koşul altında birden fazla thread'in bloke edildiğini düşünelim. Örneğin
thread'ler şöyle uykuya yatırılmış olsun:

.. code-block:: c

    if (wait_event_interruptible(g_wq, atomic_read(&g_len) > 0) != 0)
        return -ERESTARTSYS;

Buradaki koşul ``g_flag`` değerinin 0'a eşit olmamasıdır. Biz ``g_flag`` değerini örneğin 1 yapıp
``wake_up_interruptible`` makrosunu çağırırsak bu koşulu bekleyen birden fazla thread
uyanabilecektir:

.. code-block:: c

    atomic_set(&g_flag, 1);
    wake_up_interruptible(&g_wq);

Ancak bazen programcı "tek bir thread'in uyanmasını, diğer thread'lerin uyumaya devam etmesini"
isteyebilir. İşte bu tür durumlarda sistem programcısının bir döngü içerisinde bu durumu manuel
biçimde sağlaması gerekir. Bunu yapabilen tipik kalıp şöyledir:

.. code-block:: c

    if (mutex_lock_interruptible(&g_mutex) != 0)
        return -ERESTARTSYS;
    while (g_flag == 0) {
        mutex_unlock(&g_mutex);
        if (wait_event_interruptible(g_wq, g_flag != 0) != 0)
            return -ERESTARTSYS;
        if (mutex_lock_interruptible(&g_mutex) != 0)
            return -ERESTARTSYS;
    }
    g_flag = 0;
    mutex_unlock(&g_mutex);

    /* burada uyanınca yapılacak işlemler var */

Aslında bu kalıba kullanıcı modundaki *koşul değişkenleri (condition variable)* konusundan da
aşinasınızdır. Burada önce ``mutex`` kilitlenmiş ve ``while`` döngüsüne girilmiştir. ``while``
döngüsündeki koşula dikkat ediniz. Artık bu koşul sağlanmadığı sürece uyanan thread zaten yeniden
uykuya dalacaktır. Uyanan thread'ler aşağıda okla gösterdiğimiz noktadan çalışmaya devam
edecektir:

.. code-block:: c

    if (mutex_lock_interruptible(&g_mutex) != 0)
        return -ERESTARTSYS;
    while (g_flag == 0) {
        mutex_unlock(&g_mutex);
        if (wait_event_interruptible(g_wq, g_flag != 0) != 0)
            return -ERESTARTSYS;

        /* ----> çalışma buradan devam edecek */

        if (mutex_lock_interruptible(&g_mutex) != 0)
            return -ERESTARTSYS;
    }

    /* burada uyanınca yapılacak işlemler var */

Birden fazla thread uyandığında ``mutex``'in sahipliği tek bir thread tarafından alınacaktır.
Dolayısıyla diğer thread'ler ``mutex`` kilitli olduğu için bekleyecektir. ``mutex``'in kilidini
alan thread ``while`` koşuluna takılacak ve ``mutex``'in sahipliğini bırakıp yeniden uykuya
dalacaktır. Diğer thread'ler de benzer davranışı gösterecektir. Bu kalıp sayesinde aslında çok
sayıda thread uyandırıldığı halde bunlardan yalnızca bir tanesi akışına devam edecek ve diğerleri
yeniden bloke olacaktır.

Yukarıdaki kalıpta ``mutex`` yerine kod bloğu kısaysa spinlock da kullanabilirsiniz. Örneğin:

.. code-block:: c

    spin_lock(&g_spinlock);
    while (g_flag == 0) {
        spin_unlock(&g_spinlock);
        if (wait_event_interruptible(g_wq, g_flag != 0) != 0)
            return -ERESTARTSYS;
        spin_lock(&g_spinlock);
    }
    g_flag = 0;
    spin_unlock(&g_spinlock);

    /* burada uyanınca yapılacak işlemler var */

Ancak bu tür durumlarda spinlock kullanırken dikkat etmelisiniz.

Bekleme Kuyruklarının Çekirdek İçerisindeki Kullanımları
--------------------------------------------------------

Linux çekirdeklerinde bekleme kuyrukları pek çok yerde açık ya da gizli bir biçimde karşımıza
çıkmaktadır. Çekirdek kodlarındaki bekleme kuyruklarının bir bölümü burada görmüş olduğumuz veri
yapısı (``wait_queue_head_t``) ve makrolarla (``wait_event`` ve ``wake_up`` makroları)
oluşturulmuştur. Ancak bazı bekleme kuyrukları performans kazancı sağlayabilmek için ilgili veri
yapısının içerisinde manuel oluşturulmuştur. Örneğin eskiden semaphore, mutex gibi nesnelerin
bekleme kuyrukları yukarıda ele almış olduğumuz ``wait_queue_head_t`` yapısını kullanıyordu,
işlemler de ``wait_event`` ve ``wake_up`` ile yapılıyordu. Ancak daha sonraları bu senkronizasyon
nesnelerine ilişkin bekleme kuyruklarının daha az maliyetle bu senkronizasyon nesnelerinin
içerisinde manuel bir biçimde oluşturulması yoluna gidilmiştir. Örneğin çekirdeğin 2.4'lü
versiyonlarında ``semaphore`` yapısı şöyleydi:

.. code-block:: c

    struct semaphore {
        atomic_t          count;
        int               sleepers;
        wait_queue_head_t wait;
    #if WAITQUEUE_DEBUG
        long              __magic;
    #endif
    };

Görüldüğü gibi semaphore'u bekleyen thread'ler yapıdaki ``wait`` elemanına ilişkin bekleme
kuyruğunu kullanıyordu. Ancak güncel çekirdeklerdeki ``semaphore`` yapısı şöyledir:

.. code-block:: c

    struct semaphore {
        raw_spinlock_t      lock;
        unsigned int        count;
        struct list_head    wait_list;
    #ifdef CONFIG_DETECT_HUNG_TASK_BLOCKER
        unsigned long       last_holder;
    #endif
    };

Görüldüğü gibi bekleme kuyruğu için 2.6'lı çekirdeklerle birlikte manuel bir bağlı liste
oluşturulmuştur.

Bekleme Kuyruklarına İlişkin Daha Karmaşık Bir Örnek: Boru Aygıt Sürücüsü
-------------------------------------------------------------------------

Şimdi bekleme kuyruklarının kullanımına daha ayrıntılı bir örnek verelim. Bu örneğimizde isimli
boru mekanizmasını gerçekleştiren bir aygıt sürücü oluşturacağız. Anımsanacağı gibi UNIX/Linux
sistemlerinde isimli borular (named pipes) prosesler arası haberleşmede kullanılan önemli bir
mekanizmadır. Önce isimli boruların kullanıcı modundan kullanılmasını açıklayalım.

İsimli borular UNIX/Linux sistemlerinde ``mkfifo`` isimli POSIX fonksiyonuyla yaratılmaktadır:

.. code-block:: c

    #include <sys/stat.h>

    int mkfifo(const char *pathname, mode_t mode);

Fonksiyonun birinci parametresi yaratılacak isimli borunun yol ifadesini, ikinci parametresi ise
onun erişim haklarını belirtmektedir. Fonksiyon başarı durumunda 0 değerine, başarısızlık
durumunda -1 değerine geri dönmektedir. Ancak uygulamacılar genellikle isimli boruları bu
fonksiyonla değil bu fonksiyonu çağıran ``mkfifo`` isimli komutla (programla) oluşturmaktadır.
Örneğin:

.. code-block:: console

    $ mkfifo mypipe
    $ ls -l mypipe
    prw-r--r-- 1 kaan study 0 Mar 29 10:43 mypipe

İsimli boruların dosya sistemindeki dosya türünün ``p`` biçiminde olduğuna dikkat ediniz. Burada
erişim hakları default biçimde verilmiştir. Ancak komutta ``-m`` seçeneği ile erişim hakları
açıkça da belirtilebilir. Örneğin:

.. code-block:: console

    $ mkfifo -m 666 mypipe
    $ ls -l mypipe
    prw-rw-rw- 1 kaan study 0 Mar 29 10:45 mypipe

Tipik olarak isimli borular haberleşecek proseslerden biri tarafından ``open`` fonksiyonu read
modda (``O_RDONLY`` bayrağıyla) diğeri tarafından ise write modda (``O_WRONLY`` bayrağı ile)
açılmaktadır. Okuma amaçlı açan proses boruyu diğer taraf yazma amaçlı açana kadar ``open``
fonksiyonunda bloke olmaktadır. Benzer biçimde yazma amaçlı boruyu açan taraf da diğer taraf
okuma amaçlı boruyu açana kadar bloke olmaktadır.

UNIX/Linux sistemlerinde borular tek yönlüdür. Her iki proses de aynı boru üzerinde işlem
yapmaktadır. Bu nedenle boru haberleşmesinde hangi tarafın okuma yapacağı hangi tarafın yazma
yapacağı belirlenmelidir. Bundan sonra okuma ve yazma işlemleri ``read`` ve ``write`` POSIX
fonksiyonlarıyla yapılmaktadır. Borular FIFO kuyruk sistemidir. Yani yazan tarafın yazdıklarını
aynı sırada karşı taraf okumaktadır. Boruları kullanışlı kılan en önemli özellik senkronizasyonun
bloke yoluyla otomatik sağlanmasıdır. Boruların belli bir büyüklüğü vardır. Yazan taraf henüz
okuyan taraf okumamışsa boruyu doldurduğunda ``write`` fonksiyonunda bloke olur ve bekler. Okuyan
taraf borudan okuma yaptığında boruda yer açılır. Böylece yazan tarafın blokesi çözülür. Benzer
biçimde eğer boru boşsa okuyan taraf bloke olmaktadır. Boş boruya yazma yapıldığında okuyan
tarafın blokesi çözülmektedir.

Borulara ``write`` fonksiyonu ile yazma yapılırken eğer boruda tüm byte'ların yazılması için
gerekli olan boşluk yoksa ``write`` fonksiyonu tüm byte'lar yazılana kadar (yani talep edilen
miktarın hepsi yazılana kadar) boruda yer açılmasını blokede beklemektedir. Yani borulara parçalı
yazım yapılmamaktadır. Örneğin boruda 10 byte boş yer bulunuyor olsun. Biz de boruya 20 byte
yazmak isteyelim. İşte bu durumda ``write`` fonksiyonu bloke olarak bekler. Yani 10 byte'ı yazıp
geri dönmez. 20 byte'ın hepsi yazılana kadar bekler. Ancak borulardan okuma parçalı biçimde
yapılabilmektedir. Borudan okuyan taraf n byte okumak istediğinde boruda n byte yoksa ama k < n
olacak biçimde k byte varsa ``read`` fonksiyonu bu k byte'ı okur ve okuduğu byte sayısı olan bu k
değeri ile döner. Ancak boruda okunacak hiç byte yoksa ``read`` fonksiyonu thread'i bloke
etmektedir. Örneğin boş bir borudan 100 byte okumak isteyelim. Biz ``read`` içerisinde bloke
oluruz. Şimdi boruya karşı tarafın 10 byte yazdığını düşünelim. İşte ``read`` fonksiyonu 100
byte'ın hepsini okumaya çalışmaz; okuyabildiği bu 10 byte'ı okur ve geri döner.

Bir boruya iki farklı proses aynı anda yazma yapsa bile iç içe geçme oluşmamaktadır. Bunlardan
biri önce yazıp diğeri sonra yazmaktadır. Yani yazılanlar birbirleriyle iç içe geçmemektedir.
Ancak burada bir istisna da vardır. Eğer boruya tek hamlede yazılacak byte sayısı ``PIPE_BUF``
sembolik sabitiyle belirtilen değerden büyükse iç içe geçmeme garantisi verilmemektedir.
``PIPE_BUF`` değeri Linux default durumda 4096'dır. Mevcut çekirdeklerde bir boru için ayrılan
alan default olarak 64K'dır (eskiden 4K idi). Ancak ``fcntl`` çağrısı ile bu büyüklük
1.048.576'ya (1 MB) yükseltilebilmektedir.

Boru haberleşmesinde yazan tarafın boruyu kapatması gerekir. Yazan taraf boruyu kapattıktan sonra
okuyan taraf önce boruda kalanları okur. Boruda bir şey kalmayınca ``read`` fonksiyonu 0 ile geri
döner. Bu özel durum "karşı tarafın boruyu kapattığını ve artık boruda okunacak bir şey de
kalmadığını" belirtmektedir. İşte ``read`` fonksiyonu 0 ile geri döndüğünde okuyan taraf da
işlemini sonlandırır ve boruyu kapatır. Eğer yanlışlıkla okuyan taraf boruyu daha önce kapatırsa
yazan tarafta ilk ``write`` işleminde ``SIGPIPE`` sinyali oluşturulur. Bu sinyal ele alınmazsa
proses sonlandırılmaktadır.

Birden fazla proses aynı boruya yazma yapabilir ve aynı borudan okuma yapabilir. Ancak uygulamada
bu durumla seyrek karşılaşılmaktadır. Boru tabanlı client-server uygulamalarda aynı boruya istek
iletmek için birden fazla client programın yazması durumuyla karşılaşılmaktadır. Ancak aynı
borudan birden fazla prosesin okuma yapmasının bir anlamı yoktur.

Borular ``open`` fonksiyonunda ``O_NONBLOCK`` açış bayrağı kullanılarak (örneğin
``O_RDONLY|O_NONBLOCK`` gibi) blokesiz modda da kullanılabilmektedir. Ancak bu kullanım çok daha
seyrektir. Blokesiz boru işlemlerinin default blokeli işlemlere göre şu farklılıkları vardır:

- ``open`` fonksiyonunda bloke oluşmaz.
- ``read`` fonksiyonu boruda hiç byte yoksa bloke olmaz, başarısızlıkla (-1 değeri ile) geri döner.
  Ancak ``errno`` değişkeni ``EAGAIN`` özel değeri ile set edilmektedir.
- ``write`` fonksiyonu boru doluysa bloke olmaz, bu durumda ``write`` fonksiyonu da başarısızlıkla
  (-1 değeri ile) geri döner ve ``errno`` ``EAGAIN`` özel değeri ile set edilir.

Aşağıda kullanıcı modunda isimli boru haberleşmesine yönelik basit bir örnek verilmiştir. İki
ayrı terminal açarak programları herhangi bir sırada çalıştırabilirsiniz:

.. code-block:: console

    $ ./pipe-read
    $ ./pipe-write

``pipe-read.c``

.. code-block:: c

    #include <stdio.h>
    #include <stdlib.h>
    #include <fcntl.h>
    #include <unistd.h>

    void exit_sys(const char *msg);

    int main(void)
    {
        int fd;
        int val;
        ssize_t result;

        if ((fd = open("mypipe", O_RDONLY)) == -1)
            exit_sys("open");

        for (;;) {
            if ((result = read(fd, &val, sizeof(int))) == -1)
                exit_sys("read");
            if (result == 0)
                break;
            printf("%d\n", val);
        }

        close(fd);

        return 0;
    }

    void exit_sys(const char *msg)
    {
        perror(msg);
        exit(EXIT_FAILURE);
    }

``pipe-write.c``

.. code-block:: c

    #include <stdio.h>
    #include <stdlib.h>
    #include <fcntl.h>
    #include <unistd.h>

    void exit_sys(const char *msg);

    int main(void)
    {
        int fd;

        if ((fd = open("mypipe", O_WRONLY)) == -1)
            exit_sys("open");

        for (int i = 0; i < 1000000; ++i)
            if (write(fd, &i, sizeof(int)) == -1)
                exit_sys("write");

        close(fd);

        return 0;
    }

    void exit_sys(const char *msg)
    {
        perror(msg);
        exit(EXIT_FAILURE);
    }

Biz çekirdeğin boru gerçekleştirimini kursumuzun *proseslerarası haberleşme (inter-process
communication)* yöntemlerini ele aldığımız bölümde ayrıca açıklayacağız. Ancak şimdi bekleme
kuyruklarının kullanımına örnek vermek amacıyla isimli boru mekanizmasını yaklaşık oluşturan bir
çekirdek aygıt sürücüsünü yazmaya çalışalım. Bu aygıt sürücüsünde okuyan taraf ve yazan taraf için
(bunlar birden fazla olabilir) ayrı bekleme kuyrukları olması gerekir:

.. code-block:: c

    static wait_queue_head_t g_wqread;
    static wait_queue_head_t g_wqwrite;

Ayrıca ``open`` fonksiyonunda bloke oluşturmak için de iki bekleme kuyruğu bulundurulmalıdır:

.. code-block:: c

    static wait_queue_head_t g_wqwriteopen;
    static wait_queue_head_t g_wqreadopen;

Boru işlemlerinde senkronizasyon sağlamak için de ayrı bir semaphore (mutex de olabilirdi)
bulundurulmuştur:

.. code-block:: c

    static DEFINE_SEMAPHORE(g_sem, 1);

Aygıt sürücü yüklendiğinde bu bekleme kuyrukları yaratılmıştır:

.. code-block:: c

    static int __init pipe_driver_init(void)
    {
        int result;

        printk(KERN_INFO "pipe-driver init...\n");

        if ((result = alloc_chrdev_region(&g_dev, 0, 1, "pipe-driver")) < 0) {
            printk(KERN_ERR "cannot register device!...\n");
            return result;
        }

        cdev_init(&g_cdev, &g_fops);
        if ((result = cdev_add(&g_cdev, g_dev, 1)) < 0) {
            unregister_chrdev_region(g_dev, 1);
            printk(KERN_ERR "cannot add device!...\n");
            return result;
        }

        init_waitqueue_head(&g_wqreadopen);
        init_waitqueue_head(&g_wqwriteopen);
        init_waitqueue_head(&g_wqread);
        init_waitqueue_head(&g_wqwrite);

        return 0;
    }

Boruyu kullanan prosesler ``open`` fonksiyonunu çağırdığında aygıt sürücüdeki ``open`` fonksiyonu
çalıştırılacaktır. İşte aygıt sürücüdeki ``open`` fonksiyonu içerisinde "karşı taraf boruyu uygun
bir biçimde açmış mı" kontrolü yapılıp duruma göre bloke uygulanmıştır:

.. code-block:: c

    static int pipe_driver_open(struct inode *inodep, struct file *filp)
    {
        int accmode = filp->f_flags & O_ACCMODE;

        if (down_interruptible(&g_sem) != 0)
            return -ERESTARTSYS;

        if (accmode == O_RDONLY) {
            ++g_nreaders;
            wake_up_interruptible(&g_wqwriteopen);
            while (g_nwriters == 0) {
                up(&g_sem);
                if (filp->f_flags & O_NONBLOCK)
                    return 0;
                if (wait_event_interruptible(g_wqreadopen, g_nwriters > 0))
                    return -ERESTARTSYS;
                if (down_interruptible(&g_sem))
                    return -ERESTARTSYS;
            }
        }
        else if (accmode == O_WRONLY) {
            ++g_nwriters;
            wake_up_interruptible(&g_wqreadopen);
            while (g_nreaders == 0) {
                if (filp->f_flags & O_NONBLOCK) {
                    --g_nwriters;
                    up(&g_sem);
                    return -ENXIO;
                }
                up(&g_sem);
                if (wait_event_interruptible(g_wqwriteopen, g_nreaders > 0))
                    return -ERESTARTSYS;
                if (down_interruptible(&g_sem))
                    return -ERESTARTSYS;
            }
        }
        else if (accmode == O_RDWR) {
            ++g_nreaders;
            ++g_nwriters;
            wake_up_interruptible(&g_wqreadopen);
            wake_up_interruptible(&g_wqwriteopen);
        }
        up(&g_sem);

        return 0;
    }

Burada zaten kodun en dıştan semaphore ile kilitlendiğini görüyorsunuz. Bu nedenle semaphore
içerisinde ayrıca atomik işlemlerin yapılmasına gerek kalmamıştır. ``open`` fonksiyonunda ilk
olarak kullanıcı modundaki prosesin aygıt dosyasını okuma modunda mı yazma modunda mı açtığına
bakılmıştır. Eğer proses aygıt dosyasını okuma modunda açmışsa yazma modunda açanların
uyandırılması gerekmektedir. Ayrıca okuma modunda ve yazma modunda açanların sayısı da iki global
değişkende tutulmuştur:

.. code-block:: c

    if (accmode == O_RDONLY) {
        ++g_nreaders;
        wake_up_interruptible(&g_wqwriteopen);
        while (g_nwriters == 0) {
            up(&g_sem);
            if (filp->f_flags & O_NONBLOCK)
                return 0;
            if (wait_event_interruptible(g_wqreadopen, g_nwriters > 0))
                return -ERESTARTSYS;
            if (down_interruptible(&g_sem))
                return -ERESTARTSYS;
        }
    }

Burada eğer aygıt dosyası ``O_NONBLOCK`` bayrağıyla açılmışsa ``open`` hemen başarıyla
sonlandırılmıştır. Aygıt dosyası ``O_NONBLOCK`` ile açılmamışsa ve yazan taraf da yoksa bu
durumda thread ``g_wqreadopen`` bekleme kuyruğuna kendini yazarak bloke oluşturur. Bunu oradan
kurtaracak olan yazan taraftır. Koddaki semaphore'un kullanımına dikkat ediniz. Thread uykuya
dalmadan önce semaphore sayacını artırarak semaphore'u serbest bırakmıştır. Uykudan uyandığında
yeniden semaphore kilidini almıştır. Koddaki ``while`` döngüsü size biraz tuhaf gelebilir. Bu
``while`` döngüsünün amacı şudur: okuyan taraf eğer aygıt dosyasını yazma modunda açmış olan bir
proses yoksa bloke olmaktadır; ancak bir proses dosyayı write modda açıp hemen kapatırsa ve
buradaki zamanlama kötü bir tesadüfe denk gelirse, ``while`` döngüsü kullanılmadığında
uyandırılmış olan thread yoluna devam edecektir.

Aygıt sürücünün ``open`` fonksiyonunda eğer aygıt dosyası write modda açılmışsa aşağıdaki kod
parçası çalıştırılmaktadır:

.. code-block:: c

    else if (accmode == O_WRONLY) {
        ++g_nwriters;
        wake_up_interruptible(&g_wqreadopen);
        while (g_nreaders == 0) {
            if (filp->f_flags & O_NONBLOCK) {
                --g_nwriters;
                up(&g_sem);
                return -ENXIO;
            }
            up(&g_sem);
            if (wait_event_interruptible(g_wqwriteopen, g_nreaders > 0))
                return -ERESTARTSYS;
            if (down_interruptible(&g_sem))
                return -ERESTARTSYS;
        }
    }

Burada da önce aygıt dosyasını ``O_RDONLY`` modunda açıp da bloke olmuş olan thread'lerin blokesi
çözülmüştür. Daha sonra benzer mantık uygulanmıştır. Boruların read/write modda açılmasını POSIX
standartları "işletim sisteminin isteğine" bırakmaktadır. Linux'ta isimli borular ``O_RDWR``
modunda açılabilmektedir. İşte aygıt sürücünün ``open`` fonksiyonunda bu kontrol de yapılmıştır:

.. code-block:: c

    else if (accmode == O_RDWR) {
        ++g_nreaders;
        ++g_nwriters;
        wake_up_interruptible(&g_wqreadopen);
        wake_up_interruptible(&g_wqwriteopen);
    }

Aygıt sürücümüzün ``read`` fonksiyonu şöyle yazılmıştır:

.. code-block:: c

    static ssize_t pipe_driver_read(struct file *filp, char *buf, size_t size, loff_t *off)
    {
        size_t esize, size1, size2;
        ssize_t result = -EFAULT;

        if (down_interruptible(&g_sem) != 0)
            return -ERESTARTSYS;

        while (g_count == 0) {
            if (g_nwriters == 0) {
                result = 0;
                goto EXIT;
            }
            up(&g_sem);
            if (filp->f_flags & O_NONBLOCK)
                return -EAGAIN;
            if (wait_event_interruptible(g_wqread, g_count > 0 || g_nwriters == 0) != 0)
                return -ERESTARTSYS;
            if (down_interruptible(&g_sem) != 0)
                return -ERESTARTSYS;
        }

        esize = MIN(size, g_count);
        if (g_head >= g_tail)
            size1 = MIN(esize, PIPE_BUFFER_SIZE - g_head);
        else
            size1 = esize;

        size2 = esize - size1;

        if (copy_to_user(buf, g_pipebuf + g_head, size1) != 0)
            goto EXIT;

        if (size2 != 0)
            if (copy_to_user(buf + size1, g_pipebuf, size2) != 0)
                goto EXIT;

        g_head = (g_head + esize) % PIPE_BUFFER_SIZE;
        g_count -= esize;

        result = esize;

        wake_up_interruptible(&g_wqwrite);
    EXIT:
        up(&g_sem);

        return result;
    }

Burada eşzamanlı okumalarda senkronizasyon sorununun oluşmaması için önce semaphore kilidi
alınmıştır:

.. code-block:: c

    if (down_interruptible(&g_sem) != 0)
        return -ERESTARTSYS;

Eğer boruda hiç byte yoksa ve yazan taraf da boruyu kapatmışsa ``read`` fonksiyonu 0 ile geri
döndürülmektedir:

.. code-block:: c

    while (g_count == 0) {
        if (g_nwriters == 0) {
            result = 0;
            goto EXIT;
        }
        /* ... */
    }

Daha sonra semaphore kilidi açılmış ve aygıt dosyasının ``O_NONBLOCK`` bayrağıyla açılıp
açılmadığına bakılmıştır. Eğer boruda hiç byte yoksa ve aygıt dosyası da ``O_NONBLOCK``
bayrağıyla açılmışsa ``read`` fonksiyonu ``-EAGAIN`` errno değeriyle geri döndürülmüştür:

.. code-block:: c

    while (g_count == 0) {
        if (g_nwriters == 0) {
            result = 0;
            goto EXIT;
        }
        up(&g_sem);
        if (filp->f_flags & O_NONBLOCK)
            return -EAGAIN;
        /* ... */
    }

Eğer bu durum da söz konusu değilse thread ``g_count > 0 || g_nwriters == 0`` koşuluyla uykuya
yatırılmıştır:

.. code-block:: c

    while (g_count == 0) {
        if (g_nwriters == 0) {
            result = 0;
            goto EXIT;
        }
        up(&g_sem);
        if (filp->f_flags & O_NONBLOCK)
            return -EAGAIN;

        if (wait_event_interruptible(g_wqread, g_count > 0 || g_nwriters == 0) != 0)
            return -ERESTARTSYS;
        if (down_interruptible(&g_sem) != 0)
            return -ERESTARTSYS;
    }

İsimli borularda borudan okuma yapan thread bloke olmuşsa ancak boruya yazan proses de sonlanmışsa
uyuyan thread'lerin uyandırılması gerektiğini anımsayınız. Uyandırma koşulu bu durumu dikkate
almaktadır. Aygıt sürücünün ``read`` fonksiyonundaki kalan işlemler kuyrukla ilgilidir.

Aygıt sürücümüzün ``write`` fonksiyonu da şöyle yazılmıştır:

.. code-block:: c

    static ssize_t pipe_driver_write(struct file *filp, const char *buf, size_t size, loff_t *off)
    {
        size_t esize, size1, size2;
        ssize_t result = -EFAULT;

        if (size > PIPE_BUFFER_SIZE)
            size = PIPE_BUFFER_SIZE;

        if (down_interruptible(&g_sem) != 0)
            return -ERESTARTSYS;

        if (g_nreaders == 0) {
            up(&g_sem);
            send_sig(SIGPIPE, current, 0);
            return -EPIPE;
        }

        while (PIPE_BUFFER_SIZE - g_count < size) {
            up(&g_sem);
            if (filp->f_flags & O_NONBLOCK)
                return -EAGAIN;
            if (wait_event_interruptible(g_wqwrite,
                    PIPE_BUFFER_SIZE - g_count >= size || g_nreaders == 0) != 0)
                return -ERESTARTSYS;
            if (down_interruptible(&g_sem) != 0)
                return -ERESTARTSYS;
            if (g_nreaders == 0) {
                up(&g_sem);
                send_sig(SIGPIPE, current, 0);
                return -EPIPE;
            }
        }

        esize = MIN(size, PIPE_BUFFER_SIZE - g_count);

        if (g_tail >= g_head)
            size1 = MIN(esize, PIPE_BUFFER_SIZE - g_tail);
        else
            size1 = esize;

        size2 = esize - size1;

        if (copy_from_user(g_pipebuf + g_tail, buf, size1) != 0)
            goto EXIT;
        if (size2 != 0)
            if (copy_from_user(g_pipebuf, buf + size1, size2) != 0)
                goto EXIT;

        g_tail = (g_tail + esize) % PIPE_BUFFER_SIZE;
        g_count += esize;
        result = esize;

    EXIT:
        wake_up_interruptible(&g_wqread);
        up(&g_sem);

        return result;
    }

Burada da ``read`` fonksiyonuna benzer işlemler ters biçimde yapılmıştır. Yine önce semaphore ile
eş zamanlı erişimler için kilitleme uygulanmıştır. Sonra da eğer borudan okuma potansiyelinde
olan hiçbir thread yoksa ``SIGPIPE`` sinyali oluşturulmuştur:

.. code-block:: c

    if (down_interruptible(&g_sem) != 0)
        return -ERESTARTSYS;

    if (g_nreaders == 0) {
        up(&g_sem);
        send_sig(SIGPIPE, current, 0);
        return -EPIPE;
    }

Daha sonra borunun dolu olmadığına bakılmış ve eğer boru tamamen doluysa talep edilen yazmanın
yapılabilmesi için gereken boş alan koşul haline getirilerek thread bloke edilmiştir:

.. code-block:: c

    while (PIPE_BUFFER_SIZE - g_count < size) {
        up(&g_sem);
        if (filp->f_flags & O_NONBLOCK)
            return -EAGAIN;
        if (wait_event_interruptible(g_wqwrite,
                PIPE_BUFFER_SIZE - g_count >= size || g_nreaders == 0) != 0)
            return -ERESTARTSYS;
        if (down_interruptible(&g_sem) != 0)
            return -ERESTARTSYS;
        if (g_nreaders == 0) {
            up(&g_sem);
            send_sig(SIGPIPE, current, 0);
            return -EPIPE;
        }
    }

Buradaki uyanma koşuluna dikkat ediniz: ``PIPE_BUFFER_SIZE - g_count >= size || g_nreaders == 0``.
Bu koşul "boruda yeteri kadar yer açılana kadar ya da borudan okuma potansiyeline sahip hiçbir
proses kalmayana kadar uyu" anlamına gelmektedir.

Aşağıda aygıt sürücünün tüm kodları verilmiştir. Derleme işlemini şöyle yapabilirsiniz:

.. code-block:: console

    $ make file=pipe-driver

Yüklemeyi şöyle yapabilirsiniz:

.. code-block:: console

    $ sudo ./load pipe-driver

Borudan okuma yapan programı şöyle çalıştırabilirsiniz:

.. code-block:: console

    $ ./pipe-read mypipe

Boruya yazma yapan programı farklı bir terminalden çalıştırmalısınız:

.. code-block:: console

    $ ./pipe-write mypipe

Test işleminizi bitirdikten sonra aygıt sürücüyü ``unload`` betiği ile kaldırabilirsiniz:

.. code-block:: console

    $ sudo ./unload pipe-driver

``pipe-driver.c``

.. code-block:: c

    #include <linux/module.h>
    #include <linux/kernel.h>
    #include <linux/fs.h>
    #include <linux/cdev.h>
    #include <linux/semaphore.h>
    #include <linux/wait.h>

    #define PIPE_BUFFER_SIZE    10
    #define MIN(a, b)           ((a) < (b) ? (a) : (b))

    MODULE_LICENSE("GPL");
    MODULE_AUTHOR("Kaan Aslan");
    MODULE_DESCRIPTION("Pipe Device Driver");

    static int pipe_driver_open(struct inode *inodep, struct file *filp);
    static int pipe_driver_release(struct inode *inodep, struct file *filp);
    static ssize_t pipe_driver_read(struct file *filp, char *buf, size_t size, loff_t *off);
    static ssize_t pipe_driver_write(struct file *filp, const char *buf, size_t size, loff_t *off);

    static dev_t g_dev;
    static struct cdev g_cdev;
    static struct file_operations g_fops = {
        .owner   = THIS_MODULE,
        .open    = pipe_driver_open,
        .read    = pipe_driver_read,
        .write   = pipe_driver_write,
        .release = pipe_driver_release
    };

    static unsigned char g_pipebuf[PIPE_BUFFER_SIZE];
    static size_t g_head;
    static size_t g_tail;
    static size_t g_count;
    static wait_queue_head_t g_wqwriteopen;
    static wait_queue_head_t g_wqreadopen;
    static wait_queue_head_t g_wqread;
    static wait_queue_head_t g_wqwrite;
    static int g_nreaders;
    static int g_nwriters;

    static DEFINE_SEMAPHORE(g_sem, 1);

    static int __init pipe_driver_init(void)
    {
        int result;

        printk(KERN_INFO "pipe-driver init...\n");

        if ((result = alloc_chrdev_region(&g_dev, 0, 1, "pipe-driver")) < 0) {
            printk(KERN_ERR "cannot register device!...\n");
            return result;
        }

        cdev_init(&g_cdev, &g_fops);
        if ((result = cdev_add(&g_cdev, g_dev, 1)) < 0) {
            unregister_chrdev_region(g_dev, 1);
            printk(KERN_ERR "cannot add device!...\n");
            return result;
        }

        init_waitqueue_head(&g_wqreadopen);
        init_waitqueue_head(&g_wqwriteopen);
        init_waitqueue_head(&g_wqread);
        init_waitqueue_head(&g_wqwrite);

        return 0;
    }

    static void __exit pipe_driver_exit(void)
    {
        cdev_del(&g_cdev);
        unregister_chrdev_region(g_dev, 1);

        printk(KERN_INFO "pipe-driver exit...\n");
    }

    static int pipe_driver_open(struct inode *inodep, struct file *filp)
    {
        int accmode = filp->f_flags & O_ACCMODE;

        if (down_interruptible(&g_sem) != 0)
            return -ERESTARTSYS;

        if (accmode == O_RDONLY) {
            ++g_nreaders;
            wake_up_interruptible(&g_wqwriteopen);
            while (g_nwriters == 0) {
                up(&g_sem);
                if (filp->f_flags & O_NONBLOCK)
                    return 0;
                if (wait_event_interruptible(g_wqreadopen, g_nwriters > 0))
                    return -ERESTARTSYS;
                if (down_interruptible(&g_sem))
                    return -ERESTARTSYS;
            }
        }
        else if (accmode == O_WRONLY) {
            ++g_nwriters;
            wake_up_interruptible(&g_wqreadopen);
            while (g_nreaders == 0) {
                if (filp->f_flags & O_NONBLOCK) {
                    --g_nwriters;
                    up(&g_sem);
                    return -ENXIO;
                }
                up(&g_sem);
                if (wait_event_interruptible(g_wqwriteopen, g_nreaders > 0))
                    return -ERESTARTSYS;
                if (down_interruptible(&g_sem))
                    return -ERESTARTSYS;
            }
        }
        else if (accmode == O_RDWR) {
            ++g_nreaders;
            ++g_nwriters;
            wake_up_interruptible(&g_wqreadopen);
            wake_up_interruptible(&g_wqwriteopen);
        }
        up(&g_sem);

        return 0;
    }

    static int pipe_driver_release(struct inode *inodep, struct file *filp)
    {
        int accmode = filp->f_flags & O_ACCMODE;

        if (down_interruptible(&g_sem) != 0)
            return -ERESTARTSYS;

        if (accmode == O_RDONLY)
            --g_nreaders;
        else if (accmode == O_WRONLY)
            --g_nwriters;
        else if (accmode == O_RDWR) {
            --g_nreaders;
            --g_nwriters;
        }
        if (g_nreaders == 0)
            wake_up_interruptible(&g_wqwrite);
        if (g_nwriters == 0)
            wake_up_interruptible(&g_wqread);

        if (g_nreaders + g_nwriters == 0)
            g_count = g_head = g_tail = 0;

        up(&g_sem);

        return 0;
    }

    static ssize_t pipe_driver_read(struct file *filp, char *buf, size_t size, loff_t *off)
    {
        size_t esize, size1, size2;
        ssize_t result = -EFAULT;

        if (down_interruptible(&g_sem) != 0)
            return -ERESTARTSYS;

        while (g_count == 0) {
            if (g_nwriters == 0) {
                result = 0;
                goto EXIT;
            }
            up(&g_sem);
            if (filp->f_flags & O_NONBLOCK)
                return -EAGAIN;
            if (wait_event_interruptible(g_wqread, g_count > 0 || g_nwriters == 0) != 0)
                return -ERESTARTSYS;
            if (down_interruptible(&g_sem) != 0)
                return -ERESTARTSYS;
        }

        esize = MIN(size, g_count);
        if (g_head >= g_tail)
            size1 = MIN(esize, PIPE_BUFFER_SIZE - g_head);
        else
            size1 = esize;

        size2 = esize - size1;

        if (copy_to_user(buf, g_pipebuf + g_head, size1) != 0)
            goto EXIT;

        if (size2 != 0)
            if (copy_to_user(buf + size1, g_pipebuf, size2) != 0)
                goto EXIT;

        g_head = (g_head + esize) % PIPE_BUFFER_SIZE;
        g_count -= esize;

        result = esize;

        wake_up_interruptible(&g_wqwrite);
    EXIT:
        up(&g_sem);

        return result;
    }

    static ssize_t pipe_driver_write(struct file *filp, const char *buf, size_t size, loff_t *off)
    {
        size_t esize, size1, size2;
        ssize_t result = -EFAULT;

        if (size > PIPE_BUFFER_SIZE)
            size = PIPE_BUFFER_SIZE;

        if (down_interruptible(&g_sem) != 0)
            return -ERESTARTSYS;

        if (g_nreaders == 0) {
            up(&g_sem);
            send_sig(SIGPIPE, current, 0);
            return -EPIPE;
        }
        while (PIPE_BUFFER_SIZE - g_count < size) {
            up(&g_sem);
            if (filp->f_flags & O_NONBLOCK)
                return -EAGAIN;
            if (wait_event_interruptible(g_wqwrite,
                    PIPE_BUFFER_SIZE - g_count >= size || g_nreaders == 0) != 0)
                return -ERESTARTSYS;
            if (down_interruptible(&g_sem) != 0)
                return -ERESTARTSYS;
            if (g_nreaders == 0) {
                up(&g_sem);
                send_sig(SIGPIPE, current, 0);
                return -EPIPE;
            }
        }

        esize = MIN(size, PIPE_BUFFER_SIZE - g_count);

        if (g_tail >= g_head)
            size1 = MIN(esize, PIPE_BUFFER_SIZE - g_tail);
        else
            size1 = esize;

        size2 = esize - size1;

        if (copy_from_user(g_pipebuf + g_tail, buf, size1) != 0)
            goto EXIT;
        if (size2 != 0)
            if (copy_from_user(g_pipebuf, buf + size1, size2) != 0)
                goto EXIT;

        g_tail = (g_tail + esize) % PIPE_BUFFER_SIZE;
        g_count += esize;
        result = esize;

    EXIT:
        wake_up_interruptible(&g_wqread);
        up(&g_sem);

        return result;
    }

    module_init(pipe_driver_init);
    module_exit(pipe_driver_exit);

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

``pipe-read.c``

.. code-block:: c

    #include <stdio.h>
    #include <stdlib.h>
    #include <fcntl.h>
    #include <unistd.h>

    void exit_sys(const char *msg);

    int main(int argc, char *argv[])
    {
        int fd;
        int val;
        ssize_t result;

        if (argc != 2) {
            fprintf(stderr, "wrong number of arguments!..\n");
            exit(EXIT_FAILURE);
        }

        if ((fd = open(argv[1], O_RDONLY)) == -1)
            exit_sys("open");

        for (;;) {
            if ((result = read(fd, &val, sizeof(int))) == -1)
                exit_sys("read");
            if (result == 0)
                break;
            printf("%d\n", val);
        }

        close(fd);

        return 0;
    }

    void exit_sys(const char *msg)
    {
        perror(msg);
        exit(EXIT_FAILURE);
    }

``pipe-write.c``

.. code-block:: c

    /* pipe-write.c */

    #include <stdio.h>
    #include <stdlib.h>
    #include <fcntl.h>
    #include <unistd.h>

    void exit_sys(const char *msg);

    int main(int argc, char *argv[])
    {
        int fd;

        if (argc != 2) {
            fprintf(stderr, "wrong number of arguments!..\n");
            exit(EXIT_FAILURE);
        }

        if ((fd = open(argv[1], O_WRONLY)) == -1)
            exit_sys("open");

        for (int i = 0; i < 1000000; ++i)
            if (write(fd, &i, sizeof(int)) == -1)
                exit_sys("write");

        close(fd);

        return 0;
    }

    void exit_sys(const char *msg)
    {
        perror(msg);
        exit(EXIT_FAILURE);
    }

Bekleme Kuyruklarına İlişkin Ayrıntılar
---------------------------------------

Şimdi de bekleme kuyruklarıyla ilgili bazı ayrıntılar üzerinde duracağız. 

Sahte Uyanma (Spurious Wakeup) Durumu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bekleme kuyruklarına ilişkin İngilizce *spurious wakeup* denilen önemli bir olgu vardır. "Spurious" 
sözcüğü "sahte, yapay, yanlış" gibi anlamlara gelmektedir. Biz buna *sahte uyanma* diyeceğiz. Sahte uyanma
"bekleme kuyruğunda uykuda olan thread'in koşulla ilgisi olmayan başka nedenden dolayı (yani
``wake_up`` dışında bir nedenden dolayı) uyandırılması" anlamına gelmektedir. Biz bekleme
kuyruğundaki thread'lerin ``wake_up`` makrolarıyla uyandırıldığını görmüştük. Uyandırılan thread
de koşula yeniden bakıyordu. Thread'in uykuya daldırılmasına ilişkin aşağı seviyeli kodu
anımsayınız:

.. code-block:: c

    #define ___wait_event(wq_head, condition, state, exclusive, ret, cmd)       \
    ({                                                                          \
        __label__ __out;                                                        \
        struct wait_queue_entry __wq_entry;                                     \
        long __ret = ret;   /* explicit shadow */                               \
                                                                                \
        init_wait_entry(&__wq_entry, exclusive ? WQ_FLAG_EXCLUSIVE : 0);        \
        for (;;) {                                                              \
            long __int = prepare_to_wait_event(&wq_head, &__wq_entry, state);   \
                                                                                \
            if (condition)                                                      \
                break;                                                          \
                                                                                \
            if (___wait_is_interruptible(state) && __int) {                     \
                __ret = __int;                                                  \
                goto __out;                                                     \
            }                                                                   \
                                                                                \
            cmd;                                                                \
                                                                                \
    /* -----> uyandırılan thread çalışmasına buradan devam eder! */             \
                                                                                \
            if (condition)                                                      \
                break;                                                          \
        }                                                                       \
        finish_wait(&wq_head, &__wq_entry);                                     \
    __out: __ret;                                                               \
    })

Burada çekirdek kodunun bir döngü içerisinde koşula bakıp, koşul sağlanmıyorsa yeniden thread'i
uyuttuğuna dikkat ediniz. İşte bu döngünün bir işlevi de yukarıda bahsettiğimiz sahte uyandırma
sorununu çözmek içindir. Daha açık bir ifadeyle bu döngü "eğer thread koşulla ilişkisiz bir
biçimde başka bir nedenden dolayı yanlışlıkla uyandırılmışsa onun yeniden uykuya dalmasını"
sağlamaktadır.

Peki bir thread neden yanlışlıkla uyandırılmaktadır? İşte aslında çekirdek bazı durumlarda
thread'leri mecburen uyandırmak zorunda kalabilmektedir. Çünkü bazı işlemlerin yapılabilmesi için
thread'in çalışıyor durumda olması gerekir. Biz aslında uyutma işleminin ``schedule`` fonksiyonun
içerisinde yapıldığını görmüştük. Dolayısıyla aslında uyanan thread ``schedule`` fonksiyonu
içerisinde uyanmaktadır. Ancak thread uyandırıldığında yoluna da devam edecektir. İşte yukarıdaki
çekirdek kodundaki döngünün bir amacı da koşulun sağlanmadığı (yani ``wake_up`` yüzünden olmayan)
sahte uyanmalarda thread'in yeniden uykuya daldırılmasıdır.

Linux çekirdeğinde sahte uyandırmalara neden olan çeşitli durumlar vardır. Bunlardan bazıları
şunlardır:

- Uyuyan bir thread'e sinyal geldiğinde thread uyandırılmaktadır. Bu uyandırmanın ``wake_up``
  işlemiyle bir ilgisi yoktur.

- Çekirdek thread'leri ``kthread_stop()`` ile durdurulmak istendiğinde eğer thread uyuyorsa önce
  onun uyandırılması gerekir.

- Çekirdekteki zamanlayıcı mekanizmaları (örneğin ``hrtimer`` zaman aşımı) thread'i ``wake_up``
  işlemiyle ilgisiz bir biçimde uyandırabilmektedir.

- ARM ve PowerPC gibi bazı mimarilerde işlemci tasarımından kaynaklanan nedenlerden dolayı bekleme
  kuyruğundaki thread'lerin ``wake_up`` işlemi dışında çekirdek tarafından uyandırılması
  gerekebilmektedir.

Sahte uyanmaların nedenleri aşağıdaki tabloda özetlenmektedir:

+---------------------------+------------------------------------------+-------------------------+
|          Kaynak           |              Mekanizma                   | Etkilenen Thread Durumu |
+===========================+==========================================+=========================+
| ARM WFE / SEV             | Başka bir core'dan gelen SEV talimatı    | INTERRUPTIBLE +         |
|                           | tüm WFE bekleyen core'ları uyandırır     | UNINTERRUPTIBLE         |
+---------------------------+------------------------------------------+-------------------------+
| ARM Hypervisor / EL2      | Hypervisor inject ettiği sanal           | INTERRUPTIBLE +         |
|                           | interrupt'ı guest'e iletmeyebilir        | UNINTERRUPTIBLE         |
+---------------------------+------------------------------------------+-------------------------+
| ARM Donanım Errata        | Cortex-A57/A72 gibi çekirdeklerde        | INTERRUPTIBLE +         |
|                           | WFI belirli koşullarda erken döner       | UNINTERRUPTIBLE         |
+---------------------------+------------------------------------------+-------------------------+
| POWER Thermal Event       | Sıcaklık eşiği aşılınca donanım          | INTERRUPTIBLE +         |
|                           | CPU'yu yazılımdan bağımsız uyandırır     | UNINTERRUPTIBLE         |
+---------------------------+------------------------------------------+-------------------------+
| POWER HMT State Rollback  | Hiper-threading güç durumu değişikliği   | INTERRUPTIBLE +         |
|                           | uyku durumunu iptal edebilir             | UNINTERRUPTIBLE         |
+---------------------------+------------------------------------------+-------------------------+
| TIF_SIGPENDING            | signal_wake_up → wake_up_state ile       | Sadece                  |
| (schedule öncesi)         | task uyandırılır, koşul değişmemiştir    | INTERRUPTIBLE           |
+---------------------------+------------------------------------------+-------------------------+
| TIF_SIGPENDING            | Task uykudayken sinyal gelir,            | Sadece                  |
| (schedule sonrası)        | schedule döner ama koşul false           | INTERRUPTIBLE           |
+---------------------------+------------------------------------------+-------------------------+
| kthread_stop.             | wake_up_process ile thread uyandırılır,  | INTERRUPTIBLE +         |
|                           | beklenen koşulla ilgisi yok              | UNINTERRUPTIBLE         |
+---------------------------+------------------------------------------+-------------------------+
| hrtimer / Timeout         | Süre dolunca wake_up_process çağrılır;   | INTERRUPTIBLE +         |
|                           | koşul üretici henüz sağlamamış olabilir  | UNINTERRUPTIBLE         |
+---------------------------+------------------------------------------+-------------------------+
| ptrace / Debugger         | ptrace_resume → wake_up_process;         | INTERRUPTIBLE +         |
|                           | tracee koşul olmadan devam ettirilir     | UNINTERRUPTIBLE         |
+---------------------------+------------------------------------------+-------------------------+

prepare_to_wait ve finish_wait Fonksiyonları
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``wait_event`` makrolarının sahte uyanma nedeniyle bir döngü eşliğinde işlem yaptığını
belirtmiştik. Ancak bazen sistem programcısı bu döngüyü istemeyebilir. Bu durumda thread'i
uykuya doğrudan kendisi yatırabilir. İşte yukarıda da ele aldığımız gibi aslında thread'i bekleme
kuyruğuna yerleştiren asıl fonksiyon ``prepare_to_wait_event`` isimli fonksiyondur. Thread'i
bekleme kuyruğundan çıkaran fonksiyon da ``finish_wait`` fonksiyonudur. Bu fonksiyonların
parametrik yapılarını anımsayınız:

.. code-block:: c

    void prepare_to_wait(struct wait_queue_head *wq_head, 
            struct wait_queue_entry *wq_entry, int state);

    void finish_wait(struct wait_queue_head *wq_head, 
            struct wait_queue_entry *wq_entry);

``prepare_to_wait`` fonksiyonunun birinci parametresi bekleme kuyruğuna ilişkin
``wait_queue_head`` nesnesinin adresini, ikinci parametresi ise bekleme kuyruğundaki düğümleri
temsil eden ``wait_queue_entry`` nesnesinin adresini almaktadır. Görüldüğü gibi programcının
``wait_queue_entry`` nesnesini de kendisinin oluşturması gerekmektedir. Fonksiyonun üçüncü
parametresi thread'e (task da denilmektedir) ilişkin durum bilgisidir. Örneğin eğer thread
sinyalle uyandırılmak isteniyorsa bu parametreye ``TASK_INTERRUPTIBLE`` girilmesi gerekir.
``prepare_to_wait`` fonksiyonu thread'i bekleme kuyruğuna yerleştirdikten sonra CPU'yu
bırakmamaktadır. Bunun için sistem programcısının ``schedule`` fonksiyonunu çağırması gerekir.

``finish_wait`` fonksiyonunun da birinci parametresi ``wait_queue_head`` nesnesinin, ikinci
parametresi de ``wait_queue_entry`` nesnesinin adresini almaktadır. ``finish_wait`` fonksiyonu
yalnızca thread'i bekleme kuyruğundan çıkarmaktadır.

Bu fonksiyonlarla uykuya daldırılan thread'ler yine ``wake_up`` fonksiyonlarıyla
uyandırılmalıdır.

Aşağıda bu fonksiyonların kullanımına bir örnek verilmiştir. Buradaki çekirdek modülünün init
fonksiyonu şöyle yazılmıştır:

.. code-block:: c

    static int __init wait_module_init(void)
    {
        g_waiter_thread = kthread_run(waiter, NULL, "g_waiter_thread");
        if (IS_ERR(g_waiter_thread))
            return PTR_ERR(g_waiter_thread);

        msleep(100);
        wake_up_interruptible(&g_wq);

        return 0;
    }

Burada bir çekirdek thread'i yaratılmıştır. Çekirdek thread'inin akışı ``waiter`` fonksiyonundan
başlatılmıştır. Bu fonksiyonda uykuya dalma işlemi şöyle gerçekleştirilmiştir:

.. code-block:: c

    static int waiter(void *data)
    {
        DEFINE_WAIT(wait);

        prepare_to_wait_event(&g_wq, &wait, TASK_INTERRUPTIBLE);
        schedule();
        finish_wait(&g_wq, &wait);

        return 0;
    }

Görüldüğü gibi burada önce ``wait_queue_entry`` nesnesi ``DEFINE_WAIT`` makrosu ile yerel düzeyde
yaratılmıştır. Sonra ``prepare_to_wait_event`` fonksiyonu ile thread bekleme kuyruğuna
yerleştirilmiştir. Bu işlemden sonra da koşul kontrol edilmiş, koşul sağlanmıyorsa ``schedule``
işlemiyle CPU bırakılmıştır. Çıkışta da ``finish_wait`` fonksiyonu ile kuyruktaki
``wait_queue_entry`` bağlı listeden atılmıştır. Örneğimizdeki uyandırma işlemi modülün init
fonksiyonunda aşağıdaki gibi yapılmıştır:

.. code-block:: c

    wake_up_interruptible(&g_wq);

Örneğimizdeki çekirdek modülünü aşağıdaki gibi derleyebilirsiniz:

.. code-block:: console

    $ make file=wait-module

Şöyle yükleyebilirsiniz:

.. code-block:: console

    $ sudo insmod wait-module.ko

``wait-module.c``

.. code-block:: c

    /* wait-module.c */

    #include <linux/kernel.h>
    #include <linux/module.h>
    #include <linux/wait.h>
    #include <linux/kthread.h>
    #include <linux/delay.h>

    static DECLARE_WAIT_QUEUE_HEAD(g_wq);
    static struct task_struct *g_waiter_thread;

    static int waiter(void *data)
    {
        DEFINE_WAIT(wait);

        prepare_to_wait_event(&g_wq, &wait, TASK_INTERRUPTIBLE);
        schedule();   /* Let another thread run; we are blocked */
        finish_wait(&g_wq, &wait);

        return 0;
    }

    static int __init wait_module_init(void)
    {
        printk(KERN_INFO "wait_demo init\n");

        g_waiter_thread = kthread_run(waiter, NULL, "g_waiter_thread");
        if (IS_ERR(g_waiter_thread))
            return PTR_ERR(g_waiter_thread);

        msleep(100);
        wake_up_interruptible(&g_wq);

        return 0;
    }

    static void __exit wait_module_exit(void)
    {
        printk(KERN_INFO "wait_demo: module removed\n");
    }

    module_init(wait_module_init);
    module_exit(wait_module_exit);
    MODULE_LICENSE("GPL");

``Makefile``

.. code-block:: makefile

    obj-m += ${file}.o

    all:
    	make -C /lib/modules/$(shell uname -r)/build M=${PWD} modules
    clean:
    	make -C /lib/modules/$(shell uname -r)/build M=${PWD} clean

Çekirdekte ``prepare_to_wait_event`` fonksiyonunun dışında ona benzeyen biraz daha alçak seviyeli
``prepare_to_wait`` isimli bir fonksiyon da bulunmaktadır. Bu fonksiyonun da parametrik yapısı
aynıdır:

.. code-block:: c

    void prepare_to_wait(struct wait_queue_head *wq_head, 
            struct wait_queue_entry *wq_entry, int state);

İki fonksiyon arasındaki farklar aşağıdaki tabloda özetlenmektedir:

+------------------+--------------------------------------------+--------------------------------------------+
|     Özellik      |          prepare_to_wait_event             |             prepare_to_wait                |
+==================+============================================+============================================+
| Tanım / Amaç     | Bekleme kuyruğuna girmeden önce koşulu     | Süreci wait queue'ya ekler, durumunu       |
|                  | atomik olarak kontrol eder                 | TASK_INTERRUPTIBLE vb. yapar               |
+------------------+--------------------------------------------+--------------------------------------------+
| Dönüş Değeri     | wait_queue_entry_t * döner;                | void — doğrudan dönüş değeri yoktur        |
|                  | sonraki aşamada kullanılır                 |                                            |
+------------------+--------------------------------------------+--------------------------------------------+
| Kilit /          | wq_head->lock spinlock kilidini alır;      | Spinock gerektirmez;                       |
| Senkronizasyon   | çağrılan sırada queue kilidi tutulur       | set_current_state() çağırarak state        |
|                  |                                            | değiştirir                                 |
+------------------+--------------------------------------------+--------------------------------------------+
| Kullanım Sırası  | 1. adım: prepare_to_wait_event çağrılır,   | Basit döngülerde doğrudan çağrılır:        |
|                  | koşul test edilir, schedule ile uyutulur   | add → schedule → finish_wait.              |
+------------------+--------------------------------------------+--------------------------------------------+
| Koşul Kontrolü   | Atomik kontrol dahili — condition true ise | Koşul kontrolü dışarıda; çağıran kodun     |
|                  | queue'ya girmeden döner                    | döngüsü sorumludur                         |
+------------------+--------------------------------------------+--------------------------------------------+
| Spurious Wakeup  | Yerleşik koruma sağlar; sahte uyanmada     | Koruma yoktur; döngü while(condition) ile  |
|                  | koşul yeniden test edilir                  | manuel yazılmalıdır                        |
+------------------+--------------------------------------------+--------------------------------------------+
| Exclusive Destek | WQ_FLAG_EXCLUSIVE bayrağı ile exclusive    | prepare_to_wait_exclusive kardeş           |
|                  | uyuma desteklenir                          | fonksiyonla sağlanır                       |
+------------------+--------------------------------------------+--------------------------------------------+
| Üst Düzey Makro  | wait_event_* makroları bu çağrıyı sarar    | wait_event_* makroları bu çağrıyı sarar    |
+------------------+--------------------------------------------+--------------------------------------------+

Bekleme Kuyrukları Kullanılmadan Thread'lerin Uykuya Yatırılması ve Uyandırılması
=================================================================================

Yukarıdaki anlatımlardan siz bir thread'in ya *çalışma kuyruğunda (run queue)* ya da *bekleme kuyruğunda
(wait queue)* olması gerektiğini sanabilirsiniz. Aslında gerçek durum tam böyle değildir. Thread çalışma
kuyruğundan çıkartılabilir ancak bekleme kuyruğuna da yerleştirilmeyebilir. Bunu sağlamak için önce
thread'in durumunu (state) ``TASK_INTERRUPTIBLE`` olarak ayarlayıp hemen arkasından ``schedule``
fonksiyonunu çağırmak gerekir. Örneğin:

.. code-block:: c

    set_current_state(TASK_INTERRUPTIBLE);
    schedule();

Burada ``set_current_state`` fonksiyonu thread'in durumunu değiştirmek için kullanılmıştır. ``schedule``
fonksiyonu ise bağlamsal geçişi oluşturmaktadır. (Buradaki thread durumunun ``TASK_INTERRUPTIBLE`` olması
gerekmemektedir. ``TASK_INTERRUPTIBLE`` "sinyal geldiğinde thread yeniden CPU'ya atanıp sinyal fonksiyonu
çalıştırılabilir" anlamına gelmektedir.) Tabii konunun ayrıntıları aslında *çizelgeleyici (scheduler)* alt
sistemi ile ilgilidir. Bu konu çizelgeleyici alt sistemin anlatıldığı bölümde ele alınacaktır.

``set_current_state`` fonksiyonu yalnızca ``task_struct`` nesnesindeki ``state`` elemanını güncellemektedir.
(Bu ``state`` elemanı yeni çekirdeklerde "buraya doğrudan erişmeyin" anlamına gelecek biçimde ``__state``
haline getirilmiştir.) Thread çalışma kuyruğundan ``schedule`` fonksiyonu tarafından çıkartılmaktadır.
``schedule`` fonksiyonu içerisinde çağrılan ``deactivate_task`` fonksiyonunda thread'in durumuna bakılır,
durum 0'dan farklı ise (0 değeri ``TASK_RUNNING`` anlamına gelmektedir) thread çalışma kuyruğundan
çıkartılmaktadır.

wake_up_process Fonksiyonu
-------------------------------

Peki thread yukarıdaki gibi çalışma kuyruğundan çıkartıldığında ancak herhangi bir bekleme kuyruğuna da
yerleştirilmediğinde nasıl yeniden çalışma kuyruğuna aktarılacaktır? İşte bu işlem ``wake_up_process``
isimli çekirdek fonksiyonuyla yapılmaktadır. ``wake_up_process`` fonksiyonunun parametrik yapısı şöyledir:

.. code-block:: c

    int wake_up_process(struct task_struct *p);

Fonksiyon başarı durumunda 0 değerine, başarısızlık durumunda negatif errno değerine geri dönmektedir.
``wake_up_process`` fonksiyonu şöyle yazılmıştır:

.. code-block:: c

    int wake_up_process(struct task_struct *p)
    {
        return try_to_wake_up(p, TASK_ALL, 0);
    }
    EXPORT_SYMBOL(wake_up_process);

Fonksiyonun export edildiğine dikkat ediniz. Yani bu fonksiyon çekirdek modülleri ve aygıt sürücüler
tarafından da kullanılabilmektedir. Burada asıl işlemi yapan ``try_to_wake_up`` fonksiyonudur. Bu fonksiyon
export edilmemiştir. ``try_to_wake_up`` fonksiyonunun parametrik yapısı şöyledir:

.. code-block:: c

    static int try_to_wake_up(struct task_struct *p, unsigned int state, int wake_flags);

``wake_up_process`` fonksiyonu ``try_to_wake_up`` fonksiyonunu ``TASK_ALL`` durum parametresiyle
çağırmıştır. Bu durum parametresi "hangi duruma sahip thread'lerin uyandırılacağını" belirtmektedir.
``TASK_ALL`` şöyle define edilmiştir:

.. code-block:: c

    #define TASK_ALL    (TASK_NORMAL | __TASK_STOPPED | __TASK_TRACED)

Çekirdekte ``wake_up_process`` fonksiyonuna benzeyen ancak export edilmemiş ``wake_up_state`` isimli bir
fonksiyon da bulunmaktadır. Bu fonksiyon da şöyle yazılmıştır:

.. code-block:: c

    int wake_up_state(struct task_struct *p, unsigned int state)
    {
        return try_to_wake_up(p, state, 0);
    }

Görüldüğü gibi bu fonksiyon aslında daha geneldir. Yani herhangi bir thread durumunu parametre olarak
alabilmektedir.

Peki bir thread'in çalışma kuyruğundan çıkartılıp hiçbir bekleme kuyruğuna alınmamasının nasıl bir faydası
olabilir? Thread'lerin bekleme kuyruğuna alınmasının da zamansal maliyeti vardır. Bazı durumlarda bu işlemin
yukarıda anlattığımız gibi hiç bekleme kuyrukları karıştırılmadan doğrudan yapılması uygun olabilmektedir.
Gerçekten de çekirdeğin kendisi de bazı durumlarda hiç bekleme kuyruğu kullanmamaktadır. Örneğin
``SIGSTOP`` sinyali ile (ya da terminalden Ctrl+Z tuşuna basılarak) bir proses durdurulduğunda aslında o
proses (prosesin thread'lerini kastediyoruz) çekirdek tarafından herhangi bir bekleme kuyruğuna
yerleştirilmemektedir. Prosese ``SIGCONT`` sinyali gönderildiğinde (ya da terminalden *"fg"* komutu
uygulandığında) doğrudan ``wake_up_state`` fonksiyonu ile proses (prosesin tüm thread'leri) çalışma
kuyruğuna yeniden yerleştirilmektedir.
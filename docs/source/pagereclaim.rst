====================
**Sayfa Geri Alımı**
====================

Bu bölümde ``alloc_pages`` gibi fonksiyonlarla tahsis edilen sayfaların çekirdek tarafından geri alınması sürecini
inceleyeceğiz. Bu konuya genel olarak *sayfa geri alımı (page reclaim)* denilmektedir. Linux çekirdeğinde zaman 
içerisinde sayfa geri alım mekanizması üzerinde sürekli iyileştirmeler yapılmıştır. Biz kursumuzda güncel çekirdeklerdeki g
eri alım mekanizmasını esas alacağız. Aşağıdaki tabloda geri alım mekanizması üzerinde yapılan iyileştirmeleri kronolojik 
bir sıra içerisinde veriyoruz:

.. figure:: _static/page-reclaim-history-table.png
    :align: center
    :width: 60%

Geri Alınabilen ve Geri Alınamayan Sayfalar
===========================================

Çekirdek daha önce incelemiş olduğumuz sayfa önbelleğindeki, ``inode`` ve ``dentry`` önbelleklerindeki sayfaları
bellek baskısı oluşmadan geri almamaktadır. Örneğin bir dosyadan okuma yaptığımızı düşünelim. Dosyadan okunan
bloklar sayfa tahsis edilerek sayfa önbelleğine yerleştirilir. Dosya kapatıldığında dosyaya ilişkin ``inode``
nesnesi ``inode`` önbelleğinde kalmaya, ``inode`` nesnesine ilişkin sayfa önbelleğindeki sayfalar da sayfa
önbelleğinde kalmaya devam eder. Sistem hiçbir sorun yokken yani bellek bolken önbelleklerdeki sayfaları geri almaya
çalışmaz. Gereksiz geri alımın kimseye bir faydası yoktur.

Linux çekirdeğinde geri alıma konu olan önbellekleri aşağıdaki tabloda veriyoruz:

.. figure:: _static/reclaimable-memory-types-table.png
    :align: center
    :width: 60%

Anımsayacağınız gibi Linux'un tahsisat mekanizması fiziksel belleği düğümlere (*nodes*), düğümleri bölgelere (*zones*) 
ve bölgelerdeki ikiz blok düzey listeleri de "göç türlerine (migration types)" ayırıyordu. İkiz blok tahsisat sistemleri 
göç türlerinin içerisindeydi. Ancak sayfa tahsis edilmek istendiğinde *fallback* mekanizması devreye giriyor, bu
mekanizma belli bir bölge ve göç türünden başlayarak önce göç türlerini, sonra bölgeleri, sonra da düğümleri
tarıyordu. Ayrıca çekirdeğin her düğümdeki toplam boş sayfaların sayısını (yani o bölgenin her göç türündeki toplam boş
sayfaların sayısını) da tuttuğunu anımsayınız. (Göç türleri için toplam boş sayfalar çekirdek tarafından
tutulmamaktadır.)

Geri Alım Mekanizması
=====================

Güncel Linux çekirdeklerinde geri alım (*reclaim*) işlemi iki biçimde yapılmaktadır:

| **1.** ``kswapd`` çekirdek thread'i yoluyla
| **2.** Doğrudan tahsisat işleminin kendi akışında (*direct reclaim*)

Linux çekirdeği düğümlerdeki her bölgedeki boş sayfalar için dört *"su seviyesi (watermark)"* tutmaktadır:

.. code-block:: c

    WMARK_PROMO
    WMARK_HIGH
    WMARK_LOW
    WMARK_MIN

Normal durumda genellikle bölgedeki boş sayfaların sayısı ``WMARK_LOW`` ile ``WMARK_HIGH`` arasında olur. Bölgeden
(bölgenin göç türlerinden) sayfa tahsis edildikçe boş sayfaların sayısı azalır. Nihayet ``WMARK_LOW`` sınırına
ulaşır. ``alloc_pages`` gibi sayfa tahsisat fonksiyonları bir bölgedeki boş sayfa sayısı ``WMARK_LOW`` sınırına
düştüğünde (ya da o bölgedeki parçalanmadan dolayı istenilen düzeyde yer bulamayınca) artık o bölgeden tahsisat
yapmayıp *fallback* sürecinde diğer bölgelere geçer. Anımsanacağı gibi bir düğümün bölgeleri bittikten sonra tarama
diğer düğümlerin bölgeleri ile devam etmektedir. Eğer tarama sonunda hiçbir bölgeden tahsisat yapılamamışsa (bunun
sebebi boş sayfa sayısının ``WMARK_LOW`` eşiğinin altına düşmesi olabileceği gibi, parçalanma nedeniyle istenen
düzey büyüklüğünde serbest blok kalmamış olması ya da *cpuset*/kirli sayfa kotası gibi başka nedenler de olabilir)
bu durumda *"yavaş yola"* girilir ve *fallback* listesindeki düğümlerin ``kswapd`` thread'leri uyandırılır.
Çekirdek kodlarında *fallback* listesindeki düğümlerin bölgelerinden tahsisat yapılamadığında girilen yola *"yavaş
yol (slow path)"* de denilmektedir. ``kswapd`` çekirdek thread'inin bu bölgeleri doldurup boş sayfa sayılarını
``WMARK_HIGH`` seviyesinin yukarısına taşıma girişimi zaman alabilmektedir. İşte tahsisatı yapmak isteyen kod
(örneğin tipik olarak ``alloc_pages`` fonksiyonu) *fallback* listesindeki tüm düğümlerin tüm bölgelerinden tahsisat
yapamadığı durumda düğümlerin ``kswapd`` thread'lerini uyandırdıktan sonra kontrol seviyesini ``WMARK_MIN``
seviyesine indirerek gevşetilmiş kısıtlarla yeniden tarama yapmaktadır. Yani bu durumda arka planda ``kswapd``
thread'leri çalışmaktadır fakat tahsisatı yapmak isteyen akış artık ``WMARK_MIN`` seviyesini temel alarak tarama
işlemini yeniden yapmaktadır. Muhtemelen boş sayfa miktarı ``WMARK_LOW`` seviyesinin altında kalan fakat
``WMARK_MIN`` seviyesinin yukarısında kalan bölgeler vardır. Tahsisat artık bu bölgelerden yapılır. Peki düğümlerin
bölgelerindeki boş sayfa sayıları ``WMARK_MIN`` seviyesinin de altına düşmüşse ne olur? ``kswapd`` thread'lerinin
su seviyesini henüz yükseltemediğini varsayalım. İşte bu durumda tahsisat akışı artık ``kswapd``'yi beklemez ve geri
alımı kendisi üstlenir; buna *doğrudan geri alım (direct reclaim)* denir. Doğrudan geri alımda tahsisatı yapan
thread uyutulup başkası tarafından uyandırılmaz, geri alımı bizzat yürütür. 

Doğrudan geri alım işlemi bazı durumlarda hiç yapılmamaktadır. Örneğin ``GFP_ATOMIC`` bayrağı ile tahsisat
yapılırken doğrudan geri alım kodu çalıştırılmadan fonksiyon başarısızlıkla geri döndürülmektedir. Doğrudan geri
alım aynı zamanda *"ben uyuyabilirim"* anlamına gelmektedir. Doğrudan geri alım koduna girilebilmesi için tahsisat
fonksiyonlarında ``__GFP_DIRECT_RECLAIM`` bayrağının bulunuyor olması gerekir. Anımsanacağı gibi ``__GFP_RECLAIM``
bileşik bayrağı ``__GFP_DIRECT_RECLAIM`` bayrağını, ``GFP_KERNEL`` bayrağı da ``__GFP_RECLAIM`` bayrağını
barındırmaktadır. Yani en çok kullanılan bileşke bayrak olan ``GFP_KERNEL`` doğrudan geri alıma izin vermektedir.
Anımsatma amacıyla bileşke bayrakların listesini yeniden veriyoruz:

.. image:: _static/gfp-composite-flags-table.png
   :align: center
   :width: 60%

Peki ``kswapd`` çekirdek thread'leri önbelleklerden ne kadar sayfa koparacaktır? İşte ``WMARK_HIGH`` seviyesi bunu
belirtmektedir. ``kswapd`` bölgeleri doldururken boş sayfa sayıları ``WMARK_HIGH`` seviyesine geldiğinde bunu yeterli
görür daha fazla doldurma yapmaz. Çekirdeğin 5.18 (Mart 2022) versiyonuyla birlikte ``WMARK_PROMO`` denilen bir
seviye de eklenmiştir. ``kswapd`` çekirdek thread'i bazı koşullarda ``WMARK_HIGH`` seviyesinde değil
``WMARK_PROMO`` seviyesinde durmaktadır. Su seviyelerini aşağıdaki şekille de özetlemek istiyoruz:

.. figure:: _static/zone-watermarks.png
    :align: center
    :width: 70%

Yukarıdaki sürecin bazı ayrıntıları da vardır. Biz yukarıda tüm düğümlerdeki bölgelerde ``WMARK_MIN`` seviyesinin
aşağısına düşüldüğünde doğrudan geri alım uygulandığını belirtmiştik. Ancak bazı koşullarda doğrudan geri alım
uygulanmadan ``WMARK_MIN`` seviyesinin de aşağısına inilebilmektedir. Bu konudaki davranış sayfa tahsis edilirken
kullanılan bayraklara da bağlı olarak değişebilmektedir. Aşağıda çeşitli bayraklar için davranışın ayrıntıları
açıklanmaktadır:

.. figure:: _static/alloc-flags-reclaim-behavior-table.png
    :align: center
    :width: 70%

Sayfa tahsisat fonksiyonlarının başarısız olma olasılığı oldukça zayıftır.

Boş sayfalara ilişkin su seviyeleri çekirdekte ``include/linux/mmzone.h`` dosyası içerisinde aşağıdaki ``enum``
türüyle tanımlanmıştır:

.. code-block:: c

    enum zone_watermarks {
        WMARK_MIN,
        WMARK_LOW,
        WMARK_HIGH,
        WMARK_PROMO,
        NR_WMARK
    };

Yukarıda da belirttiğimiz gibi bu seviyeler bölgeleri belirten ``zone`` yapısının içerisinde tutulmaktadır:

.. code-block:: c

    struct zone {
        /* ... */
        unsigned long   _watermark[NR_WMARK];
        /* ... */
    };

``_watermark`` elemanı yukarıdaki seviyeler için geçerli seviye değerlerini tutmaktadır. Her bölgedeki toplam boş
sayfaların sayısı ise ``zone`` yapısının ``vm_stat`` elemanının belirttiği dizinin ``NR_FREE_PAGES`` indeksli elemanında
tutulmaktadır:

.. code-block:: c

    struct zone {
        /* ... */
        unsigned long       _watermark[NR_WMARK];
        atomic_long_t       vm_stat[NR_VM_ZONE_STAT_ITEMS];
        /* ... */
    };

Tabii ``vm_stat`` dizisi yalnızca bölgedeki toplam boş sayfa sayılarını değil başka bilgileri de tutmaktadır. Dizi
elemanlarının tuttuğu bilgilere ilişkin indeksler için ``zone_stat_item`` isimli bir ``enum`` bulundurulmuştur:

.. code-block:: c

    enum zone_stat_item {
        /* First 128 byte cacheline (assuming 64 bit words) */
        NR_FREE_PAGES,
        NR_FREE_PAGES_BLOCKS,
        NR_ZONE_LRU_BASE, /* Used only for compaction and reclaim retry */
        NR_ZONE_INACTIVE_ANON = NR_ZONE_LRU_BASE,
        NR_ZONE_ACTIVE_ANON,
        NR_ZONE_INACTIVE_FILE,
        NR_ZONE_ACTIVE_FILE,
        NR_ZONE_UNEVICTABLE,
        NR_ZONE_WRITE_PENDING,  /* Count of dirty, writeback and unstable pages */
        NR_MLOCK,               /* mlock()ed pages found and moved off LRU */
        /* Second 128 byte cacheline */
    #if IS_ENABLED(CONFIG_ZSMALLOC)
        NR_ZSPAGES,             /* allocated in zsmalloc */
    #endif
        NR_FREE_CMA_PAGES,
    #ifdef CONFIG_UNACCEPTED_MEMORY
        NR_UNACCEPTED,
    #endif
        NR_VM_ZONE_STAT_ITEMS
    };

Yukarıda da belirttiğimiz gibi ``vm_stat`` dizisinin ``NR_FREE_PAGES`` indeksli (0'ıncı indeksli) elemanında
bölgedeki toplam boş sayfaların sayısı tutulmaktadır. Bu değeri ``/proc/zoneinfo`` dosyasında *"pages free"*
satırından da görüntüleyebilirsiniz.

Biz bölgeleri incelerken bölgelerdeki ikiz blok sisteminin düzey listelerinin göç türlerinden oluştuğunu
belirtmiştik. Anımsanacağı gibi ikiz blok düzey listeleri ``zone`` yapısının ``free_area`` elemanında saklanıyordu:

.. code-block:: c

    struct zone {
        /* ... */
        unsigned long       _watermark[NR_WMARK];
        struct free_area    free_area[NR_PAGE_ORDERS];
        atomic_long_t       vm_stat[NR_VM_ZONE_STAT_ITEMS];
        /* ... */
    };

Buradaki ``free_area`` elemanının ``free_area`` isimli bir yapı türünden olduğunu belirtmiştik:

.. code-block:: c

    struct free_area {
        struct list_head    free_list[MIGRATE_TYPES];
        unsigned long       nr_free;
    };

İşte bu yapıdaki ``nr_free`` elemanı her düzey için toplam boş sayfa sayısını tutmaktadır. Bu durumda su seviyesi
(*watermark*) kontrolünü çekirdek ``zone`` nesnesinden hareketle iki aşamada yapmaktadır: Çekirdek önce ``zone``
nesnesindeki toplam boş sayfa sayısına bakar (bu ana şalter görevindedir), eğer toplam boş sayfa sayısı talep
edilen miktarı barındırıyorsa bu durumda hangi ikiz blok tahsisat düzeyinden tahsisat yapılacaksa ayrıca o
``free_area`` içerisindeki ``nr_free`` elemanını da kontrol eder.

Burada bir noktayı yeniden vurgulamak istiyoruz: *Fallback* mekanizması altında düğümlerin birden fazla bölgesi
taranmaktadır. Bir düğümün taranan bölgelerinin hepsinde ``WMARK_LOW`` altına düşülmüşse o düğüm için ``kswapd``
çekirdek thread'i uyandırılıp tarama diğer düğümlerle devam ettirilmektedir.

kswapd Çekirdek Thread'lerinin Uyguladığı Geri Alım İşlemleri
=============================================================

Şimdi de ``kswapd`` thread'leri tarafından geri alımın nasıl yapıldığı üzerinde duralım. Anımsanacağı gibi ``kswapd``
thread'leri zamanının önemli bölümünü uykuda geçirmektedir. Bunlar yukarıda belirttiğimiz koşullar oluşunca
tahsisat fonksiyonları tarafından uyandırılmaktadır. Bu thread'ler düğüm belirten ``pglist_data`` yapısının
``kswapd_wait`` bekleme kuyruğunu kullanmaktadır. Düğümü temsil eden ``pglist_data`` yapısının ``kswapd`` ile ilgili
elemanlarını aşağıda veriyoruz:

.. code-block:: c

    typedef struct pglist_data {
        /* ... */
        struct task_struct  *kswapd;
        wait_queue_head_t   kswapd_wait;                /* bekleme kuyruğu */
        wait_queue_head_t   pfmemalloc_wait;            /* kısma (throttle) bekleme kuyruğu */
        int                 kswapd_order;               /* istenen düzey */
        enum zone_type      kswapd_highest_zoneidx;
        int                 kswapd_failures;            /* ardışık başarısızlık sayacı */
        /* ... */
    } pg_data_t;

Aşağıdaki tabloda bu elemanların işlevlerini özetliyoruz:

.. figure:: _static/kswapd-pgdat-fields-table.png
    :align: center
    :width: 60%

``kswapd`` thread'lerinin çalışma biçimleri oldukça ayrıntılıdır. Ancak kabaca bu *thread*'ler geri alımlar için
aşağıdaki iki işlemi yapmaktadır:

| **Evre-1:** ``inode`` nesnelerinin sayfa önbelleklerindeki sayfaları geri alırlar.

| **Evre-2:** Kullanılmayan ``inode`` nesnelerinin yok edilmelerini sağlarlar ve çekirdekteki dilim önbelleklerinden
    (``inode`` önbelleği, ``dentry`` önbelleği gibi) tahsis edilmiş ve artık kullanılmayan nesnelerin sistemden
    çıkartılarak (*evict* edilerek) dilim önbelleğine iade edilmesine önayak olurlar. Ancak ``kswapd`` thread'leri
    bunların dışında sistemdeki tüm büzücüleri (*shrinkers*) de işleme sokmaktadır.

Biz birinci evreye *"sayfa geri alımı (page reclaim)"*, ikinci evreye ise *"dilim geri alımı (slab reclaim)"*
diyeceğiz. Aşağıda birinci ve ikinci işlemi "evre 1" ve "evre 2" diye isimlendirerek ayrıntılı akışı veriyoruz:

.. figure:: _static/shrink-node-call-tree.png
    :width: 80%

Bu akışı şekilsel olarak da şöyle betimleyebiliriz:

.. figure:: _static/reclaim-phases-flow.png
    :align: center
    :width: 100%

Evre-1: Sayfa Geri Alımı
------------------------

Şimdi *"Evre-1"* üzerinde duralım. Sayfa önbelleğindeki sayfaların geri alım süreci zaman içerisinde iyileştirilmiş
ve geliştirilmiştir. Güncel çekirdeklerde bu *"Evre-1"* işlemleri ``shrink_lruvec`` fonksiyonu tarafından
yapılmaktadır. Çekirdeğin bu konudaki evrimini aşağıdaki tabloyla özetlemek istiyoruz:

.. figure:: _static/lru-evolution-table.png
    :align: center
    :width: 55%

Geri alım için geri alımı yapılabilecek olan (her sayfanın geri alımının mümkün olmadığını anımsayınız) sayfalar 
LRU listelerinde tutulmaktadır. LRU listelerinde tutulan sayfalar şunlardır:

* Anonim sayfalar (*heap*, *stack*, *private mapping*'ler, *copy-on-write (COW)* kopyaları).
* Sayfa önbelleğindeki sayfalar (dosya içeriği taşıyan sayfalar, ``mmap`` edilmiş olsun ya da olmasın).
* *shmem/tmpfs* sayfaları (çekirdek bunları *anon* gibi takasa çıkarabilir ama sayfa önbelleğinde tutar).
* *takas önbelleğindeki* sayfalar (akas önbelleğini takas işlemlerini anlattığımız bölümde ele alacağız).
    
Şunlar LRU listelerinde değildir:

* Dilim önbelleğine ilişkin sayfalar. (Yani ``kmem_cache_alloc`` ve dolayısıyla ``kmalloc`` ile tahsis edilmiş olan sayfalar.)
* Sayfa tablolarına ilişkin sayfalar.
* Çekirdek *stack* alanları.
* ``vmalloc`` ve türevileri ile tahsis edilen (yani ``vmalloc`` alanında tahsis edilen) sayfalar).
* İkiz blok tahsisat sisteminde boşta duran sayfalar.
* *Reserved* olarak işaretlenmiş sayfalar.

Bunların bir kısmı hiç geri alınamaz; dilim önbelleğindeki olanlar ise LRU üzerinden değil Evre-2'de açıklayacağımız 
*büzücüler (shrinkers)* yoluyla küçültülmektedir.

Güncel çekirdeklerde sayfalara ilişkin LRU listeleri eğer ``CONFIG_MEMCG`` konfigürasyon seçeneği aktif değilse
``pglist_data`` nesnesinde, aktifse ``mem_cgroup`` nesnesinin içerisinde tutulmaktadır:

.. figure:: _static/lruvec-location.png
    :width: 60%

Biz daha önce de *memory cgroup* kavramından bellek yönetiminde üstünkörü bahsetmiştik. Bu mekanizma *docker* gibi
*container* teknolojilerinin gerçekleştirilmesi için diğer *cgroup* mekanizmalarıyla birlikte kullanılmaktadır. Biz
kursumuzda *"container"* oluşturabilmek için gereken çekirdek altyapısını ayrı bir bölümde ele alacağız. LRU
listelerinin tutulduğu yeri ve bunlara erişim fonksiyonlarını aşağıda bir tablo halinde de veriyoruz:

.. figure:: _static/lruvec-location-api-table.png
    :align: center
    :width: 70%

``pglist_data`` yapısının ``__lruvec`` elemanı sayfalar için LRU listelerini tutmaktadır:

.. code-block:: c

    typedef struct pglist_data {
        /* ... */

        struct lruvec           __lruvec;

        /* ... */
    } pg_data_t;

``lruvec`` yapısı şöyle tanımlanmıştır:

.. code-block:: c

    struct lruvec {
        struct list_head            lists[NR_LRU_LISTS];
        /* per lruvec lru_lock for memcg */
        spinlock_t                  lru_lock;
        /*
         * These track the cost of reclaiming one LRU - file or anon -
         * over the other. As the observed cost of reclaiming one LRU
         * increases, the reclaim scan balance tips toward the other.
         */
        unsigned long               anon_cost;
        unsigned long               file_cost;
        /* Non-resident age, driven by LRU movement */
        atomic_long_t               nonresident_age;
        /* Refaults at the time of last reclaim cycle */
        unsigned long               refaults[ANON_AND_FILE];
        /* Various lruvec state flags (enum lruvec_flags) */
        unsigned long               flags;
    #ifdef CONFIG_LRU_GEN
        /* evictable pages divided into generations */
        struct lru_gen_folio        lrugen;
    #ifdef CONFIG_LRU_GEN_WALKS_MMU
        /* to concurrently iterate lru_gen_mm_list */
        struct lru_gen_mm_state     mm_state;
    #endif
    #endif /* CONFIG_LRU_GEN */
    #ifdef CONFIG_MEMCG
        struct pglist_data *pgdat;
    #endif
        struct zswap_lruvec_state zswap_lruvec_state;
    };

Yapının ``lists`` elemanına dikkat ediniz:

.. code-block:: c

    struct list_head    lists[NR_LRU_LISTS];

Bu eleman LRU listelerini tutmaktadır. Ancak gördüğünüz gibi LRU listeleri bir tane değildir. LRU listelerinin türleri
``lru_list`` isimli ``enum`` türünün içerisinde belirtilmektedir:

.. code-block:: c

    enum lru_list {
        LRU_INACTIVE_ANON = LRU_BASE,
        LRU_ACTIVE_ANON = LRU_BASE + LRU_ACTIVE,
        LRU_INACTIVE_FILE = LRU_BASE + LRU_FILE,
        LRU_ACTIVE_FILE = LRU_BASE + LRU_FILE + LRU_ACTIVE,
        LRU_UNEVICTABLE,
        NR_LRU_LISTS
    };

Bu bağlı liste türlerini aşağıda tablo halinde de gösterebiliriz:
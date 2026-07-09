
===============================================================
Bellek Yönetimi - 2. Bölüm :raw-html:`<br>` Tahsisat İşlemleri
===============================================================

Bu bölümde Linux çekirdeğinin sayfa düzeyindeki ve byte düzeyindeki tahsisat mekanizmalarını ele
alacağız. Bölüm içerisinde önce çekirdeğin boş sayfaları nasıl belirlediğini ve sayfa düzeyinde
tahsisatları nasıl yaptığını açıklayacağız. Sonra da byte düzeyindeki tahsisat işlemleri üzerinde
duracağız.

Linux çekirdeğinde iki düzeyli tahsisat sistemi vardır:

1. Sayfa düzeyinde tahsisat sistemi (*buddy allocator*)
2. Byte düzeyinde tahsisat sistemi (*slab allocator*)

Linux çekirdeğindeki sayfa düzeyinde tahsisat sistemine *ikiz blok tahsisat sistemi* ya da
İngilizcesiyle *buddy allocator*, byte düzeyinde tahsisat sistemine ise *dilimli tahsisat sistemi*
ya da İngilizcesiyle *slab allocator* denilmektedir.

İkiz Blok Tahsisat Sistemi (Buddy Allocator)
============================================

Çekirdek tüm fiziksel sayfaları bir heap alanıymış gibi ele alıp onların tahsisatlarını yönetmektedir.
Fiziksel sayfaları temsil eden ``page`` nesneleri ilgili sayfanın tahsis edilip edilmediği gibi bilgileri
de tutmaktadır. Biz bir aygıt sürücü yazarken ya da çekirdeğe bir modül eklerken bir fiziksel sayfayı
doğrudan kullanamayız. Çünkü o sayfa başka amaçlarla başka kaynaklar tarafından kullanılıyor olabilir.
Biz önce sayfa düzeyinde tahsisat yapan fonksiyonlarla sayfayı tahsis edip ondan sonra o sayfayı
kullanabiliriz. Yukarıda da belirttiğimiz gibi Linux çekirdeğinde sayfa düzeyinde tahsisat yapan bir
tahsisat sistemi bulunmaktadır. Biz bu sisteme Türkçe *ikiz blok tahsisat sistemi* diyeceğiz. Bu sistemin
İngilizce ismi *buddy allocator* biçimindedir. İzleyen paragraflarda ikiz blok tahsisat sisteminin
algoritmik yapısını açıklayacağız.

İşletim sistemlerinde sayfa düzeyinde tahsisatların hızlı yapılması gerekir. Aynı zamanda sayfa tahsisat
sisteminin mümkün olduğunca bellek bölünmesi (*fragmentation*) olgusuna dirençli olması da istenir. İkiz
blok tahsisat sistemi ilk kez Knowlton tarafından ortaya atılmıştır. Knowlton bu algoritmayı 1965 yılında
*Communications of the ACM* dergisinde *A Fast Storage Allocator* başlıklı makalesinde açıklamıştır. Bu
sistem Linux çekirdeklerine 1.2 versiyonuyla (1995) eklenmiştir. Linux çekirdeklerinde zamanla ikiz blok 
tahsisat sistemi daha karmaşık hale getirilmiştir. Bu karmaşıklık tahsisat algoritmasının kendisinden değil 
*boş listelerin (free lists)* ve bölgelerin (zones) *fallback* denilen gözden geçirilmesi mekanizmasından 
kaynaklanmaktadır. Biz burada önce ikiz blok tahsisat sisteminin algoritmik yapısını açıklayacağız sonra 
Linux çekirdeğindeki gerçekleştirimi üzerinde
duracağız.

İkiz Blok Tahsisat Sisteminin Algoritmik Yapısı
------------------------------------------------

İkiz blok tahsisat sisteminde boş bloklar 2'nin kuvvetlerine ilişkin ardışıl fiziksel sayfalardan oluşan
bloklar biçiminde organize edilmektedir. Buradaki 2'nin kuvvetine ilişkin boş blok listelerine İngilizce
*order* denilmektedir. Biz *order* sözcüğü yerine Türkçe *düzey* sözcüğünü kullanacağız. Aşağıda 5
düzeyli bir ikiz blok sisteminin çizimi yapılmıştır:

.. image:: _static/buddy-levels.png
   :align: center
   :width: 70%

Tabii buradaki listeler boş sayfa listeleridir. Tahsis edilen sayfalar bu listelerden çıkartılmaktadır.
Tahsisat her zaman 2ⁿ sayfa olacak biçimde düzey belirtilerek yapılmaktadır. Örneğin 4 sayfanın (2²
sayfanın) tahsis edilmek istendiğini düşünelim. Tahsisat 2'inci düzeydeki boş listeden sağlanacaktır.
Peki ya istenilen düzeyde hiç boş sayfa bloğu yoksa ne olur? İşte bu durumda daha yüksek düzeylere
başvurulup onlar parçalanmaktadır. Örneğin 2'inci düzeyde boş sayfa bloğu bulunmuyor olsun. Algoritma
bu durumda 3'üncü düzeye bakar. Eğer 3'üncü düzeyde 8 sayfalık boş bir sayfa bloğu varsa onu 2 parçaya
ayırır. Parçalardan birini 2'inci düzeydeki sayfa bloğu listesine ekler, diğerini verir. Peki biz sayfa
tahsis etmek istediğimizde 2'inci düzeyde de 3'üncü düzeyde de boş sayfa bloğu yoksa ne olacaktır? İşte
bu durumda gittikçe yukarı çıkılır, ilk boş sayfa bloğu olan düzeyden blok tahsis edilir. Sonra blok
bölüne bölüne aşağıya inilir. Örneğin 4 sayfa tahsis etmek istediğimizde 3'üncü düzeyde boş sayfa bloğu
yoksa ancak 4'üncü düzeyde boş sayfa bloğu varsa bu düzeydeki 16 sayfalık blok yarıya bölünür. Bunun
8'lik kısmı 3'üncü düzeydeki boş listeye eklenir, diğer 8'lik kısmı yine bölünür, onun 4'lük kısmı
2'inci düzey listeye eklenir, diğeri de tahsis edilir. Şimdi bu süreci şekillerle adım adım gösterelim.
Başlangıç durumu şöyledir:

.. image:: _static/buddy-initial.png
   :align: center
   :width: 60%

2'inci düzeyde ve 3'üncü düzeyde boş sayfa bloğu olmadığı için 4'üncü düzeydeki boş sayfa bloklarının
biri alınıp bölünür. Bölünen bloklar 8 sayfalık olacaktır. Bunlardan biri 3'üncü düzeydeki boş listeye
eklenir, diğeri bölünmeye devam eder:

.. image:: _static/buddy-split-step1.png
   :align: center
   :width: 70%

Burada 3'üncü düzeydeki 8 sayfanın yeniden ikiye bölünmesiyle bunlardan biri 2'inci düzeydeki boş listeye eklenir:

.. image:: _static/buddy-split-step2.png
   :align: center
   :width: 70%

İşte 8 sayfanın 4'lük kısmı 2'inci düzeydeki bağlı listeye eklenip kalan 4'lük kısmı da çağrıyı yapana verilmektedir. 
Boş listelerin son hali şöyle olacaktır:

.. image:: _static/buddy-final-state.png
   :align: center
   :width: 70%

Peki tahsis edilen bu 4 sayfalık blok free hale getirildiğinde ne olmaktadır? İşte algoritma bu durumda
tersten işletilmektedir. Yani bu 4 sayfalık blok 2'inci düzeye yerleştirilir. Ancak bu 2'inci düzeyde onun
*ikizi (buddy'si)* varsa free hale getirilenle bu ikizi birleştirilerek üst düzeydeki boş listeye eklenir.
Tabii aynı durum üst düzey için de yapılacaktır. Burada bir noktaya dikkatinizi çekmek istiyoruz: Free hale
getirme algoritmasından amaç en yüksek sayfa içeren ardışıl bloğun oluşturulmasıdır. Free edilen blokla onun
*ikizinin (buddy'sinin)* birleştirilip üst bloğa taşınmasının temel amacı budur. Şimdi bu birleştirme işlemini
yine adım adım gösterelim. Free işlemi öncesindeki durum şöyledir:

Şimdi 4 sayfalık bloğu free hale getirelim. Algoritma önce bu bloğu 2'inci düzeye eklerken onun ikizi (buddy'si)
o düzeyde var mı diye bakar. Eğer varsa onları birleştirip bir yukarıdaki düzeye eklemeye çalışır. Bizim örneğimizde
onun ikizi 2'inci düzeyde bulunmaktadır:

.. image:: _static/buddy-coalesce.png
   :align: center
   :width: 70%

Birleştirme sonucunda şu durum oluşacaktır:

.. image:: _static/buddy-coalesce-lv3.png
   :align: center
   :width: 70%

İşte 3'üncü düzeyde de birleştirilmiş bloğun ikizi bulunduğu için o ikiz blok da birleştirilip üst boş blok listesine
(4'üncü düzeydeki boş blok listesine) yerleştirilecektir:

.. image:: _static/buddy-final-merge.png
   :align: center
   :width: 70%

Görüldüğü gibi her şey ters sırada eski haline gelmiştir. 

Linux çekirdeklerinde maksimum düzey ``include/linux/mmzone.h`` dosyasındaki ``MAX_ORDER`` sembolik
sabitiyle belirtiliyordu. Ancak en son çekirdeklerde (>= 6.8) artık ``MAX_ORDER`` yerine aşağıdaki
iki sembolik sabit kullanılmaya başlanmıştır:

.. code-block:: c

   #define MAX_PAGE_ORDER    10                       /* en yüksek düzey indeksi  */
   #define NR_PAGE_ORDERS    (MAX_PAGE_ORDER + 1)     /* listelerin sayısı = 11   */

``MAX_PAGE_ORDER`` maksimum düzeyin indeks numarasını, ``NR_PAGE_ORDERS`` ise bunların sayısını
belirtmektedir. Linux çekirdeklerinde maksimum düzey 10'dur. (Yani toplam 11 tane düzey listesi
bulunmaktadır.) 6.1 çekirdeği ve öncesinde ``MAX_ORDER`` toplam liste sayısını belirtirken, daha
sonra en yüksek düzey indeksini belirtir hale getirilmiştir. Nihayet yukarıda da belirttiğimiz gibi
6.8 ile birlikte bu sembolik sabitlerin isimleri değiştirilmiştir.

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Versiyon
     - Durum
   * - ≤ 6.1
     - ``MAX_ORDER = 11``; maksimum düzey indeksi 10.
   * - 6.2 – 6.7
     - ``MAX_ORDER = 10``; anlam düzeltildi (artık indeks numarasını belirtiyor).
   * - ≥ 6.8
     - ``MAX_ORDER`` kaldırıldı → ``MAX_PAGE_ORDER = 10``, ``NR_PAGE_ORDERS = 11``.

Linux çekirdeklerinde en yüksek düzey 10 olduğuna göre ve 2\ :sup:`10` = 1024 olduğuna göre, en
yüksek düzeydeki sayfa blokları 1024 sayfadan oluşmaktadır. 1024 sayfa da 4 MB yer kaplamaktadır.

Bellek Bölgeleri ve Göç Türleri
-------------------------------

Biz yukarıda ikiz blok tahsisat sisteminin temel algoritmasını açıkladık. Ancak Linux çekirdeğinde ikiz blok
tahsisat sistemi bir tane değildir. Her NUMA düğümü bellek bölgelerinden (memory zones), her bellek bölgesi
de göç türlerine (migration types) ilişkin ikiz blok tahsisat sistemlerinden (buddy allocators)
oluşmaktadır. Yani bir bellek bölgesinde bile birden fazla ikiz blok tahsisat sistemi bulunmaktadır.

.. figure:: _static/numa-buddy-node0.png
   :alt: NUMA Düğümü 0 — Zone ve göç türü hiyerarşisi
   :align: center
   :width: 80%

.. figure:: _static/numa-buddy-node1.png
   :alt: NUMA Düğümü 1 — Zone ve göç türü hiyerarşisi
   :align: center
   :width: 80%

Görüldüğü gibi NUMA düğümleri bellek bölgelerinden, bellek bölgeleri ise göç türlerine göre birden fazla
ikiz blok tahsisat sisteminden oluşmaktadır.

NUMA düğümleri içerisindeki her bölgenin *zone* isimli bir yapıyla temsil edildiğini belirtmiştik.
İşte ``zone`` yapısının ``free_area`` elemanı o bölgedeki ikiz blok tahsisat sistemlerini
tutmaktadır:

.. code-block:: c

   struct zone {
       /* ... */

       struct free_area  free_area[NR_PAGE_ORDERS];
       int               nr_zones;

       /* ... */
   };

Görüldüğü gibi ``free_area`` dizisi *free_area* isimli yapı türündendir ve uzunluğu maksimum düzey
sayısına eşittir. (Yani dizi 11 elemanlıdır; ilk elemanı 0'ıncı düzeyi, son elemanı 10'uncu düzeyi
belirtmektedir.)

``free_area`` yapısı şöyle bildirilmiştir:

.. code-block:: c

   struct free_area {
       struct list_head  free_list[MIGRATE_TYPES];
       unsigned long     nr_free;
   };

Görüldüğü gibi ``free_area`` aslında her göç türü için bağlı listelerden oluşmaktadır. Aşağıdaki
şekil bu veri yapısını daha iyi anlaşılmasına yardımcı olacaktır:

.. code-block:: text

   zone (örn. ZONE_NORMAL):
   │
   ├── free_area[0]   (düzey-0, 4 KB bloklar)
   │   ├── free_list[MIGRATE_UNMOVABLE]   → [pg1] → [pg4] → [pg9] → NULL
   │   ├── free_list[MIGRATE_MOVABLE]     → [pg2] → [pg7] → NULL
   │   ├── free_list[MIGRATE_RECLAIMABLE] → [pg3] → NULL
   │   ├── free_list[MIGRATE_HIGHATOMIC]  → NULL
   │   ├── free_list[MIGRATE_CMA]         → NULL
   │   └── free_list[MIGRATE_ISOLATE]     → NULL
   │
   ├── free_area[1]   (düzey-1, 8 KB bloklar)
   │   ├── free_list[MIGRATE_UNMOVABLE]   → [pg16,17] → NULL
   │   ├── free_list[MIGRATE_MOVABLE]     → [pg32,33] → [pg64,65] → NULL
   │   └── ...
   │
   ├── free_area[2]   (düzey-2, 16 KB bloklar)
   │   └── ...
   │
   ...
   │
   └── free_area[10]  (düzey-10, 4 MB bloklar)
       └── ...

Buradaki ``free_area``'nın düzeylerden oluşan bir dizi olduğuna, dizinin her elemanının her göç türü
için ayrı listeler barındırdığına dikkat ediniz. ``free_area`` listesinin her elemanı aslında bir
bağlı liste dizisidir. ``free_area[n]`` bağlı liste dizisi *n*'inci düzeyin her göç türü için bağlı
listelerini tutmaktadır. (Örneğin ``free_area[0]`` bağlı liste dizisi her göç türü için 0'ıncı
düzeyin bağlı listelerini, ``free_area[1]`` bağlı liste dizisi her göç türü için 1'inci düzeyin
bağlı listelerini tutmaktadır.) Göç türlerinin ne amaçla kullanıldığını izleyen paragraflarda
açıklayacağız.

Güncel çekirdeklerde ``free_area`` nesnelerinin içerisindeki ``free_list`` bağlı listeleri
``buddy_list`` elemanı yoluyla *page* nesnelerini tutar durumdadır:

.. code-block:: c

   struct page {
       memdesc_flags_t flags;

       union {
           struct {
               union {
                   /* ... */

                   struct list_head buddy_list;  /* free_list tarafından kullanılan düğüm */

                   /* ... */
               };

               /* ... */
           };

           /* ... */
       }
   } _struct_page_alignment;

Sayfa Tahsisat Fonksiyonları
----------------------------

``alloc_pages`` fonksiyonu ikiz blok tahsisat sisteminden sayfa tahsis eden en temel
fonksiyondur. Fonksiyonun parametrik yapısı şöyledir:

.. code-block:: c

    struct page *alloc_pages(gfp_t gfp_mask, unsigned int order);

``alloc_pages`` eskiden ``include/linux/gfp.h`` dosyasında ``CONFIG_NUMA`` konfigürasyon
parametresine göre makro ya da inline fonksiyon biçiminde tanımlanıyordu. Ancak daha sonra
makro haline getirilmiştir.

``alloc_pages`` fonksiyonun birinci parametresi tahsisatın nereden yapılacağını belirtmektedir.
İkinci parametresi ise tahsisat için düzey belirtmektedir. (Yani örneğin 1 sayfa tahsis
edilecekse bu parametre 0, iki sayfa tahsis edilecekse 1, 4 sayfa tahsis edilecekse 2
girilmelidir.) Fonksiyonun birinci parametresindeki ``gfp_t`` türü tipik olarak ``unsigned int``
biçiminde typedef edilmektedir. Bu parametreye çeşitli mask bayrakları bit düzeyinde OR işlemine
sokularak verilmektedir. Mask bayrakları ``include/linux/gfp_types.h`` dosyası içerisinde
define edilmiştir. Bunları aşağıda bir tablo biçiminde veriyoruz:

.. list-table:: 
   :header-rows: 1

   * - Bayrak Adı
     - İşlevi
   * - ``__GFP_DMA``
     - Tahsisatı ZONE_DMA'dan yap (eski ISA DMA uyumu için)
   * - ``__GFP_HIGHMEM``
     - Tahsisatı ZONE_HIGHMEM'den yap
   * - ``__GFP_DMA32``
     - Tahsisatları 32-bit adreslenebilir ZONE_DMA32'den yap
   * - ``__GFP_MOVABLE``
     - ZONE_MOVABLE'a izin ver; sayfa göç ile taşınabilir
   * - ``__GFP_RECLAIMABLE``
     - Sayfa shrinker'lar aracılığıyla geri alınabilir (dilim için)
   * - ``__GFP_WRITE``
     - Sayfa kirletilecek; bölgeler arasında dağıtılır (fair policy)
   * - ``__GFP_HARDWALL``
     - cpuset bellek tahsisat politikasını zorla uygula
   * - ``__GFP_THISNODE``
     - Yalnızca belirtilen NUMA düğümlerini ayır, fallback yok
   * - ``__GFP_ACCOUNT``
     - Tahsisatı kmemcg'ye hesapla (kernel memory cgroup)
   * - ``__GFP_HIGH``
     - Yüksek öncelikli; atomic rezervlere erişebilir
   * - ``__GFP_MEMALLOC``
     - Tüm belleğe (rezervler dahil) erişime izin ver
   * - ``__GFP_NOMEMALLOC``
     - Acil rezervlere erişimi açıkça yasakla
   * - ``__GFP_IO``
     - Bellek geri almak için fiziksel I/O başlatabilir
   * - ``__GFP_FS``
     - Bellek geri almak için dosya sistemi çağrısı yapabilir
   * - ``__GFP_DIRECT_RECLAIM``
     - Çağıran doğrudan geri alıma girebilir
   * - ``__GFP_KSWAPD_RECLAIM``
     - Low watermark'ta kswapd'yi uyandırabilir
   * - ``__GFP_RECLAIM``
     - ``__GFP_DIRECT_RECLAIM | __GFP_KSWAPD_RECLAIM`` kısayolu
   * - ``__GFP_RETRY_MAYFAIL``
     - İlerleme varsa geri alımı tekrar dene; OOM'u tetiklemez
   * - ``__GFP_NOFAIL``
     - Sonsuz yineleme; asla başarısız olamaz, bloke olabilir
   * - ``__GFP_NORETRY``
     - Yalnızca hafif geri alım dene; "OOM killer" çağrılmaz
   * - ``__GFP_NOWARN``
     - Ayırma başarısız olursa çekirdek uyarı mesajını bastır
   * - ``__GFP_COMP``
     - Bileşik sayfalar için metadata ekle (büyük sayfa grupları için)
   * - ``__GFP_ZERO``
     - Başarılı tahsisatlarda sıfırlanmış sayfa döndür
   * - ``__GFP_ZEROTAGS``
     - Bellek sıfırlanırken KASAN HW bellek etiketlerini de sıfırla
   * - ``__GFP_SKIP_ZERO``
     - KASAN HW etiket sıfırlamasını atla
   * - ``__GFP_SKIP_KASAN``
     - KASAN sayfa zehirleme/çözme kontrollerini atla
   * - ``__GFP_NOLOCKDEP``
     - GFP context takibi için lockdep denetimini devre dışı bırak

Linux çekirdek kodlamasında başı ``__`` ile başlayan değişkenlerin "aşağı seviyeli kodlar
tarafından kullanıldığını" anımsayınız. Yukarıdaki bayraklar ince ayar için kullanılmaktadır.
Bunların her bileşimi anlamlı değildir. Yani örneğin bazı bayraklar bazı bayraklarla
kullanılamamaktadır. Aslında çekirdek içerisinde yukarıdaki bayraklar kullanılarak oluşturulmuş
başı ``__`` ile başlamayan daha yüksek seviyeli bayraklar da vardır. Bunların listesini de
aşağıdaki tabloda veriyoruz:

.. list-table:: 
   :width: 70%
   :header-rows: 1
  
   * - Kompozit Bayrak Adı
     - Bileşen Bayraklar
   * - ``GFP_ATOMIC``
     - ``__GFP_HIGH | __GFP_KSWAPD_RECLAIM``
   * - ``GFP_KERNEL``
     - ``__GFP_RECLAIM | __GFP_IO | __GFP_FS``
   * - ``GFP_KERNEL_ACCOUNT``
     - ``GFP_KERNEL | __GFP_ACCOUNT``
   * - ``GFP_NOWAIT``
     - ``__GFP_KSWAPD_RECLAIM``
   * - ``GFP_NOIO``
     - ``__GFP_RECLAIM``
   * - ``GFP_NOFS``
     - ``__GFP_RECLAIM | __GFP_IO``
   * - ``GFP_USER``
     - ``__GFP_RECLAIM | __GFP_IO | __GFP_FS | __GFP_HARDWALL``
   * - ``GFP_HIGHUSER``
     - ``GFP_USER | __GFP_HIGHMEM``
   * - ``GFP_HIGHUSER_MOVABLE``
     - ``GFP_HIGHUSER | __GFP_MOVABLE | __GFP_SKIP_KASAN``
   * - ``GFP_DMA``
     - ``__GFP_DMA``
   * - ``GFP_DMA32``
     - ``__GFP_DMA32``
   * - ``GFP_TRANSHUGE``
     - ``GFP_HIGHUSER_MOVABLE | __GFP_COMP | __GFP_NOMEMALLOC |``
       ``__GFP_NORETRY | __GFP_NOWARN | __GFP_KSWAPD_RECLAIM``
   * - ``GFP_TRANSHUGE_LIGHT``
     - ``GFP_HIGHUSER_MOVABLE | __GFP_COMP | __GFP_NOMEMALLOC |``
       ``__GFP_NORETRY | __GFP_NOWARN``

Programcılar genellikle bu yüksek seviyeli bayrakları kullanmaktadır. Örneğin ``GFP_ATOMIC``,
``GFP_KERNEL``, ``GFP_USER``, ``GFP_DMA``, ``GFP_DMA32`` en çok kullanılan yüksek seviyeli
bayraklardır. Biz bu bayraklar hakkında izleyen paragraflarda daha fazla bilgi vereceğiz.

``alloc_pages`` fonksiyonu başarı durumunda tahsis edilen sayfaların ilkine ilişkin ``page``
yapı nesnesinin adresiyle, başarısızlık durumunda ``NULL`` adresle geri dönmektedir.
Anımsanacağı gibi zaten çekirdek tüm sayfaları doğrudan ya da dolaylı biçimde bir dizi
içerisinde tutmaktadır. ``alloc_pages`` bize ilgili ``page`` nesnesinin bu dizideki adresini
vermektedir. Burada bize verilen ``page`` adresini biz ilerleterek ilgili dizinin sonraki
elemanına erişiriz. İkiz blok tahsisat sisteminde her zaman fiziksel bellekte ardışıl fiziksel
sayfaların tahsis edildiğini anımsayınız. Tabii ``alloc_pages`` fonksiyonun bize verdiği adres
sanal adrestir. Anımsanacağı gibi bir ``page`` nesnesinin adresi bilindiğinde bunun fiziksel
bellekteki kaç numaralı sayfaya ilişkin olduğu ``page_to_pfn`` fonksiyonuyla elde
edilebilmekteydi.

``alloc_pages`` fonksiyonuyla tahsis edilen sayfaların ``__free_pages`` fonksiyonuyla serbest
bırakılması gerekir:

.. code-block:: c

    void __free_pages(struct page *page, unsigned int order);

Fonksiyon ``mm/page_alloc.c`` dosyası içerisinde tanımlanmıştır. Fonksiyonun birinci parametresi
tahsisata ilişkin ilk ``page`` nesnesinin adresini, ikinci parametresi ise düzey bilgisini
belirtmektedir. Örneğin 2'inci düzeyden 4 sayfa tahsis etmiş olalım. Bu sayfaları serbest
bırakırken yine düzey bilgisini 2 olarak girmeliyiz. Örneğin:

.. code-block:: c

    struct page *pages;

    pages = alloc_pages(GFP_KERNEL, 2);  /* 2'inci düzeyden 4 ardışıl fiziksel sayfa tahsis ediliyor */
    if (pages == NULL)
        return -ENOMEM;

    /* ... */

    __free_pages(pages, 2);              /* 2'inci düzeyden yapılan tahsisat iade ediliyor */

``alloc_pages`` fonksiyonun başında ``__`` yokken yapılan tahsisatı serbest bırakan
``__free_pages`` fonksiyonun başında ``__`` olması bir uyumsuzluk oluşturmaktadır. Çekirdekte
aslında ``free_pages`` isimli başka bir fonksiyon da vardır. Bu fonksiyon sayfaları onların
sanal adreslerini (``page`` adreslerini değil sanal adreslerini) alarak serbest bırakmaktadır.

``alloc_pages`` ile tahsis edilen sayfaları farklı miktarlarda iade etmeye çalışmayınız. Bu
durumda dilimli tahsisat sistemini bozabilirsiniz:

.. code-block:: c

    __free_pages(pages + 0, 0);  /* dikkat! yanlış kullanım */
    __free_pages(pages + 1, 0);  /* dikkat! yanlış kullanım */
    __free_pages(pages + 2, 0);  /* dikkat! yanlış kullanım */
    __free_pages(pages + 3, 0);  /* dikkat! yanlış kullanım */

``alloc_pages`` ve ``__free_pages`` fonksiyonları export edildiği için aygıt sürücüler
tarafından da kullanılabilmektedir.

``alloc_pages`` fonksiyonunun bize fiziksel sayfanın sanal adresini vermediğine, o sayfayı
yönetmekte kullanılan ``page`` nesnesinin adresini verdiğine dikkat ediniz. Biz eğer ilgili
sayfanın içeriğine erişmek istiyorsak ``page_to_virt`` makrosunu ya da ``page_address``
fonksiyonunu kullanmalıyız.

Eğer tek sayfalık tahsisat yapılacaksa ``alloc_pages`` yerine ``alloc_page`` makrosu
kullanılabilir. Bu makro ``include/linux/gfp.h`` dosyasında şöyle yazılmıştır:

.. code-block:: c

    #define alloc_page(gfp_mask)    alloc_pages(gfp_mask, 0)

Yukarıda da belirttiğimiz gibi artık ``alloc_pages`` çekirdeklerde bir süredir makro olarak
yazılmaktadır. Bu makronun çağırma grafı şöyledir:
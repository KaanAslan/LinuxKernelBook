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
ve bölgelerdeki ikiz blok düzey listeleri de *"göç türlerine (migration types)"* ayırıyordu. İkiz blok tahsisat sistemleri 
göç türlerinin içerisindeydi. Ancak sayfa tahsis edilmek istendiğinde *fallback* mekanizması devreye giriyor, bu
mekanizma belli bir bölge ve göç türünden başlayarak önce göç türlerini, sonra bölgeleri, sonra da düğümleri
tarıyordu. Ayrıca çekirdeğin her düğümdeki toplam boş sayfaların sayısını (yani o bölgenin her göç türündeki toplam boş
sayfaların sayısını) da tuttuğunu anımsayınız. (Göç türleri için toplam boş sayfalar çekirdek tarafından
tutulmamaktadır.)

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
yol (slow path)"* de denilmektedir. *kswapd* çekirdek thread'inin bu bölgeleri doldurup boş sayfa sayılarını
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
thread uyutulup başkası tarafından uyandırılmaz, geri alımı bizzat yürütür. Bu süreci aşağıdaki şekille
özetleyebiliriz:
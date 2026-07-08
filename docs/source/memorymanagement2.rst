
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
   



====================
**Tampon Önbelleği**
====================

Bu bölümde eskiden ismine *tampon önbelleği (buffer cache)* denilen önbellek mekanizması 
üzerinde duracağız. Çekirdeğin 2.4 versiyonundan önce sayfa önbelleği ile tampon 
önbelleği ayrı veri yapıları biçiminde organize edilmişti. 2.4 çekirdeği ile birlikte tampon
önbelleği sayfa önbelleğinin içerisine gömüldü ve *tampon önbelleği (buffer cache)* terimi yerine 
*tampon başları (buffer heads)* terimi de kullanılmaya başlandı. Biz kitabımızda bu önbellek 
mekanizması için geleneksel olarak *tampon önbelleği* terimini kullanacağız. 

Çekirdek evrimleştikçe sayfa önbelleği ve tampon önbelleği üzerinde peek çok iyileştirmeler yapılmıştır. 
Biz kitabımızın bu bölümünde güncel çekirdeklerdeki tasarımı ele alıp açıklayacağız. Gelecekte tampon 
mekanizmasının çekirdeğin veri yolundan tamamen çıkartılması da düşünülmektedir. 

Giriş
=====

Sayfa önbelleği bir dosyanın içerisindeki bilgileri önbellekte tutmak için kullanılmaktadır. Linux çekirdeğinde 
dosya içeriğine ilişkin olmayan diskin metadata alanlarını önbelleklemek için kullanılan önbellek 
sistemine *tampon önbelleği* denilmektedir. Yani sayfa önbelleğinin amacı dosyanın içeriklerini önbelleklemekken 
tampon önbelleğinin amacı disk metadata bloklarını önbelleklemektir. 

Biz dosya sistemini ele aldığımız bölümde *simplefs* dosya sistemimizde blokları ``sb_bread`` fonksiyonuyla okumuştuk. 
Bu fonksiyona okuyacağımız blok numarasını vermiştik, fonksiyondan da ``buffer_head`` nesnesi elde etmiştik. 
``sb_bread`` fonksiyonunun prototipi şöyleydi:

.. code-block:: c

    static inline struct buffer_head *sb_bread(struct super_block *sb, sector_t block);

Fonksiyon başarı durumunda bize okunan bloğa ilişkin bir ``buffer_head`` nesnesi veriyordu. Biz o
bölümde okunan blokların aynı zamanda sayfa önbelleğine de yerleştirildiğini söylemiştik. Bu
bölümde bu tamponlama sistemini ele alıp bu sistemin sayfa önbelleğiyle ilişkisi üzerinde
duracağız.


Eskiden çekirdeğin 2.4 versiyonu öncesinde tampon önbelleği ile sayfa önbelleği birbirinden tamamen
ayrıydı. Tampon önbelleği dosya sisteminin bloklarını önbelleklerken, sayfa önbelleği dosya
içeriklerini önbellekliyordu. Bu iki önbellek sisteminin veri yapıları da birbirinden ayrıydı.
2.4 öncesi çekirdeklerdeki bu iki önbellek sistemini aşağıdaki şekille betimleyebiliriz:

.. figure:: _static/old-dual-cache.png
   :alt: 2.4 öncesi ayrık sayfa ve tampon önbellekleri
   :align: center
   :width: 55%

Sayfa önbelleği 2.4 öncesinde read-only bir önbellekti. Kirli veri orada durmuyordu, oradan diske
geri yazım da yapılmıyordu. O dönemlerde yazma sahipliği tampon önbelleğindeydi. O dönemlerde bu
iki önbelleğin birbirinden ayrık olmasının yarattığı en önemli sorunlardan biri disk bloğunun her
iki önbellekte de bulunabilmesiydi. Örneğin biz blok okuması yoluyla bir bloğu okumuş olalım. Bu
blok tampon önbelleğine giriyordu. Ancak aynı blok bir dosyanın da parçasıysa aynı zamanda bu blok
sayfa önbelleğinde de bulunuyordu. Tabii bu durumla genellikle karşılaşılmıyordu. Çekirdeğin 2.4
versiyonuyla bu iki önbellek sistemi birleştirildi. Tampon önbelleği sayfa önbelleğinin içine
oturtuldu. 2.4 ve sonrasındaki organizasyonu şekilsel olarak şöyle gösterebiliriz:

.. figure:: _static/unified-cache.png
   :alt: 2.4 ve sonrasında birleştirilmiş önbellek organizasyonu
   :align: center
   :width: 55%

Tampon önbelleğinin sayfa önbelleğinin içerisine oturtulmasıyla artık her disk bloğu toplamda tek
bir yerde önbelleklenmektedir. Bu durum hem sistemin ele alınmasını kolaylaştırmış hem de
tutarlılığı artırmıştır.
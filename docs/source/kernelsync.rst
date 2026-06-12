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

Kritik Kod Blokları ve Senkronizasyonun Gerekliliği
===================================================

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

Manuel Kritik Kod Bloklarını Oluşturmanın Sorunları
----------------------------------------------------

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
faydalanılmaktadır. Bugün bilgisayar sistemlerinde birden fazla çekirdek
bulunabildiği için kritik kod oluşturan sistem programcılarının bunlara dikkat
etmesi gerekir. Linux'un çekirdek kodlarında zaten çeşitli senaryolar için
kullanılabilecek senkronizasyon nesneleri hazır biçimde bulunmaktadır. Bu bölümde
biz bu senkronizasyon nesnelerini ele alacağız. Bölümün sonlarına doğru da bu
senkronizasyon nesnelerinin oluşturulabilmesi için gereken makine komutları hakkında
bilgiler vereceğiz.
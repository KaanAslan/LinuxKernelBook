===================
Bekleme Kuyrukları
===================

Bu bölümde önce bekleme kuyruklarının (wait queues) genel yapısını açıklayacağız. Sonra da
thread'lerin çalışma kuyruğundan (run queue) bekleme kuyruklarına nasıl aktarıldığı (yani
thread'lerin nasıl bloke edildiği) ve yeniden nasıl çalışır duruma getirildiği (yani blokenin nasıl
çözüldüğü) konuları üzerinde duracağız. Çizelgeleyici (scheduler) alt sistem başka bir bölümde
ayrıntılarıyla ele alınacaktır.

Thread'lerin Çizelgelenmesi
---------------------------

Linux çekirdeklerinde çizelgeleyici (scheduler) alt sistem zaman içerisinde birkaç kere önemli ölçüde
değiştirilmiştir. Mevcut Linux çekirdeklerinde sistemdeki her işlemci ya da çekirdek için ayrı bir
*çalışma kuyruğu (run queue)* bulundurulmaktadır. Yani her işlemci ya da çekirdek kendi çalışma
kuyruğundaki thread'leri çizelgelemektedir. Çalışma kabaca *zaman paylaşımlı (time sharing)* biçimde
yapılmaktadır. Yani sıradaki thread CPU'ya atanır, belli bir süre çalıştırılır, sonra thread'in
çalışmasına ara verilir ve kuyruktaki yeni thread CPU'ya atanır. Bu işlem böyle devam ettirilir. Bir
thread'in parçalı çalışma süresine *quantum süresi (time quantum)* denilmektedir. Thread'lerin quantum
süreleri aynı olmak zorunda değildir. Bu konunun ayrıntılarını çizelgeleyici alt sistemin ele alındığı
bölümde açıklayacağız. Aşağıda güncel çekirdeklerdeki çizelgeleme işlemlerini bir şekille betimliyoruz:

.. image:: _static/scheduler-run-queue.png
   :alt: Çizelgeleyici ve Çalışma Kuyruğu
   :align: center
   :width: 70%

Çalışma kuyruğundaki bir thread'e çalışma sırası geldiğinde o thread CPU'ya atanıp belli bir süre
çalıştırılır. Bu süre dolduğunda bir sonraki turda kalınan yerden çalışmaya devam edebilmesi için
thread çalışma kuyruğuna geri bırakılır. Bir thread'in çalışmasına ara verilip çalışma kuyruğundaki
diğer thread'in CPU'ya atanması sürecine işletim sistemleri terminolojisinde *bağlamsal geçiş (context
switch)* denilmektedir. Bağlamsal geçiş terimi yerine *task switch* terimi de kullanılabilmektedir.
Thread'in quantum süresi bittiğinde CPU'dan kopartılması işlemine *preemption* da denilmektedir.
*Preemption* İngilizcede *zorla ele geçirmek, el koymak* gibi anlamlara gelmektedir. Bağlamsal geçiş
donanım kesmeleriyle yapılmaktadır. Genel amaçlı bilgisayar donanımlarında periyodik kesme üreten
zamanlayıcı (timer) devreleri vardır. Zamanlayıcı devreleri yoluyla oluşturulan kesmeler belli bir
sayıya geldiğinde çizelgeleyici o anda çalışmakta olan kodu herhangi bir noktasında keserek çalışmaya
ara verebilmektedir.

Thread'lerin çalışmasına ara verilmesi ve çalışmayı kaldığı yerden devam ettirilmesi aslında zor bir
işlem değildir. Thread'in o andaki tüm konumu aslında CPU yazmaçlarının içerisindeki değerlerden
oluşmaktadır. Bağlamsal geçiş sırasında CPU yazmaçlarının içerisindeki değerler thread'in
``task_struct`` alanına kaydedilmektedir. Thread CPU'ya atanırken de bu yazmaç bilgileri oradan
alınarak yeniden CPU yazmaçlarına aktarılmaktadır. Tabii tüm bu işlemler bir zaman kaybına da yol
açmaktadır. Eğer quantum süresi çok kısa tutulursa çok bağlamsal geçiş oluşur ve birim zamanda yapılan
iş miktarı (throughput) düşer. Eğer bağlamsal geçiş çok uzun tutulursa bu durumda da interaktivite
azalır. Bir thread işletim sistemi tarafından bir CPU'nun çalışma kuyruğuna atandığında hep o CPU'nun
kuyruğunda kalması garanti değildir. Zaman içerisinde (tıpkı süper marketlerdeki kasa kuyruklarında
olduğu gibi) kuyruklar arasında dengesizlikler oluşabilmektedir. Bu durumda işletim sistemi dengeyi
sağlamak için thread'leri daha boş olan bir CPU'nun çalışma kuyruğuna taşıyabilmektedir.

Thread'lerin Bloke Olması
-------------------------

Bir thread uzun sürebilecek dışsal bir olayı bekleyeceği zaman bunu CPU zamanı harcayarak beklemez.
Bu tür durumlarda thread CPU'nun çalışma kuyruğundan çıkartılarak *bekleme kuyrukları (wait queues)*
denilen kuyruklarda bekletilir. Bu sürece *thread'in bloke olması* denilmektedir. Örneğin ``read``
POSIX fonksiyonuyla bir dosyadan okuma yapmak isteyelim. Anımsanacağı gibi ``read`` fonksiyonu
``sys_read`` sistem fonksiyonunu çağırmaktadır. Bu fonksiyon da önce okunacak yerin page cache
içerisinde olup olmadığına bakmaktadır. Okunacak yer page cache içerisindeyse thread bloke olmadan
okuma yapılır. Ancak okunacak yer page cache içerisinde değilse disk okumaları yavaş olduğu için thread
bloke edilir, çalışma kuyruğundan çıkartılarak bir bekleme kuyruğunda bekletilir. Disk okuması
gerçekleştiğinde thread yeniden çalışma kuyruğuna yerleştirilmektedir. Spinlock ve readers/writer lock
nesneleri dışındaki senkronizasyon nesnelerinde de eğer kilit kapalıysa lock işlemini yapmaya çalışan
thread'ler benzer biçimde bloke olmaktadır. ``sleep`` gibi fonksiyonlar da yine blokeye yol açmaktadır.
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
   :width: 65%

Buradaki *Running* thread'in CPU'ya atanmış ve çalışmakta olduğu anlamına gelmektedir. *Ready* ise
thread'in çalışma kuyruğunda bulunduğunu ve sonraki quantum'u beklediğini belirtmektedir. Thread
dışsal bir olay nedeniyle bloke olduğunda bekleme kuyruklarına alınır. Şeklimizdeki *Waiting* ise
thread'in bekleme kuyruğunda beklediğini belirtmektedir. Dışsal olay gerçekleştiğinde thread'in
blokesi çözülüp yeniden çalışma kuyruğuna yerleştirilmektedir. Tabii buradaki şekil oldukça
sadeleştirilmiş bir şekildir. Örneğin thread'in sonlanması başka biçimlerde de gerçekleşebilmektedir.

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
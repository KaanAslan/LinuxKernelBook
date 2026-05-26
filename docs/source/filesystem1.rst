.. _dosya-sistemi-1:

===========================================
Linux Çekirdeğinde Dosya Sistemi - I. Bölüm
===========================================

Bu bölümde dikkatimizi dosya sistemine illişkin çekirdek veri yapıları üzerine yönelteceğiz. Bilindiği gibi 
UNIX/Linux sistemlerinde pek çok kavram kullanıcıya bir dosya gibi gösterilmektedir. Biz bu birinci bölümde belli bir derinliğe 
kadar çekirdeğin dosya işlemleri için oluşturduğu organizasyon üzerinde duracağız. Daha sonra ikinci bölümde
dosya sistemine ilişkin aşağı seviyeli ayrıntıları ele alacağız.

Giriş
-----

İşletim sistemlerinin *dosya sistemi (file system)* denilen alt sistemlerinin iki tarafı vardır: **Disk tarafı**
ve  **bellek tarafı**. Dosya bilgileri disk üzerindeki bloklarda tutulmaktadır. (Bu bloklara Microsoft dünyasında
*cluster* da denilmektedir.) Hangi dosyaların diskin hangi bloklarında tutulduğu, dosyaların
metadata bilgilerinin diskte nasıl saklandığı gibi belirlemeler dosya sisteminin disk tarafını;
diskteki dosya sisteminin çekirdekteki temsilinin oluşturulması ve işletim sisteminin açılan
dosyalar için yaptığı düzenlemeler ise dosya sisteminin bellek tarafını oluşturmaktadır.

Disk Aktarımına İlişkin Temel Bilgiler
--------------------------------------

Biz kursumuzda "disk" terimini ikinci bellekleri belirten genel bir terim olarak kullanacağız. 
Bir süre önceye kadar disk olarak ağırlıklı biçimde *hard disk* dnilen elektromekanik birimler 
kullanılıyordu. Ancak bir süredir artık disk olarak yarı iletken teknolojiler kullanılarak oluşturulmuş 
*SSD (Solid State Disk)* denilen diskler kullanılmaktadır. Bugün ağırlıklı olarak kullandığımız SSD disklerin 
herhangi bir mekanik parçası yoktur. SSD'ler *NAND Flash* denilen bellek teknolojisini kullanmaktadır. 
SSD'ler hard disklere göre oldukça hızlıdır. Ancak onların en önemli handikapları belli bir yazma ömrünün 
olmasıdır. SSD'lerde aynı bölgeye belli sayıdan daha fazla yazma yapıldığında artık SSD'nin o bölgesi 
bozulabilmektedir. Tabii teknoloji bu bakımdan da ilerleme içerisindedir. SSD teknolojisi ile USB yuvalarına
taktığımız flash belleklerin teknolojisi birbirine benzemektedir.


Sektörler ve Disk Denetleyicisi
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Kullandığımız disk birimi ister *hard disk* olsun isterse SSD olsun disk ile bilgisayarımızın
RAM'i arasındaki transferler *sektör (sector)* denilen byte blokları düzeyinde yapılmaktadır. Sektör
bir diskten okunabilecek ya da bir diske yazılabilecek en küçük birimdir. Bir sektör tipik olarak
512 byte'tır. Diskte byte düzeyinde erişim yoktur. Sektörel erişim vardır. Örneğin diskteki bir
sektörde bulunan bir byte üzerinde değişiklik ancak şöyle yapılabilmektedir: Önce o byte'ın
içinde bulunduğu sektör RAM'e okunur. Sonra byte RAM üzerinde değiştirilir. Sonra aynı sektör
yeniden diske yazılır.

Diskteki her sektörün ilk sektör 0 olmak üzere bir mantıksal numarası vardır. Hard disklerde
ardışıl numaralı mantıksal sektörler disk üzerinde de fiziksel olarak peşi sıra bulunmaktadır.
Mekanik hard disklerde bilgiler *track* denilen yollara yazılmaktadır. Ardışıl sektörler aynı
track'te bulunurlar. Dolayısıyla hard disklerde diskin kafası bir kez konumlandırıldığında
ardışıl sektörlere daha hızlı okuma yazma yapılabilmektedir. SSD'ler mekanik öğe barındırmadığı
için rastgele erişimlidir. Yani her sektörden okuma aynı hızda yapılmakta ve her sektöre yazma da
aynı hızda yapılmaktadır.

Modern bilgisayar sistemlerinde disk birimine doğrudan erişilmez. Disk erişimlerinde bu işleme
aracılık eden ismine *disk denetleyicisi (disk controller)* denen yerel bir işlemciden
faydalanılmaktadır. Yani sistem programcıları ya da işletim sistemlerini yazanlar disk
denetleyicisini programlar, disk denetleyicisi isteği elektriksel olarak disk birimine iletir,
okuma yazma işlemleri de disk birimi tarafından yapılır:

.. graphviz::

   digraph disk_hierarchy {
       rankdir=TB;
       node [shape=box, style="rounded,filled", fillcolor="#D6E8FA",
             fontname="DejaVu Sans", margin="0.3,0.2"];
       edge [color="#555555"];

       OS         [label="İşletim Sistemi"];
       CPU        [label="CPU / RAM"];
       Controller [label="Disk Denetleyicisi\n(Disk Controller)"];
       Disk       [label="Disk\n(HDD / SSD)", fillcolor="#D5F5D5"];

       OS -> CPU -> Controller -> Disk;
   }

Bugünkü masaüstü bilgisayarlarımızda *SATA* ve *NVMe* en çok kullanılan disk denetleyicileridir.


DMA (Direct Memory Access)
~~~~~~~~~~~~~~~~~~~~~~~~~~

Peki işletim sistemi tarafından disk denetleyicisi "falanca sektörleri oku" ya da "falanca 
sektörlere yaz" biçiminde  programlandıktan sonra aktarım nasıl yapılmaktadır?  Aktarım CPU
tarafından tek tek byte'ların denetleyiciden alınarak RAM'e yerleştirilmesi yoluyla
yapılmamaktadır. (Çok eskiden ilk PC mimarilerinde aktarım böyle de yapılabiliyordu.) Çünkü
CPU'nun bu işle meşgul olması önemli bir zaman kaybı oluşturmaktadır. Bu tür disk ile RAM
arasındaki aktarımlar için *DMA (Direct Memory Access)* denilen yardımcı denetleyiciler
kullanılmaktadır.

Tipik olarak CPU'da çalışan kod (yani işletim sistemi) disk denetleyicisine transfer isteğini
ve aktarımda kullanılacak bellek alanlarının adresini bildirir. Disk denetleyicisi de disk
birimini ve DMA'yı elektriksel düzeyde programlayarak aktarımın DMA üzerinden doğrudan RAM'e
yapılmasını sağlar. Aktarım sırasında artık CPU bu işle meşgul olmaz, işletim sistemi de
CPU'yu başka bir thread'i çalıştırması için *bağlamsal geçişe (task switch)* sokar. Tabii
aktarım işlemi bittiğinde disk denetleyicisi CPU'yu bir donanım kesmesi yoluyla durumdan
haberdar etmektedir.

Yani disk ile RAM arasındaki aktarım işlemleri tipik olarak şöyle yapılmaktadır:

1. İşletim sistemi disk denetleyicisine aktarılacak sektörlere ilişkin bilgileri ve transfer
   adreslerini CPU yoluyla elektriksel olarak iletir.
2. Okuma söz konusuysa disk denetleyicisi disk birimine elektriksel düzeyde komutlar göndererek
   sektörlerin okunmasını ve DMA yoluyla bunların RAM'de uygun yerlere aktarılmasını sağlar.
   Eğer yazma söz konusuysa RAM'de belirtilen adresteki bilgiler yine DMA yoluyla disk birimine
   iletilerek yazma gerçekleştirilir.
3. Aktarım işlemi bittiğinde disk denetleyicisi bir donanım kesmesi yoluyla CPU'yu durumdan
   haberdar eder.
4.  İşletim sistemi aktarım için gereken kodları çalıştırdıktan sonra aktarım bitene kadar meşgul 
    bir döngüde beklemez. Başka thread'ler çalıştırılabiliyorsa *bağlamsal geçiş (context switch)* 
    oluşturarak CPU'nun boş biçimde beklemesinin önüne geçer.

Bu süreci aşağıdaki diyagram özetlemektedir:

.. graphviz::

   digraph dma_flow {
       rankdir=TB;
       graph [splines=ortho, fontname="DejaVu Sans",
              nodesep=0.8, ranksep=0.9];
       node  [shape=box, style="rounded,filled", fontname="DejaVu Sans",
              margin="0.32,0.20", fontsize=11];
       edge  [fontname="DejaVu Sans", fontsize=9, color="#444444"];

       /* IRQ yayını üstten yönlendiren görünmez köprü */
       IRQ_kpr [label="", shape=point, style=invis,
                width=0.01, height=0.01, fixedsize=true];

       /* Üst katman: yazılım zinciri */
       App        [label="Uygulama\nI/O çağrısı",
                   fillcolor="#EEEDFE", color="#534AB7", fontcolor="#3C3489"];
       CPU        [label="OS / CPU\nKesmeyi alır",
                   fillcolor="#EEEDFE", color="#534AB7", fontcolor="#3C3489"];
       Driver     [label="Aygıt Sürücüsü\nKomut hazırlar",
                   fillcolor="#EEEDFE", color="#534AB7", fontcolor="#3C3489"];
       Controller [label="Denetleyici\nIRQ tetikler",
                   fillcolor="#FAEEDA", color="#854F0B", fontcolor="#633806"];

       /* Alt katman: DMA donanımı */
       Memory     [label="Bellek (RAM)\nDMA hedefi",
                   fillcolor="#E1F5EE", color="#0F6E56", fontcolor="#085041"];
       DMA        [label="DMA Motoru\nCPU'dan bağımsız",
                   fillcolor="#E1F5EE", color="#0F6E56", fontcolor="#085041"];
       Disk       [label="Disk Donanımı\nHDD / SSD / FTL",
                   fillcolor="#EAF3DE", color="#3B6D11", fontcolor="#27500A"];

       /* Sıra düzeni */
       { rank=source; IRQ_kpr; }
       { rank=same;   App; CPU; Driver; Controller; }
       { rank=same;   Memory; DMA; Disk; }

       /* 1. Komut zinciri */
       App    -> CPU        [label="read()/write()"];
       CPU    -> Driver     [label="I/O isteği"];
       Driver -> Controller [label="komutu gönder"];

       /* 2. Donanım komutları */
       Controller -> Disk [label="komut gönder"];
       Controller -> DMA  [label="DMA tablo ayarı",
                            style=dashed, color="#888780",
                            fontcolor="#5F5E5A"];

       /* 3. Veri akışı (DMA, CPU katılmadan) */
       Disk -> DMA    [label="veri aktarır",
                        style=dashed, color="#1D9E75", fontcolor="#0F6E56"];
       DMA  -> Memory [label="RAM'e yazar",
                        style=dashed, color="#1D9E75", fontcolor="#0F6E56"];

       /* 4. Kesme — IRQ_kpr üzerinden üstten kıvrılarak CPU'ya */
       Controller -> IRQ_kpr [color="#E24B4A", penwidth=2.0,
                               arrowhead=none, weight=0];
       IRQ_kpr    -> CPU     [color="#E24B4A", penwidth=2.0,
                               label="Transfer tamamlandı → Kesme (IRQ)",
                               fontcolor="#E24B4A", weight=0];
   }

Eskiden Intel tabanlı PC mimarisinde ISA bus kullanıldığı zamanlarda tek bir merkezi DMA
denetleyicisi (Intel 8237) vardı. Ancak daha sonra PCI bus kullanılmaya başlanmasıyla birlikte
artık transfer yapabilen her donanım birimi kendi DMA denetleyicisini de içermeye başladı.
Bugün Intel tabanlı ve Apple Silicon tabanlı bilgisayar mimarilerinde disk denetleyicisi kendi
içerisindeki DMA denetleyicisini programlayarak transferi gerçekleştirmektedir. Disk
denetleyicilerinin programlanması ise artık uzunca bir süredir *bellekten tabanlı IO
(memory-mapped IO)* tekniği ile yapılmaktadır.

Hard disklerde disk birimi içerisinde önbellekler (cache) de bulundurulmaktadır. Böylece disk denetleyicisi aynı 
sektörleri disk biriminden istediği zaman disk birimi eğer ilgili sektörler önbellek içerisindeyse hiç kafa 
hareketleri yapmadan onları doğrudan önbellekten verebilmektedir. Bugünlerde örneğin 1 TB'lık hard disklerde 64MB, 
128, 256 MB civarında önbellekler kullanılmaktadır. Yalnızca hard disklede değil SSD'lerde de bir önbellek sistemi 
vardır. SSD'lerdeki önbellek sistemi özellikle yazma işlemlerinde hız kazancı sağlamakta ve aynı sektörlere sürekli 
yazım yapıldığında o bölgenin *aşınmasını (wearing)* engellemektedir. Tabii bu öönbellek sistemleri tamamen disk 
birimleri tarafından içsel olarak (built-in) işletilmektedir. Bu önbellek sistemleri işletim sistemleri tarafından 
erişilebilir değildir.


Blok Kavramı
~~~~~~~~~~~~

Yukarıda da belirttiğimiz gibi bir disk biriminde transfer edilecek en küçük birime sektör denilmektedir. Bir sektör 
tipik olarak 512 byte uzunluğundadır. Ancak aslında sektör uzunlukları da disk üreticilerine bağlı olarak değişebilmektedir. 
512 byte sektör uzunlukları bugün için standart bir uzunluktur. Tabii zaman geçtikçe diskler büyüdüğü için sektör 
uzunluklarının da büyüyebileceğini söylemek istiyoruz. Nitekim 4K uzunluğunda sektörlere sahip olan diskler özellikle 
büyük sistemlerde gittikçe yaygınlaşmaktadır. Disk birimi her sektöre ilk sektör 0 olmak üzere mantıksal bir numara 
vermektedir. Yani adeta disk üzerindeki her sektörün bir adresi vardır. Disk denetleyicisi disk birimine transfer 
edilecek sektörlerin numaralarını elektriksel düzeyde iletmektedir. (Bu biçimde mantıksal sektör numaraları kullanılmadan 
önce 80'lerde ve 90'ların ilk yarısında sektörlerin yerleri "fiziksel koordinat sistemi" denilen "hangi yüz (head)", 
"hangi track", "hangi sektör dilimi" biçiminde üç parametreyle belirtiliyordu.)

Sektör kavramı aslında dosya sistemleri için küçük bir depolama birimidir. İşletim sistemleri
bir dosyanın parçası olabilecek en küçük disk alanı için sektör yerine *blok (block)* ya da
*cluster* denilen daha büyük birimleri kullanmaktadır. Blok terimi daha çok UNIX/Linux
sistemlerinde kullanılmaktadır. Microsoft ise blok yerine *cluster* terimini kullanmaktadır.
Bir blok ardışıl n tane sektörden oluşmaktadır. Uygulamada bu n değeri 2'nin bir kuvveti olur. Ardışıllık hard disklerde 
önemli bir unsurdur. Çünkü hard disklerde en önemli zaman kaybı mekanik bir birim olan disk kafasının track hizasına 
çekilmesinde yaşanmaktadır. Disk kafası track hizasına çekildiğinde disk dönerken artık ardışıl sektörler hiç kafa 
hareketi yapılmadan okunup yazılabilmektedir. Peki neden işletim sistemi dosyalar söz konusu olduğunda bir dosyanın 
parçası olabilecek en küçük birim için sektör değil de ardışıl n tane sektör kullanmaktadır? İşte bunun birkaç nedeni 
vardır:

1. Dosyaların parçaları disk üzerinde ardışıl yerlerde olmak zorunda değildir. Eğer dosyalar
   çok fazla parçadan oluşursa hard disklerde (ve kısmen de olsa SSD'lerde de) bu parçalar disk
   üzerinde daha fazla yayılmış olur, bunlara erişmek için gereken zaman artar.

2. Eğer dosyanın parçaları sektör gibi küçük birimlerden oluşsaydı bu parçaların diskteki
   yerlerine ilişkin metadata tabloları büyürdü. Bu da hem disk alanını hem de işletim sisteminin
   bellekte yaptığı düzenlemede alan verimsizliği oluştururdu.

3. CPU'ların kullandığı sayfalama mekanizmasında genellikle 4K uzunluklar kullanılmaktadır.
   Dosya parçalarının 4K uzunluğun katlarında olması dosya sistemi ile sayfalama sistemi arasında
   daha iyi bir uyumun ortaya çıkmasına yol açmaktadır.

Peki bu durumda işletim sistemleri blok denilen dosyanın parçası olabilecek en küçük birim için hangi uzunluğu 
kullanmaktadır? İşte genellikle bu karar disk formatlanırken diskin (disk bölümünün) büyüklüğüne bakılarak verilmektedir. 
Dosyaların son bloklarında kalan kullanılmayan alanların oluşmasına *içsel bölünme (internal fragmentation)* 
denilmektedir. Küçük disklerde (disk bölümlerinde) içsel bölünmenin etkisi daha büyük olacağından blokların 1K gibi 
küçük uzunluklarda alınması uygun olabilir. Ancak orta büyüklükte disklerde içsel bölünmenin etkisi göreli olarak 
azalacağı için bloklar 4k gibi bir değerde seçilebilmektedir. Büyük disklerde ise 8K, 16K blok büyüklükleri tercih 
edilmektedir. Aslında blok büyüklükleri ilgili disk bölümü formatlanırken (Linux sistemlerinde ``mkfs.xxx`` programlarıyla 
formatlama yapılmaktadır) belirlenmektedir. Yani kullanıcı isterse kendisi bu programda kendi tercih ettiği blok 
uzunluğunu kullanabilir. Ancak kullanıcılar genellikle böyle bir belirleme yapmazlar. Bu durumda bu programlar disk 
bölümünün büyüklüğüne bağlı olarak yukarıda açıkladığımız gibi uygun bir blok büyüklüğünü seçerler.

UNIX/Linux sistemlerinde dosya sistemi için tek bir kök vardır. Blok aygıtları (örneğin hard
diskler, flash bellekler vb.) belli bir dizine mount edilmektedir. Mount işlemi bir dizin üzerine
uygulanır; mount işlemi sonucunda o dizinin içeriği görünmez, artık mount edilen dosya sisteminin
kök dizini mount dizininde gözükür. Dolayısıyla bu sistemlerde farklı dizinler farklı blok
büyüklüklerine ilişkin dosya sistemlerinin içerisinde olabilmektedir.

Anımsanacağı gibi ``stat`` POSIX fonksiyonu ya da komut satırından uygulanan *stat* komutu belli
bir dosyanın bilgilerini verirken o dosyanın içinde bulunduğu dosya sisteminin blok uzunluğunu
da vermektedir. Linux sistemlerinde bu bilgi doğrudan dosya sistemine ilişkin blok aygıtı
üzerinde ``dumpe2fs`` programıyla da elde edilebilmektedir.

Windows sistemlerinde de *cluster* adı altında blok sistemi kullanılmaktadır. O sistemlerde blok
uzunluklarını *chkdsk* programı ile ya da *fsutil* programı ile komut satırından elde
edebilirsiniz.

İşletim sistemleri işlemlerini kolaylaştırmak için her bloğa bir numara da vermektedir. Örneğin
bir bloğun 4K (tipik olarak 8 sektör) olduğunu düşünelim. İşletim sistemi için ilgili disk (aslında
disk bölümü ya da genel olarak blok aygıtı da diyebiliriz) bloklardan oluşmaktadır. Örneğin
diskin (disk bölümünün) ilk 8 sektörü artık 0'ıncı bloktur. Sonraki 8 sektör 1'inci bloktur.

İşletim sistemi içsel olarak artık ilgili diski bloklardan oluşan ve her bloğun bir numarasının
olduğu mantıksal bir depolama alanı gibi ele almaktadır. Yani işletim sistemi için yalnızca
sektörlerin değil aynı zamanda dosya sistemine ilişkin blokların da numaraları vardır.

Sayfa Önbelleği (Page Cache)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

İşletim sistemleri son okunan ya da yazılan disk bloklarını RAM'de bir önbellek sisteminde
saklamaktadır. Bu önbellek sistemine genel olarak *işletim sisteminin disk önbellek sistemi*
denilmektedir. Linux dünyasında eskiden bu önbellek sistemine *buffer cache* deniliyordu. Sonra
bu önbellek sistemi iyileştirildi ve ismi *page cache* olarak değiştirildi.

İşletim sistemlerinin bu disk önbellek sistemleri disk erişimini ciddi boyutta azaltmakta ve
sistem performansı üzerinde en önemli olumlu etkilerden birini oluşturmaktadır. Eğer işletim
sistemlerinde böyle bir disk önbellek sistemi olmasaydı sistemler çok yavaş çalışırdı.

Dosyalardan Okuma ve Yazma İşlemleri
----------------------------------------------

Biz UNIX/Linux sistemlerinde bir dosyadan okuma yapmak için ya da bir dosyaya yazma yapmak için
``read``/``write`` POSIX fonksiyonlarını kullanmış olalım. Bu fonksiyonlar çekirdek içerisindeki
``sys_read`` ve ``sys_write`` sistem fonksiyonlarını çalıştırmaktadır.

İşletim sistemi bellek tarafında yaptığı organizasyonla okunacak ya da yazılacak bilginin ilgili
blok aygıtının (disk bölümünün) kaç numaralı bloğuna ve sektörüne ilişkin olduğunu
belirleyebilmektedir. Ancak ``sys_read`` ve ``sys_write`` gibi sistem fonksiyonları hemen diske
yönelmez. Bu fonksiyonlar önce dosyanın ilgili bölümünün RAM'de oluşturulmuş bir sayfa önbelleği
(*page cache*) içerisinde olup olmadığına bakmaktadır. Eğer ilgili bölüm bu önbellek sisteminin
içerisinde varsa bu fonksiyonlar diske hiç erişmeden dolayısıyla da hiç bloke olmadan bu okuma
yazma işlemini gerçekleştirmektedir.

``read``/``write`` POSIX fonksiyonları çağrıldığında yapılan işlemler aşağıdaki diyagramda
özetlenmiştir:

.. graphviz::

   digraph rw_flow {
       rankdir=TB;
       node [shape=box, style="rounded,filled", fillcolor="#D6E8FA",
             fontname="DejaVu Sans", margin="0.3,0.2"];
       edge [fontname="DejaVu Sans", fontsize=9, color="#444444"];

       POSIX  [label="read / write POSIX Fonksiyonları"];
       Sys    [label="sys_read / sys_write"];
       Check  [label="Page Cache'te bilgi var?",
               shape=diamond, fillcolor="#FFF3CD"];
       Copy   [label="Veriyi kopyala\n(disk erişimi yok)", fillcolor="#D5F5D5"];
       DiskIO [label="Gerçek disk I/O başlat\n(okuma / yazma)"];
       Update [label="Page Cache güncellenir", fillcolor="#D5F5D5"];

       POSIX  -> Sys    [label="Çekirdek Moduna Geçiş",
                         fontsize=13, fontcolor="#1a5fa8"];
       Sys    -> Check;
       Check  -> Copy   [label="Evet"];
       Check  -> DiskIO [label="Hayır"];
       DiskIO -> Update;
   }

Peki dosyadaki okunacak ya da yazılacak kısım sayfa önbelleğinde (*page cache*) yoksa gerçek
transfer nasıl yapılmaktadır? Linux sistemlerinde bu transferlerin yapıldığı birime *blok aygıt
sürücüleri (block device drivers)* denilmektedir.

Bir Linux sistemi kurulduğunda zaten temel disk denetleyicileri üzerinden transfer yapabilen blok
aygıt sürücüleri çekirdeğin içerisine gömülmüş durumda olur. Ancak sistem programcısının kendisi
de blok aygıt sürücüleri yazabilir. Örneğin bir gömülü Linux sisteminde yeni bir SD kart birimi
için bir blok aygıt sürücüsü yazmak zorunda kalabilirsiniz.

İşletim sistemi bu IO isteklerini hemen blok aygıt sürücüsüne göndermez. Çünkü çok sayıda
farklı proses aynı disk sektörlerini okuyacak ya da o sektörlere yazacak olabilir. İşletim
sistemi önce istekleri sıraya dizer, mümkünse birleştirir, bu biçimdeki iyileştirme işleminden
sonra istekleri blok aygıt sürücüsüne gönderir. Bu sürece *IO çizelgelemesi (IO scheduling)*
denilmektedir.

O halde bir dosya okuması ya da yazması sonucunda gelişen olayları şöyle özetleyebiliriz:

1. Kullanıcı modunda çalışan program (yani proses) ``read`` ya da ``write`` POSIX fonksiyonlarını
   çağırır. (UNIX/Linux sistemlerindeki C derleyicilerinin standart dosya fonksiyonları da eğer
   okunacak ya da yazılacak kısım kendi tamponlarında yoksa zaten bu POSIX fonksiyonlarını
   çağırmaktadır.)

2. ``read`` ve ``write`` POSIX fonksiyonları Linux'ta ``sys_read`` ve ``sys_write`` isimli sistem
   fonksiyonlarını çağırır. Artık akış kullanıcı modundan (user mode) çekirdek moduna (kernel
   mode) geçmiştir.

3. ``sys_read`` ve ``sys_write`` fonksiyonları önce okunacak ya da yazılacak yerin Linux'un disk
   önbellek sistemi olan sayfa önbelleğinde (*page cache*, eski ismiyle *buffer cache*) olup
   olmadığına bakar. Eğer ilgili disk blokları sayfa önbelleğinde varsa akış hiç bloke olmadan
   sayfa önbelleği içerisinden karşılanır. Aksi hâlde Linux çekirdeği isteği *IO çizelgeleyicisi
   (IO scheduler)* denilen çekirdek birimine iletir; ``read``/``write`` çağrısını yapan thread
   bloke edilir.

4. IO çizelgeleyicisi istekleri çizelgeler. Okuma işlemi söz konusuysa sayfa önbelleğinde
   transfer edilecek önbellek bloklarını tahsis eder. Yazma işlemi söz konusuysa diske transfer
   edilecek önbellek bloklarını belirler. Blok aygıt sürücüsüne transfer edilecek sektörleri ve
   transfere ilişkin bellek adreslerini iletir.

5. Gerçek transfer işlemi blok aygıt sürücüsü tarafından yapılmaktadır. İşletim sistemi blok
   aygıt sürücüsüne hangi sektörlerin sayfa önbelleğindeki hangi adreslere (ya da tersi yönde)
   transfer edileceğini bir kuyruk sistemi yardımıyla iletmektedir.

6. Blok aygıt sürücüsü diskten istenen sektörleri sayfa önbelleği içerisinde belirtilen adrese
   ya da sayfa önbelleğindeki bilgileri diskin belirtilen sektörlerine transfer eder.

7. Artık okuma söz konusuysa okunan bilgi sayfa önbelleği içerisindedir. İşlemi başlatan
   thread'in blokesi çözülür. ``sys_read`` sistem fonksiyonu bunu sayfa önbelleği içerisinden
   programcının kullanıcı modundaki adresine kopyalar.

Tabii bugün kullandığımız Linux sistemlerinde aslında disk transflerini yapan blok aygıt sürücüleri zaten çekirdek 
imajı içerisine gömülmüş bir biçimde bulunmaktadır. Ancak nadiren de olsa sistem programcısının yeni birtakım aygıtlar 
için blok aygıt sürücüleri yazması gerekebilmektedir.


Yukarıda maddeler halinde açıkladığımız süreci bir şekille de özetleyebiliriz:


.. graphviz::

   digraph io_pipeline {
       rankdir=TB;
       node [shape=box, style="rounded,filled", fillcolor="#D6E8FA",
             fontname="DejaVu Sans", margin="0.3,0.18", width=4];
       edge [fontname="DejaVu Sans", fontsize=9, color="#444444"];

       S1 [label="1) Program read() / write() çağırır\n(veya stdio tamponları doluysa/boşaldıysa)"];
       S2 [label="2) POSIX → sys_read / sys_write\nUser Mode ➜ Kernel Mode"];
       S3 [label="3) Page Cache kontrolü:\n· Varsa → bloke olmaz, bellekten oku/yaz\n· Yoksa → adım 4'e geç"];
       S4 [label="4) I/O çizelgeleyicisine gönderilir\nThread bloke edilir"];
       S5 [label="5) I/O Çizelgeleyicisi\n· Page Cache'te yer ayırır\n· Blok aygıt sürücüsüne iletir"];
       S6 [label="6) Blok aygıt sürücüsü\n· Sektörleri belirler\n· Page Cache adresleriyle eşleştirir\n· İsteği donanıma iletir"];
       S7 [label="7) Gerçek transfer (donanım)\n· Tamamlanınca kesme gönderilir\n· Veri artık page cache'tedir\n· Thread'in blokesi çözülür",
           fillcolor="#D5F5D5"];
       S8 [label="8) Kernel Mode → User Mode\n· Okuma: veri kullanıcıya kopyalanır\n· Yazma: geri dönüş yapılır",
           fillcolor="#D5F5D5"];

       S1 -> S2 -> S3 -> S4 -> S5 -> S6 -> S7 -> S8;
   }

Linux sistemlerinde yukarıda özetlediğimiz olaylar silsilesi zaman içerisinde değişikliklere
uğratılarak ve sürekli geliştirilerek bugünkü durumuna getirilmiştir.


Yazma İşleminin Ayrıntıları
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Buradaki süreçte yazma olayı söz konusu olduğunda bazı ayrıntılar da devreye girmektedir.
Kullanıcı modundaki program ``write`` POSIX fonksiyonunu çağırıp bu fonksiyon da ``sys_write``
fonksiyonunu çağırdığında bu sistem fonksiyonu yazılmak istenen bilgiler diske yazılana kadar
``write`` işlemini yapan thread'i bloke etmez. Yazma işlemi her zaman Linux'un RAM'deki sayfa
önbelleğine yapılmaktadır. ``sys_write`` fonksiyonu yazmayı sayfa önbelleği içerisine yaptıktan
sonra hemen "başarılı" olarak geri dönmektedir.

Sistem programlama terminolojisinde IO işlemlerinde *senkron* terimi "fonksiyon geri döndüğünde
tüm işlemlerin yapılıp bitmiş olması" anlamına gelmektedir. *Asenkron* terimi ise "işlemin
başlatılması, fonksiyonun geri dönmesi ancak işlemin aslında arka planda devam etmesi" anlamına
gelmektedir. Görüldüğü gibi modern işletim sistemlerinde diske yazma işlemi aslında disk 
bağlamında *senkron* bir işlem değildir.

Ancak bunun bir istisnası vardır. Eğer bir dosya ``O_DSYNC`` ya da ``O_SYNC`` bayraklarıyla
açılmışsa o dosyaya yapılan yazma işlemleri aygıta aktarılana kadar thread ``write`` fonksiyonunda
bloke edilmektedir. Yani bu bayraklar yazma işlemlerinin senkron yapılmasını sağlamaktadır.

Gecikmeli Yazım ve Flush Thread'leri
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Peki yazma işleminde sayfa önbelleğine yazılan bilgiler çekirdek tarafından ne zaman gerçek
aygıta aktarılmaktadır? İşte işletim sistemleri bu tür durumlarda kasten araya belli bir gecikme
koymaktadır. Böylece peşi sıra yapılan ``write`` işlemlerinin tek tek gereksiz biçimde aygıta
yapılması engellenir, bunlar biriktirilerek ve çizelgelenerek blok aygıt sürücüsüne aktarılır.
Bu biçimdeki aktarmaya *gecikmeli yazım (delayed write)* da denilmektedir.

Buradaki süreci aşağıdaki şekille özetleyebiliriz:

.. graphviz::

   digraph delayed_write {
       rankdir=LR;
       node [shape=box, style="rounded,filled", fillcolor="#D6E8FA",
             fontname="DejaVu Sans", margin="0.25,0.18"];
       edge [fontname="DejaVu Sans", fontsize=9, color="#444444"];

       write   [label="write()\nKullanıcı Modu"];
       sysw    [label="sys_write()\nÇekirdek Modu"];
       cache   [label="Page Cache'e kopyala\n(sayfa \"dirty\" olarak işaretlenir)",
                fillcolor="#FFF3CD"];
       ret     [label="Geri dönüş\n(User Mode)", fillcolor="#D5F5D5"];
       flush   [label="Flusher Thread\n(Asenkron)", fillcolor="#F8D7DA"];
       sched   [label="I/O Çizelgeleyici"];
       driver  [label="Blok Aygıt\nSürücüsü"];
       ctrl    [label="Disk\nDenetleyicisi"];
       disk    [label="Disk\nDonanımı", fillcolor="#D5F5D5"];

       write  -> sysw  -> cache -> ret;
       cache  -> flush [style=dashed, label="zaman geçince"];
       flush  -> sched -> driver -> ctrl -> disk;
   }

Peki işletim sistemi transfer işlemlerini ne kadar süre bekletmektedir? Eğer transfer çok uzun süre bekletilirse 
elektrik kesilmesi gibi durumlarda kayıplar fazlalaşır. İşte modern işletim sistemlerinde kirlenmiş sayfaların 
*flush* edilmesi *çekirdek thread'leri (kernel threads)* tarafından yapılmaktadır. Örneğin Linux sistemlerinde 
bu işlemlerden *flush* isimli çekirdek thread'leri sorumludur. Eskiden Linux çekirdeklerinin 2.6.32 versiyonuna 
kadar bu işşlemler *pdflush* isimli tek bir çekirdek thread tarafından yapılıyordu. Bu versiyondan sonra
artık her blok aygıt sürücüsü için ayrı bir flush thread'i oluşturulmaya başlandı. Bu thread'leri komut satırında 
şöyle görüntüleyebilirsiniz:

.. code-block:: bash

   $ ps -aux | grep flush

flush thread'leri arka planda sürekli olarak sayfa önbelleğini izler. Orada *kirlenmiş (dirty)*
olan sektörleri ilgili blok aygıt sürücüsüne gönderir. Peki bu işleyişte yazma gecikmesi takriben kaç saniye 
civarında olmaktadır? Aslında bu gecikme süresi başka faktörlere de bağlı olarak değişebilmketedir Burada fikir 
vermek amacıyla istersek modern Linux sistemleri için bu sürenin ortalama 5 saniye civarında olduğunu söyleyebiliriz. 
Ancak bu değerler de değiştirilebilmektedir. flush thread'lerinin parametreleri hakkında aşağıda tabloda özet bir 
bilgi veriyoruz:

.. rst-class:: centered-headers

.. list-table::
   :header-rows: 1
   :widths: 28 18 60

   * - Parametre
     - Varsayılan Değer
     - Anlamı
   * - ``dirty_writeback_centisecs``
     - 500
     - Flusher thread'in periyodik olarak çalıştığı aralık (santi saniye
       cinsinden). 500 cs = 5 saniye. Bu aralıkta çekirdek *dirty* sayfaları
       kontrol eder.
   * - ``dirty_expire_centisecs``
     - 3000
     - Bir *dirty* sayfa en fazla bu kadar süre (santi saniye cinsinden)
       RAM'de kalabilir. 3000 cs = 30 saniye sonra *süresi dolmuş* sayılır
       ve flush edilir.
   * - ``dirty_ratio`` / ``dirty_background_ratio``
     - %20 / %10 civarı
     - RAM'in ne kadarı *dirty* sayfalarla dolarsa flush işleminin
       başlatılacağını belirler (bellek baskısı durumunda
       zaman beklenmez).
       
Bu değerler proc dosya sisteminden görüntülenebilmektedir:

.. code-block:: bash

   $ cat /proc/sys/vm/dirty_writeback_centisecs
   $ cat /proc/sys/vm/dirty_expire_centisecs

*sysctl* komutu ile de bu değerler değiştirilebilmektedir:

.. code-block:: bash

   $ sudo sysctl -w vm.dirty_writeback_centisecs=100

*sysctl* komutu zaten kendi içerisinde ``/proc/sys`` dizinindeki dosyalar üzerinde güncelleme
işlemleri yapmaktadır.

flush thread'lerinin çalışması daha ayrıntılı olarak *sayfa önbelleği (page cache)* konusunun
ele alındığı bölümde açıklanacaktır.

Gecikmeli Yazımın Gerekçeleri
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Gecikmeli yazım (delayed write)* işleminin gerekçeleri nelerdir? En önemli gerekçe peşi sıra
yapılan yazma işlemlerinin tek hamlede aygıta yansıtılmasıdır. Bu sayede yazma işlemini yapan
thread bloke olmaz ve toplamda bu işlemler paralel yürütüldüğü için sistem performansı yükselir.
Aynı zamanda flash belleklerde ve SSD'lerde bu gecikme sürekli yazım sonucunda oluşan belleğin
aşınmasını (wearing) da kısmen engellemektedir. (Aslında bu "eskime" sorunu asıl olarak flash
belleklerdeki ve SSD içerisindeki önbellekler ve *FTL (Flash Translation Layer)* sayesinde 
azaltılmaktadır.)

Kirlenmiş Sayfaların Erken Temizlenmesi
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sayfa önbelleğinde kirlenen sayfalar bazı durumlarda işletim sisteminin *tazeleyici (flusher)*
thread'lerini beklemeden de diske aktarılabilmektedir. Örneğin bir dosya kapatıldığında artık
bu işlem arka planda dosyanın kirlenmiş sayfalarının da diske yazılmasına yol açmaktadır.

UNIX/Linux sistemlerinin çoğunda bazı özel sistem fonksiyonları yoluyla ya da ``open``
fonksiyonundaki bayraklarla da bu duruma müdahale edilebilmektedir.

``sync`` POSIX fonksiyonu çağrıldığında o anda dosya sistemine ilişkin *kirlenmiş (dirty olan)*
sayfaların hepsi flush edilmektedir:

.. code-block:: c

   #include <unistd.h>

   void sync(void);

``sync`` fonksiyonu *asenkron (asynchronous)* biçimde çalışmaktadır. Yani fonksiyon geri döndüğünde tüm blokların
flush edilmiş olma garantisi yoktur. Aynı zamanda Linux sistemlerde *sync* isimli bir kabuk komutu
da bulunmaktadır. Bu komut ``sync`` fonksiyonunu çağırmaktadır.

``fsync`` POSIX fonksiyonu ise belli bir dosyaya ilişkin kirlenmiş sayfaların flush edilmesi için
kullanılmaktadır:

.. code-block:: c

   #include <unistd.h>

   int fsync(int fildes);

``fsync`` fonksiyonu *senkron (synchronous)* çalışmaktadır. Yani fonksiyon geri döndüğünde sayfa
önbelleğindeki kirlenmiş sayfaların flush edilmiş olması garanti edilmektedir.

Bir dosya açılırken ``open`` POSIX fonksiyonunda kullanılan konuyla ilgili üç bayrak vardır:

``O_DSYNC`` **Bayrağı**
   Bu bayrak POSIX'in *"Base Definitions"* bölümündeki *"Synchronized I/O Data Integrity Completion"*
   başlığında açıklanan yazma koşullarının sağlanacağını belirtmektedir. Bu bayrak kullanıldığında
   aşağıdaki iki durumun çekirdek tarafından sağlanması garanti edilmektedir:

   - Dosyaya yazdırılan bilgilerin ``write`` fonksiyonu geri döndüğünde hedefe transfer edilmiş
     olması.
   - Yazılan bilginin dosyadan okunabilmesi için gereken metadata bilgilerinin hedefe transfer
     edilmiş olması. (Tüm metadata bilgilerinin hedefe transfer edilmiş olması gerekmemektedir.)

``O_SYNC`` **Bayrağı**
   Bu bayrak POSIX'in *"Base Definitions"* bölümündeki *"Synchronized I/O File Integrity Completion"*
   başlığında açıklanan koşulların sağlanacağını belirtmektedir. ``O_SYNC`` bayrağı ``O_DSYNC``
   bayrağını kapsamaktadır. Fakat bu bayrak ``write`` fonksiyonu geri dönmeden önce tüm metadata
   bilgilerinin hedefe transfer edilmiş olmasını zorunlu tutmaktadır.

``O_RSYNC`` **Bayrağı**
   Bu okuma işlemi ile ilgilidir. Tek başına değil ``O_DSYNC`` ya da ``O_SYNC`` bayraklarıyla
   birlikte kullanılır. Eğer ``O_RSYNC`` bayrağı ``O_DSYNC`` bayrağı ile birlikte kullanılırsa
   ``read`` işlemini etkileyecek olan daha önce yapılmış ``write`` işlemleri varsa ``read``
   fonksiyonu geri dönmeden önce bu ``write`` işlemleri için ``O_DSYNC`` bayrağında belirtilen
   semantik uygulanmaktadır. Eğer bu bayrak ``O_SYNC`` ile birlikte kullanılırsa ``read`` işlemini
   etkileyecek olan daha önce yapılmış ``write`` işlemleri varsa ``read`` fonksiyonu geri dönmeden
   önce bu ``write`` işlemleri için ``O_SYNC`` bayrağında belirtilen semantik uygulanmaktadır.


Standart C Kütüphanesinin Süreçteki Yeri
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Peki C'nin standart dosya fonksiyonları bu süreçte nerede yer almaktadır? C'nin dosya fonksiyonları
aslında neticede POSIX fonksiyonlarını çağırmaktadır. Ancak C'nin standart dosya fonksiyonları
işletim sisteminin okuma yazma fonksiyonlarını daha az çağırmak için *kullanıcı alanında (user
space)* her dosya için bir önbellek de oluşturmaktadır. Bu önbellek sistemine genellikle önbellek
yerine *tamponlama (buffering)* sistemi, burada kullanılan önbelleğe de *tampon (buffer)*
denilmektedir.

Örneğin Linux'ta biz C'nin ``getc`` gibi dosya fonksiyonunu çağırmış olalım. Standart C
kütüphanesi ``fgetc`` ile 1 byte okumak istediğimizde ``read`` POSIX fonksiyonu ile 1 byte
okumamaktadır. ``fgetc`` fonksiyonu ``read`` POSIX fonksiyonu ile ``<stdio.h>`` dosyasında belirtilen 
``BUFSIZ`` kadar byte'ı bir tampona okumakta ve oradan 1 byte'ı programcıya vermektedir.  Böylece sonradan 
okunanacak byte'lar için hiç read fonksiyonu çağrılmayacak ve istek hemen bu tampondan karşılanacaktır. Aynı 
durum yazma için de söz konusudur. Bu nedenle C'nin standart dosya fonksiyonlarına *tamponlı IO (buffered IO)* 
fonksiyonları da denilmektedir. Buradaki önbellek sisteminin POSIX fonksiyonlarını dolayısıyla da sistem 
fonksiyonlarını daha az çağırmak için oluşturulduğuna dikkat ediniz. O hâlde C'nin standart dosya fonksiyonlarıyla 
yapılan tipik bir okuma işlemi şöyle gerçekleşmektedir:

.. graphviz::

   digraph read_chain {
       rankdir=TB;
       node [shape=box, style="rounded,filled", fillcolor="#D6E8FA",
             fontname="DejaVu Sans", margin="0.3,0.2"];
       edge [fontname="DejaVu Sans", fontsize=10, color="#444444"];

       C      [label="C'deki okuma fonksiyonu"];
       POSIX  [label="read() — POSIX fonksiyonu"];
       Sys    [label="sys_read() — Sistem fonksiyonu"];
       Dots   [label="...", shape=plaintext, style="",
               fontname="DejaVu Sans", fontsize=16];

       C     -> POSIX [label="Tampona bakılıyor",
                        fontsize=13, fontcolor="#1a5fa8"];
       POSIX -> Sys   [label="Çekirdek moduna geçiliyor",
                        fontsize=13, fontcolor="#1a5fa8"];
       Sys   -> Dots;
   }

Tabii biz kursumuzda okuma ve yazma süreçleri üzerinde dururken olaylar silsilesini standart C fonksiyonlarından 
başlatmayacağız. POSIX fonksiyonlarından ya da sistem fonksiyonlarından başlatacağız.

C'deki bu tamponlama yani önbellek mekanizması aslında yalnızca C'ye özgü değildir. Diğer prgramlama dillerinin de 
standart kütüphanelerinde benzer biçimde tamponlamalar yapılmaktadır. Örneğin C++'taki ``<iostream>`` fonksiyonları, 
C#'tan kullanılan .NET sınıfları, Java'da kullanılan IO sınıfları, C'de olduğu gibi hep kullanıcı alanında 
oluşturulan tamponlama mekanizması eşliğine çalışmaktadır. Ancak bunların hepsi Linux sistemlerinde neticede POSIX 
fonksiyonlarını, onlar da sistem fonksiyonlarını çağırmaktadır.

POSIX dosya fonksiyonlarının Linux'taki işletim sisteminin sistem fonksiyonlarını çağırdığını belirtmiştik. İşletim 
sisteminin sistem fonksiyonları ilgili disk bloğu sayfa önbellekte olsa bile belli bir yavaşlık oluşturmaktadır. 
Programın akışının kullanıcı modundan çekirdek moduna geçirilmesi ve akışın ilgili sistem fonksiyonuna aktarılması 
göreli bir zaman kaybına yol açmaktadır. Bu nedenle ayrıca bu kütüphanelerin kullanıcı modunda tamponlama yapması 
önemli olmaktadır.

UNIX/Linux sistemlerinde kullanılan standart C kütüphaneleri aynı zamanda POSIX fonksiyonlarını
da içermektedir. Bilindiği gibi bugün masaüstü Linux sistemlerinde en fazla kullanılan standart C
kütüphanesi GNU'nun *libc* kütüphanesidir. Eğer standart C fonksiyonlarının ve POSIX
fonksiyonlarının nasıl yazıldığını merak ediyorsanız gömülü Linux sistemleri için daha minimalist
biçimde yazılmış olan kütüphanelerin kaynak kodlarını inceleyebilirsiniz. Bu iş için iki alternatif
*musl* ve *uclibc* kütüphaneleridir. *uclibc* kütüphanesine *Mikro C kütüphanesi* de denilmektedir.
Bu kütüphanelerin kaynak kodlarını `elixir.bootlin.com <https://elixir.bootlin.com>`_ sitesinden
inceleyebilirsiniz. Bu site yalnızca Linux çekirdekleri için değil başka projeler için de kodlar
üzerinde gezinme olanağı sunmaktadır. Sadeliği nedeniyle *musl* kütüphanesini incelemenizi salık
veririz. Kütüphanenin kodları üzerinde gezinebilmek için aşağıdaki bağlantıdan
faydalanabilirsiniz:

`https://elixir.bootlin.com/musl/v1.2.5/source <https://elixir.bootlin.com/musl/v1.2.5/source>`_

task_struct İçerisindeki Dosya Sistemine İlişkin Veri Yapıları
--------------------------------------------------------------

Şimdiye kadar blok ve sektör düzeyinde okuma yazmaların kabaca nasıl gerçekleştirildiğini
açıkladık. Ancak çekirdeğin açık dosyalar için oluşturduğu organizasyon hakkında bilgi vermedik.
Şimdi sürecin bu yönü üzerinde duracağız.

Anımsanacağı gibi UNIX/Linux sistemlerinde dosyalar ``open`` isimli POSIX fonksiyonuyla
açılmaktadır. ``open`` POSIX fonksiyonu başarı durumunda ismine *dosya betimleyicisi (file
descriptor)* denilen bir handle değeri vermektedir. ``read``, ``write``, ``lseek``, ``close``
gibi POSIX'in diğer dosya fonksiyonları bu dosya betimleyicisini parametre olarak alıp hangi
dosya üzerinde işlem yapılacağını bu betimleyiciden hareketle belirlemektedir. ``open``, 
``read``, ``write``, ``lseek``, ``close`` gibi POSIX'in temel dosya fonksiyonları Linux 
sistemlerinde aslında neredeyse doğrudan Linux'un ilgili sistem fonksiyonlarını çağırmaktadır:

.. code-block:: none

   open  ---> sys_open
   read  ---> sys_read
   write ---> sys_write
   lseek ---> sys_lseek
   close ---> sys_close

Bu nedenle birtakım ayrıntıları da göz ardı edersek biz Linux sistemlerinde dosya işlemlerini
yapan temel POSIX fonksiyonlarının aslında doğrudan ``sys_xxx`` sistem fonksiyonlarını çağırdığını
varsayabiliriz.

``task_struct`` yapısı (proses kontrol bloğu) içerisinde proseslere ilişkin dosya işlemleri için
kullanılan iki önemli eleman bulunmaktadır:

.. code-block:: c

   struct task_struct {
       /* ... */

       /* Filesystem information: */
       struct fs_struct        *fs;

       /* Open file information: */
       struct files_struct     *files;

       /* ... */
   };

Bu iki eleman çok uzun süredir ``task_struct`` yapısı içerisinde bulunmaktadır. Ancak buradaki
``fs_struct`` ve ``files_struct`` yapılarının içeriğinde çekirdeğin versiyonları ilerledikçe
çeşitli değişiklikler de yapılmıştır.

fs_struct Yapısı
~~~~~~~~~~~~~~~~

``fs_struct`` yapısı açık dosyalara ilişkin yapılan organizasyonla ilgili değildir.
Prosesin kök dizini ve çalışma dizini gibi dosya sistemine ilişkin proses bilgileri burada
tutulmaktadır. Mevcut çekirdeklerde ``fs_struct`` yapısı ``include/linux/fs_struct.h`` dosyası
içerisinde şöyle bildirilmiştir:

.. code-block:: c

   struct fs_struct {
       int users;
       spinlock_t lock;
       seqcount_spinlock_t seq;
       int umask;
       int in_exec;
       struct path root, pwd;
   } __randomize_layout;

Buradaki ``root`` ve ``pwd`` elemanları sırasıyla prosesin kök dizinini ve çalışma dizinini
(current working directory) tutmaktadır. ``umask`` elemanı ise prosesin umask değerini
tutmaktadır. Buradaki ``path`` yapısı da şöyle bildirilmiştir:

.. code-block:: c

   struct path {
       struct vfsmount *mnt;
       struct dentry *dentry;
   } __randomize_layout;

``vfsmount`` ve ``dentry`` yapıları ilerleyen bölümlerde ele alınacaktır. Eskiden bu yapı biraz daha küçüktü.
Örneğin çekirdeğin 2.2'li versiyonlarında şöyleydi:

.. code-block:: c

   struct fs_struct {
       atomic_t count;
       int umask;
       struct dentry * root, * pwd;
   };

Çekirdeğin 2.4'te şu hale getirildi:

.. code-block:: c

   struct fs_struct {
       atomic_t count;
       rwlock_t lock;
       int umask;
       struct dentry * root, * pwd, * altroot;
       struct vfsmount * rootmnt, * pwdmnt, * altrootmnt;
   };

2.6'da ise şu hale getirildi:

.. code-block:: c

   struct fs_struct {
       int users;
       spinlock_t lock;
       seqcount_t seq;
       int umask;
       int in_exec;
       struct path root, pwd;
   };

Çekirdeğin öğrenci ödevi gibi olan 0.01 versiyonunda bu yapı yoktu. Bu yapıdaki bilgiler doğrudan
``task_struct`` içerisinde bulunmaktaydı:

.. code-block:: c

   struct task_struct {
       /* ... */

       unsigned short umask;
       struct m_inode * pwd;
       struct m_inode * root;
       unsigned long close_on_exec;

       /* ... */
   };

Ayrıntıları göz ardı edersek bu ``fs_struct`` yapısındaki en önemli elemanlar "prosesin kök dizinin yeri",
"prosesin çalışma dizinin yeri" ve "prosesin *umask* değeri" dir.

files_struct Yapısı
~~~~~~~~~~~~~~~~~~~

``task_struct`` içerisindeki ``files`` isimli gösterici prosesin açmış olduğu dosyalara ilişkin
bilgilerin tutulduğu ``files_struct`` türünden yapı nesnesini göstermektedir. ``files_struct``
yapısı da zaman içerisinde değişikliklere uğratılmıştır. Güncel çekirdeklerde bu yapı
``include/linux/fdtable.h`` dosyası içerisinde şöyle bildirilmiştir:

.. code-block:: c

   struct files_struct {
   /*
    * read mostly part
    */
       atomic_t count;
       bool resize_in_progress;
       wait_queue_head_t resize_wait;

       struct fdtable __rcu *fdt;
       struct fdtable fdtab;
   /*
    * written part on a separate cache line in SMP
    */
       spinlock_t file_lock ____cacheline_aligned_in_smp;
       unsigned int next_fd;
       unsigned long close_on_exec_init[1];
       unsigned long open_fds_init[1];
       unsigned long full_fds_bits_init[1];
       struct file __rcu * fd_array[NR_OPEN_DEFAULT];
   };

2.6'lı çekirdeklerde bu yapı şöyleydi:

.. code-block:: c

   struct files_struct {
   /*
    * read mostly part
    */
       atomic_t count;
       struct fdtable __rcu *fdt;
       struct fdtable fdtab;
   /*
    * written part on a separate cache line in SMP
    */
       spinlock_t file_lock ____cacheline_aligned_in_smp;
       int next_fd;
       struct embedded_fd_set close_on_exec_init;
       struct embedded_fd_set open_fds_init;
       struct file __rcu * fd_array[NR_OPEN_DEFAULT];
   };

2.4'lü çekirdeklerde şöyleydi:

.. code-block:: c

   struct files_struct {
       atomic_t count;
       rwlock_t file_lock;
       int max_fds;
       int max_fdset;
       int next_fd;
       struct file ** fd;          /* current fd array */
       fd_set *close_on_exec;
       fd_set *open_fds;
       fd_set close_on_exec_init;
       fd_set open_fds_init;
       struct file * fd_array[NR_OPEN_DEFAULT];
   };

2.2'li çekirdeklerde bu yapı bir eleman dışında aşağı yukarı aynıydı:

.. code-block:: c

   struct files_struct {
       atomic_t count;
       int max_fds;
       int max_fdset;
       int next_fd;
       struct file ** fd;      /* current fd array */
       fd_set *close_on_exec;
       fd_set *open_fds;
       fd_set close_on_exec_init;
       fd_set open_fds_init;
       struct file * fd_array[NR_OPEN_DEFAULT];
   };

Çekirdeğin 0.01 versiyonunda bu bilgiler doğrudan ``task_struct`` içerisinde bulunuyordu:

.. code-block:: c

   struct task_struct {
       /* ... */

       unsigned short umask;
       struct m_inode * pwd;
       struct m_inode * root;
       unsigned long close_on_exec;

       /* ... */
   };

Dosya Nesnesi (struct file)
----------------------------

Linux'ta ne zaman ``open`` POSIX fonksiyonuyla bir dosya açılsa ``sys_open`` sistem fonksiyonu
açılan dosya için ``file`` isimli (``struct file`` türünden) bir yapı nesnesini tahsis edip
dosya işlemleri için gereken bilgileri bu yapı nesnesinin içerisine yerleştirmektedir.
``sys_read``, ``sys_write``, ``sys_lseek``, ``sys_close`` gibi sistem fonksiyonları da dosya
üzerinde işlem yapabilmek için bu ``file`` yapısındaki bilgileri kullanmaktadır. İşletim
sistemlerinde bu amaçla kullanılan nesnelere *dosya nesnesi (file object)* de denilmektedir.
Tabii sistem fonksiyonları ve çekirdek bu dosya nesnelerine ``task_struct`` nesnesinden hareketle 
erişmektedir. Zaten ``files_struct`` yapısı bu erişime ilişkin bilgileri de içermektedir. Biz aşağıdaki 
gibi bir dosya açmış olalım:

.. code-block:: c

   fd = open(...);

``sys_open`` sistem fonksiyonu açılmak istenen dosyanın diskteki yerini ve metadata bilgilerini bulur. O bilgilerden
hareketle bir dosya nesnesi (file object) oluşturur. O dosya nesnesinin adresini de izleyen paragrafta açıklayacağımız
gibi ``files_struct`` nesnesinin içerisine yerleştirir. Böylece ``sys_read``, ``sys_write``, ``sys_lseek``,
``sys_close`` gibi sistem fonksiyonları ``task_struct`` nesnesinden hareketle bu dosya nesnesine erişebilmektedir.
Güncel çekirdeklerde ``file`` yapısı ``include/linux/fs.h`` dosyasının içerisinde şöyle bildirilmiştir:

.. code-block:: c

   struct file {
       spinlock_t                   f_lock;
       fmode_t                      f_mode;
       const struct file_operations *f_op;
       struct address_space        *f_mapping;
       void                        *private_data;
       struct inode                *f_inode;
       unsigned int                 f_flags;
       unsigned int                 f_iocb_flags;
       const struct cred           *f_cred;
       struct fown_struct          *f_owner;
       /* --- cacheline 1 boundary (64 bytes) --- */
       struct path                  f_path;
       union {
           struct mutex             f_pos_lock;
           u64                      f_pipe;
       };
       loff_t                       f_pos;
   #ifdef CONFIG_SECURITY
       void                        *f_security;
   #endif
       /* --- cacheline 2 boundary (128 bytes) --- */
       errseq_t                     f_wb_err;
       errseq_t                     f_sb_err;
   #ifdef CONFIG_EPOLL
       struct hlist_head           *f_ep;
   #endif
       union {
           struct callback_head     f_task_work;
           struct llist_node        f_llist;
           struct file_ra_state     f_ra;
           freeptr_t                f_freeptr;
       };
       file_ref_t                   f_ref;
       /* --- cacheline 3 boundary (192 bytes) --- */
   } __randomize_layout
   __attribute__((aligned(4)));

Eskiden bu yapının içeriği daha küçüktü. Zaman içerisinde bu yapıda da değişilikler ve eklemeler yapılmıştır.

Dosya Betimleyici Tablosu (File Descriptor Table)
-------------------------------------------------

Şimdi ``sys_open`` sistem fonksiyonuyla bir dosya açıldığında dosya betimleyicisinin (file descriptor) nasıl elde
edildiğini açıklayalım. Güncel çekirdeklerde bu sürece ilişkin veri yapısı biraz ayrıntılıdır. Biz bu ayrıntılardan
bahsedeceğiz ancak önce çekirdeğin "öğrenci ödevi gibi olan" 0.01 versiyonunda bu süreci açıklayalım. Bu ilkel
versiyonda henüz ``files_struct`` biçiminde bir yapı yoktu. Açık dosya bilgileri doğrudan ``task_struct`` içerisinde
bulunan aşağıdaki elemanlarda saklanıyordu:

.. code-block:: c

   struct task_struct {
       /* ... */

       unsigned long close_on_exec;
       struct file *filp[NR_OPEN];

       /* ... */
   };

Burada ``filp`` isimli dizinin ``struct file *`` türünden olduğuna dikkat ediniz. Yani ``filp``
dizisi file nesnelerinin adreslerini tutan bir gösterici dizisidir. Bu versiyonda ``NR_OPEN``
şöyle tanımlanmıştır:

.. code-block:: c

   #define NR_OPEN 20

İzleyen paragraflarda da anlayacağınız üzere bu ilkel versiyonda bir proses en fazla 20 dosyayı açık durumda
tutabiliyordu. UNIX/Linux dünyasında dosya nesnelerinin adreslerini tutan bu gösterici dizilerine *dosya betimleyici
tablosu (file descriptor table)* denilmektedir. Yukarıda da belirttiğimiz gibi dosya betimleyici tablosu dosya
nesnelerinin adreslerini tutan bir gösterici dizisi biçimindedir. Bunu 0.01 çekirdeği için şöyle bir şekille
gösterebiliriz:

.. graphviz::

   digraph fd_table {
       rankdir=LR;
       node [fontname="DejaVu Sans"];

       table [
           shape=none,
           label=<
           <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6">
             <TR><TD BGCOLOR="#D6E8FA"><B>İndeks</B></TD><TD BGCOLOR="#D6E8FA"><B>Gösterici</B></TD></TR>
             <TR><TD>0</TD><TD PORT="f0">●</TD></TR>
             <TR><TD>1</TD><TD PORT="f1">●</TD></TR>
             <TR><TD>2</TD><TD PORT="f2">●</TD></TR>
             <TR><TD>3</TD><TD PORT="f3">●</TD></TR>
             <TR><TD>...</TD><TD>...</TD></TR>
             <TR><TD>18</TD><TD>(boş)</TD></TR>
             <TR><TD>19</TD><TD>(boş)</TD></TR>
           </TABLE>>
       ];

       fo0 [label="Dosya Nesnesi\n(fd=0)", shape=box, style="rounded,filled", fillcolor="#D5F5D5"];
       fo1 [label="Dosya Nesnesi\n(fd=1)", shape=box, style="rounded,filled", fillcolor="#D5F5D5"];
       fo2 [label="Dosya Nesnesi\n(fd=2)", shape=box, style="rounded,filled", fillcolor="#D5F5D5"];
       fo3 [label="Dosya Nesnesi\n(fd=3)", shape=box, style="rounded,filled", fillcolor="#D5F5D5"];

       table:f0 -> fo0;
       table:f1 -> fo1;
       table:f2 -> fo2;
       table:f3 -> fo3;
   }

Buradaki sayılar dizinin indekslerini belirtmektedir. Tabii zamanla dosyalar kapanınca bu dizinin elemanları boşa
düşecektir. Boş elemanlara ``NULL`` adres yerleştirilmektedir. İşte ``open`` POSIX fonksiyonunun (yani ``sys_open``
sistem fonksiyonunun) verdiği *dosya betimleyicisi (file descriptor)* aslında dosya betimleyici tablosu dizisinde
bir indeks belirtmektedir. ``open`` POSIX fonksiyonunun (dolayısıyla ``sys_open`` sistem fonksiyonunun) dosya
betimleyici tablosundaki en düşük boş indeksi vereceği POSIX standartlarında garanti edilmiştir. Dosya betimleyici 
tablosunun (yani ``struct file *``) dizisinin uzunluğunun "aynı anda açık tutulabilecek" dosya sayısını
da belirttiğine dikkat ediniz.

Dosya betimleyici tablosunun prosese özgü olduğuna dikkat ediniz. Bir proseste açılmış olan dosyaya ilişkin dosya
nesnesinin adresi o prosesteki dosya betimleyici tablosuna yazılmaktadır. Dosya betimleyicileri sistem genelinde
bir değer belirtmemektedir, dosya betimleyici değerleri yalnızca ilgili proses için anlamlıdır. Örneğin 12 numaralı
betimleyici bir proseste bir dosyayı belirtirken diğer bir proseste başka bir dosyayı belirtiyor olabilir.
Dolayısıyla biz bir proseste bir dosya açıp elde ettiğimiz dosya betimleyicisini başka bir prosese prosesler arası
haberleşme yöntemleriyle iletsek o proseste o betimleyicinin hiçbir anlamı olmaz. Ancak anımsanacağı gibi özel bir
durum olarak üst proses ``fork`` işlemi yaptığında üst prosesin dosya betimleyici tablosu alt prosese *sığ (shallow)*
kopyalanmaktadır. Böylece üst proses ile alt proses aynı dosya üzerinde işlem yapabilmektedir. (Linux çekirdeklerinde 
trace işlemleri için ``sys_pidfd_getfd`` isimli bir sistem fonksiyonu bulundurulmuştur. Bu sistem fonksiyonu başka bir 
prosesin dosya betimleyici tablosunda betimleyici tahsis etmektedir. Ayrıca çekirdekte başka bir prosesten açmış olduğu 
dosyaya ilişkin  bir betimleyicinin elde edilmesini sağlayan ``sys_pidfd_open`` isimli bir sistem fonksiyonu da 
bulunmaktadır.)

Yukarıdaki 0.01 versiyonunda konuyla ilgili ``unsigned long`` türden ``close_on_exec`` isimli bir elemanın da
bulunduğunu görüyorsunuz. Bu elemanın her biti bir betimleyicinin "close-on-exec" durumunu belirtmektedir. Söz
konusu bit 1 ise ilgili betimleyici ``exec`` işlemleri sırasında kapatılır, 0 ise kapatılmaz. POSIX standartlarında
bir dosya açıldığında close-on-exec bayrağının varsayılan durumda 0 olduğu belirtilmiştir. (Yani varsayılan durumda
``exec`` işlemlerinde dosya kapatılmamaktadır.) Bu ilkel versiyonda zaten bir prosesin maksimum açık tutacağı dosya
sayısı 20'dir. O zamanlarda ``long`` türü 32 bitti. Yani bu ``unsigned long`` eleman bütün dosya betimleyicilerinin
*close-on-exec* bayraklarını tutmak için yeterliydi.

İlk Boş Betimleyicinin Bulunması
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``sys_open`` sistem fonksiyonu öncelikle dosya betimleyici tablosundaki ilk boş betimleyiciyi bulmaya çalışır.
Çünkü dosya betimleyici tablosu tamamen doluysa zaten bir dosya nesnesinin oluşturulup işlemlere devam edilmesinin
de bir anlamı olmayacaktır. Peki dosya betimleyici tablosundaki ilk boş betimleyici nasıl bulunmaktadır? Düz
mantıkla "mademki dosya betimleyici tablosundaki boş indekslerde ``NULL`` adres var o zaman ilk ``NULL`` adres
görülene kadar bir döngü ile sıralı arama yapılabilir" diye düşünebilirsiniz. Eğer dosya betimleyici tabloları
0.01 versiyonundaki gibi çok küçük olsaydı sıralı arama yapmanın önemli bir sakıncası olmayabilirdi. Gerçekten
de 0.01 versiyonunda boş betimleyici şöyle bulunmuştur:

.. code-block:: c

   int sys_open(const char * filename, int flag, int mode) {
       /* ... */

       for (fd = 0; fd < NR_OPEN; fd++)
           if (!current->filp[fd])
               break;

       /* ... */
   }

Görüldüğü gibi bu ilkel versiyonda dosya betimleyici tablosu üzerinde tek tek sıralı arama yapılmış, ilk boş
betimleyici (yani ``NULL`` adres içeren ilk dizi elemanının indeksi) elde edilmiştir. Ancak uzunca bir süredir
proseslerin varsayılan dosya betimleyici tablolarının varsayılan uzunlukları 1024'tür ve bu uzunluk da
büyütülebilmektedir. 1024 elemanlı bir tabloda sıralı arama ile ilk ``NULL`` olan dizi elemanının indeksinin
bulunması yavaş bir işlemdir. İşte bir süre sonra Linux çekirdeklerinde bu arama işlemi bit düzeyinde aramayla
hızlandırılmıştır. 

Bit düzeyinde arama yönteminde dosya betimleyici tablosunun uzunluğu kadar bit dizisi oluşturulur. Sonra o bit 
dizisindeki ilk 0 olan bitin indeksi bulunmaya çalışılır. Bu bit dizisindeki 0 olan bitler betimleyici tablosundaki 
boş elemanları, 1 olan bitler dolu olan elemanları belirtmektedir. İşlemcilerde belli bir yazmaçtaki (ya da Intel 
işlemcileri söz konusuysa bellek adresindeki) "ilk 0 olan bitin indeksini veren özel makine komutları" bulunmaktadır. 
Tabii işlemci 32 bit ise bu makine komutları 32 bitlik yani 4 byte'lık bir veri üzerinde, 64 bit ise 64 bitlik yani 
8 byte'lık bir veri üzerinde işlem yapabilmektedir. Örneğin elimizdeki işlemcinin 64 bit olduğunu düşünelim. Bu 
işlemcilerdeki C derleyicilerinde ``unsigned long`` türü 8 byte yani 64 bittir. Bu durumda örneğin 1024 eleman 
uzunluğundaki dosya betimleyici tablosu için 16 elemanlı bir ``unsigned long`` dizi bitmap olarak kullanılabilir. 
Tabii bu sistemlerde ilk 0 bitini bulan makine komutları zaten 64 bitlik bir bilgi üzerinde bu işi yapabilmektedir.
O halde çekirdek tasarımcısı 16 elemanlı bir döngü kullanıp dizinin her elemanı için bu özel makine komutunu 
kullanarak işlemleri hızlandırabilir. Ancak belli bir süreden sonra bu yöntem de biraz daha geliştirilerek arama 
işlemi biraz daha hızlandırılmıştır. Bu ikinci hızlandırma yönteminde ikinci bir bit dizisi kullanılmaktadır. 
Ancak ikinci bit dizisinin her biti birinci bit dizisindeki ``unsigned long`` elemanın tüm bitlerinin 0 olup 
olmadığını tutmaktadır. Bu durumda güncel çekirdeklerde önce bu ikinci bit dizisindeki ilk 1 olan bit bulunur.
Sonra bu bitin indeksi birinci bit dizisine indeks yapılarak oradaki ``unsigned long`` değer içerisinde ilk 0 
olan bit elde edilir. Bu yöntemde örneğin birinci bit dizisinin aşağıdaki gibi olduğunu varsayalım:

.. code-block:: text

   1111 1111 1111 1111 1111 1111 1111 1111 1111 1111 - 1111 1111 1111 1111 1111 1111 1111 1111 1111 1111 -
   1111 1111 1111 1111 1111 1111 1111 1111 1111 1111 - 1111 1101 1111 1111 1111 1111 1111 1111 1111 1111 - ....

Burada birinci bit dizisi ``unsigned long`` dizi biçimindedir. Görüldüğü gibi bu dizinin ilk üç elemanında hiç
0 olan bit yoktur. İlk 0 olan bit 3'üncü indekstedir. Bu durumda ikinci bit dizisi de aşağıdaki gibi olacaktır:

.. code-block:: text

   0001.....

Bu hızlandırma mantığında önce ikinci bit dizisindeki ilk 1 olan bitin indeksi elde edilir. Örneğimizde bu
3'tür. Sonra birinci bit dizisinin 3'üncü indeksteki ``unsigned long`` elemanında ilk 0 olan bitin indeksi
bulunur. Bu yöntemde birkaç makine komutuyla istenen bilginin elde edilebildiğine dikkat ediniz.

Çekirdek dokümantasyonunda her dosya betimleyicisinin boş mu dolu mu olduğunu tutan bitmap'e "birinci düzey
bitmap", bu bitmap'teki ilk boş ``unsigned long`` elemanın dizi indeksini veren ikinci bitmap'e ise "ikinci
düzey bitmap" denilmektedir.

2.6 çekirdeğine kadar (bu çekirdek de dahil) bit dizileri için ``fd_set`` isimli bir yapı kullanılıyordu. Sonraları
bu ``fd_set`` yapısı bırakıldı. Örneğin çekirdeğin 2.2 ve 2.4 versiyonundaki ``include/linux/sched.h`` içerisindeki
``files_struct`` yapısı şöyleydi:

.. code-block:: c

   struct files_struct {
       atomic_t count;
       rwlock_t file_lock;     /* Protects all the below members. Nests inside tsk->alloc_lock */
       int max_fds;
       int max_fdset;
       int next_fd;
       struct file ** fd;      /* current fd array */
       fd_set *close_on_exec;
       fd_set *open_fds;
       fd_set close_on_exec_init;
       fd_set open_fds_init;
       struct file * fd_array[NR_OPEN_DEFAULT];
   };

Burada görmüş olduğunuz ``fd_set`` yapısı "bit dizilerini" temsil etmektedir. Bu yapı şöyle bildirilmiştir:

.. code-block:: c

   typedef __kernel_fd_set     fd_set;

   typedef struct {
       unsigned long fds_bits [__FDSET_LONGS];
   } __kernel_fd_set;

Buradaki ``__FDSET_LONGS`` sembolik sabiti 32 bit sistemlerde 32 değerini, 64 bit sistemlerde 16 değerini
vermektedir. Yani bu yapının içerisindeki ``fds_bits`` elemanı toplamda 1024 biti tutan ``unsigned long``
türünden dizidir. 2.6 çekirdeği dahil olmak üzere bit dizisi anlamında çekirdekte bu ``fd_set`` yapısı
kullanılmıştır. Ancak bu ``fd_set`` temsilinin tasarımında da aslında kusurlar vardır. Bu temsilde bit dizisi
büyütülmek istendiğinde artık bu ``fd_set`` temsili işe yaramaz hale gelmektedir. Bu nedenle artık güncel
çekirdeklerde ``fd_set`` yerine doğrudan ``unsigned long *`` türünden bir gösterici tutulup bu göstericinin
gösterdiği yer için belli uzunlukta ``unsigned long`` dizi tahsis edilmektedir. Aslında uzun süre kullanılmış
olan bu ``fd_set`` temsilinden vazgeçilmesi iyi olmuştur. Yukarıdaki çekirdeğin 2.4 versiyonundaki
``files_struct`` yapısında dosya betimleyici tablosunun uzunluğu yapının ``max_fds`` elemanında tutulmaktadır.
Çünkü işin başında bu tablo 1024 elemanlık olsa da daha sonra büyütülebilmektedir. Bu versiyonda dosya
betimleyici tablosunun adresinin de ``fd`` elemanında tutulduğuna dikkat ediniz. Dosyaların close-on-exec
bayrakları da yine yapının ``close_on_exec`` elemanında tutulmaktadır.

Yukarıdaki ``files_struct`` yapısı biraz kafanızı karıştırabilir. Sanki bu yapıda aynı amaçla kullanılan
birden fazla eleman varmış gibi gelebilir. Konuya açıklık getirmek amacıyla bu versiyondaki yapı elemanlarının
hepsinin işlevlerini tek tek açıklayalım:

Bir proses yaratıldığında işin başında dosya betimleyici tablosu için, boş betimleyici tespit etmek için ve
close-on-exec bayrakları için ``files_struct`` yapısı içerisinde alanlar ayrılmıştır:

.. code-block:: c

   struct files_struct {
       /* ... */

       fd_set close_on_exec_init;               /* close-on-exec bayrakları için kullanılan statik bitmap */
       fd_set open_fds_init;                    /* açık dosya betimleyicilerini tutan statik bitmap */
       struct file * fd_array[NR_OPEN_DEFAULT]; /* dosya betimleyici tablosu için ayrılmış statik dizi */

       /* ... */
   };

Burada ``NR_OPEN_DEFAULT`` 32 bit sistemlerde 32, 64 bit sistemlerde 64 değerini vermektedir. Eğer proses dosya
betimleyici tablosunu genişletmezse zaten bu tablolar ve bitmap'ler ``files_struct`` yapısı içerisinde hazır bir
biçimde tutulmaktadır.

Çekirdek her zaman dosya tablosunun yerini ``fd`` göstericisinin gösterdiği yerde, açık dosya betimleyicilerinin
bitmap'ini ``open_fds`` göstericisinin gösterdiği yerde, close-on-exec bayraklarına ilişkin bitmap'i ise
``close_on_exec`` göstericisinin gösterdiği yerde aramaktadır. Yapının bu elemanlarına dikkat ediniz:

.. code-block:: c

   struct files_struct {
       /* ... */

       struct file ** fd;          /* current fd array */
       fd_set *close_on_exec;
       fd_set *open_fds;

       fd_set close_on_exec_init;
       fd_set open_fds_init;
       struct file * fd_array[NR_OPEN_DEFAULT];

       /* ... */
   };

İşin başında varsayılan durumda ``fd`` göstericisi ``fd_array`` elemanını, ``close_on_exec`` göstericisi
``close_on_exec_init`` elemanını ve ``open_fds`` göstericisi de ``open_fds_init`` elemanını göstermektedir.

``current`` göstericisinden hareketle ``fdx`` betimleyicisinin gösterdiği yerdeki dosya nesnesine
(``struct file``) ``current->files->fd[fdx]`` ifadesiyle erişilebilir. Bu erişimi kolaylaştırmak için 2.2 ve
2.4 çekirdeklerinde ``fcheck`` isimli çekirdek fonksiyonu bulundurulmuştur:

.. code-block:: c

   static inline struct file * fcheck(unsigned int fd)
   {
       struct file * file = NULL;
       struct files_struct *files = current->files;

       if (fd < files->max_fds)
           file = files->fd[fd];
       return file;
   }

Ancak bu fonksiyon export edilmemiştir. Yani aygıt sürücüler tarafından kullanılamamaktadır. Aslında çekirdekte
bir dosya betimleyicisinden hareketle dosya nesnesini elde etmek için daha yüksek seviyeli ``fget`` fonksiyonu
kullanılmaktadır. Bu fonksiyon 2.4 ve 2.6 versiyonlarında aşağıdaki gibi yazılmıştır:

.. code-block:: c

   struct file fastcall *fget(unsigned int fd)
   {
       struct file * file;
       struct files_struct *files = current->files;

       read_lock(&files->file_lock);
       file = fcheck(fd);
       if (file)
           get_file(file);
       read_unlock(&files->file_lock);
       return file;
   }

Bu fonksiyonun ``fcheck`` fonksiyonu kullanılarak yazıldığını görüyorsunuz. Ancak bu fonksiyon ileride
göreceğimiz gibi dosya nesnesi içerisindeki (``struct file`` yapısındaki) sayacı da güvenli bir biçimde
artırmaktadır. ``fget`` fonksiyonu da bu versiyonlarda export edilmemiştir.

Çekirdeğin 2.6 versiyonlarına gelindiğinde ``files_struct`` yapısının içerisi ``fdtable`` isimli bir yapı ile
biraz daha derli toplu fakat biraz daha karmaşık hale getirilmiştir. 2.6'lı versiyonlardaki ``files_struct``
yapısı şöyledir:

.. code-block:: c

   struct files_struct {
   /*
    * read mostly part
    */
       atomic_t count;
       struct fdtable __rcu *fdt;
       struct fdtable fdtab;
   /*
    * written part on a separate cache line in SMP
    */
       spinlock_t file_lock ____cacheline_aligned_in_smp;
       int next_fd;
       struct embedded_fd_set close_on_exec_init;
       struct embedded_fd_set open_fds_init;
       struct file __rcu * fd_array[NR_OPEN_DEFAULT];
   };

``fdtable`` yapısı da şöyledir:

.. code-block:: c

   struct fdtable {
       unsigned int max_fds;
       struct file __rcu **fd;      /* current fd array */
       fd_set *close_on_exec;
       fd_set *open_fds;
       struct rcu_head rcu;
       struct fdtable *next;
   };

Artık bu yapılar da ``include/linux/fdtable.h`` isimli dosya oluşturularak oraya taşınmıştır. Bu versiyonlarda
çekirdek her zaman ``fdt`` göstericisinin gösterdiği yerden işlemine başlamaktadır. ``fdt`` göstericisi işin
başında yapı içerisindeki ``fdtab`` yapı nesnesini göstermektedir. ``fdtab`` yapı nesnesinin içerisinde de
önceki versiyonlarda olduğu gibi ``fd``, ``close_on_exec``, ``open_fds`` göstericileri vardır. Bu göstericiler
de işin başında ``files_struct`` içerisindeki ``fd_array``, ``close_on_exec_init`` ve ``open_fds_init``
elemanlarını göstermektedir. Ancak ileride aslında ``files_struct`` içerisindeki ``fdt`` göstericisi başka bir
``fdtable`` nesnesini, ``fdtable`` nesnesinin içerisindeki göstericiler de büyütülmüş başka nesneleri gösterir
hale gelebilmektedir.

Bu versiyonlarda ``current`` göstericisinden hareketle ``fdx`` betimleyicisinin gösterdiği yerdeki dosya
nesnesine (``struct file``) ``current->files->fdt->fd[fdx]`` ifadesiyle erişilebilir. Bu versiyonlarda da bu
erişimi bazı kontrollerle sağlayan ayrı fonksiyonlar ve makrolar da bulundurulmuştur. Örneğin
``fcheck_files`` fonksiyonu şöyle tanımlanmıştır:

.. code-block:: c

   static inline struct file * fcheck_files(struct files_struct *files, unsigned int fd)
   {
       struct file * file = NULL;
       struct fdtable *fdt = files_fdtable(files);

       if (fd < fdt->max_fds)
           file = rcu_dereference_check_fdtable(files, fdt->fd[fd]);
       return file;
   }

   #define files_fdtable(files)    \
           (rcu_dereference_check_fdtable((files), (files)->fdt))

   #define fcheck(fd)  fcheck_files(current->files, fd)

Yani çekirdek içerisinde ``fcheck`` makrosuyla ``fd`` numaralı betimleyiciye ilişkin dosya nesnesi elde
edilebilmektedir. Ancak ``fcheck_files`` fonksiyonu da export edilmemiştir. Yine 2.6'lı çekirdeklerde de
dosya betimleyicisinden hareketle dosya nesnesi içerisindeki sayacı artırarak dosya nesnesini elde eden daha
yüksek seviyeli ``fget`` isimli bir fonksiyon da bulunmaktadır:

.. code-block:: c

   struct file *fget(unsigned int fd)
   {
       return __fget(fd, FMODE_PATH);
   }
   EXPORT_SYMBOL(fget);

Biz burada bu fonksiyonun çağırdığı fonksiyonları gözden geçirmeyeceğiz. Ancak bu fonksiyonun artık export
edildiğine dikkat ediniz. Yani bu versiyondan itibaren aygıt sürücüler de dosya betimleyicisinden hareketle
dosya nesnesine bu fonksiyon yoluyla erişebilmektedir. Çekirdekteki nesnenin sayacını artırarak erişim sağlayan
fonksiyonlar genel olarak ``get`` soneki ile, sayacı eksilten fonksiyonlar da ``put`` soneki ile
isimlendirilmiştir. ``fget`` fonksiyonuyla elde edilen dosya nesnesi ``fput`` fonksiyonuyla geri
bırakılmaktadır:

.. code-block:: c

   void fput(struct file *file)
   {
       if (atomic_long_dec_and_test(&file->f_count))
           __fput(file);
   }

Belli bir zamandan sonra artık bit dizisi oluşturmak için ``fd_set`` yapısının kullanılmasından vazgeçilmiştir.
Güncel çekirdeklerdeki açık dosyalara ilişkin veri yapısı 2.6 ile çok benzerdir. Ancak yukarıda da belirttiğimiz
gibi artık ``fd_set`` yapısı kullanılmamaktadır. Güncel çekirdeklerdeki ``files_struct`` yapısı şöyledir:

.. code-block:: c

   struct files_struct {
   /*
    * read mostly part
    */
       atomic_t count;
       bool resize_in_progress;
       wait_queue_head_t resize_wait;

       struct fdtable __rcu *fdt;
       struct fdtable fdtab;
   /*
    * written part on a separate cache line in SMP
    */
       spinlock_t file_lock ____cacheline_aligned_in_smp;
       unsigned int next_fd;
       unsigned long close_on_exec_init[1];
       unsigned long open_fds_init[1];
       unsigned long full_fds_bits_init[1];
       struct file __rcu * fd_array[NR_OPEN_DEFAULT];
   };

``fdtable`` yapısı da şöyledir:

.. code-block:: c

   struct fdtable {
       unsigned int max_fds;
       struct file __rcu **fd;      /* current fd array */
       unsigned long *close_on_exec;
       unsigned long *open_fds;
       unsigned long *full_fds_bits;
       struct rcu_head rcu;
   };

Görüldüğü gibi artık bit dizileri ``fd_set`` yerine doğrudan ``unsigned long`` türden bir dizi biçiminde
oluşturulmaktadır. Yine bu versiyonlarda da ``fdx`` numaralı dosya betimleyicisinin gösterdiği yerdeki dosya
nesnesine ``current->files->fdt->fd[fdx]`` ifadesiyle erişilmektedir. Fakat artık güncel versiyonlarda
``fcheck`` biçiminde bir makro ve ``fcheck_files`` isimli bir fonksiyon yoktur. Ancak yine güncel versiyonlarda
dosya betimleyicisi yoluyla dosya nesnesine erişimi referans sayacını artırarak yapan ``fget`` fonksiyonu
bulunmaktadır:

.. code-block:: c

   struct file *fget(unsigned int fd)
   {
       return __fget(fd, FMODE_PATH);
   }
   EXPORT_SYMBOL(fget);

Yine referans sayacını azaltarak nesneyi bırakmak için ``fput`` fonksiyonu kullanılmaktadır:

.. code-block:: c

   void fput(struct file *file)
   {
       if (unlikely(file_ref_put(&file->f_ref)))
           __fput_deferred(file);
   }
   EXPORT_SYMBOL(fput);

Güncel çekirdeklerde dosya betimleyici tablosundaki ilk boş betimleyicinin bulunmasının bit dizilerinde "ilk 0
olan bitin bulunması" problemi biçiminde ele alındığını belirtmiştik. Bunun için güncel çekirdeklerde iki düzey
bitmap kullanılıyordu. Güncel çekirdeklerdeki ``fdtable`` yapısının içerisinde bulunan ``open_fds`` birinci
düzey bitmap'i, ``full_fds_bits`` ise ikinci düzey bitmap'i belirtmektedir. Tüm dosya betimleyicilerinin dolu
mu boş mu olduğu ``open_fds`` bitmap'inde tutulmaktadır. ``full_fds_bits`` bitmap'i ise ``open_fds``
bitmap'indeki tüm bitleri 1 olan ilk ``unsigned long`` elemanın indeksinin bulunmasında kullanılmaktadır.
``files_struct`` ve ``fdtable`` yapılarını aşağıda yeniden veriyoruz:

.. code-block:: c

   struct files_struct {
   /*
    * read mostly part
    */
       atomic_t count;
       bool resize_in_progress;
       wait_queue_head_t resize_wait;

       struct fdtable __rcu *fdt;
       struct fdtable fdtab;
   /*
    * written part on a separate cache line in SMP
    */
       spinlock_t file_lock ____cacheline_aligned_in_smp;
       unsigned int next_fd;
       unsigned long close_on_exec_init[1];
       unsigned long open_fds_init[1];
       unsigned long full_fds_bits_init[1];
       struct file __rcu * fd_array[NR_OPEN_DEFAULT];
   };

   struct fdtable {
       unsigned int max_fds;
       struct file __rcu **fd;      /* current fd array */
       unsigned long *close_on_exec;
       unsigned long *open_fds;
       unsigned long *full_fds_bits;
       struct rcu_head rcu;
   };

Uzun süredir bir bit dizisi içerisindeki ilk 0 olan bitin indeksini elde etmek için ``find_next_zero_bit``
isimli bir çekirdek fonksiyonu kullanılmaktadır. Tabii bu fonksiyon nihayetinde yukarıda da bahsettiğimiz gibi
işlemciye özgü makine komutlarını kullanmaktadır. Çekirdeğin güncel versiyonlarında ``sys_open`` sistem
fonksiyonundan başlanarak ilk boş dosya betimleyicisinin bulunması için yapılan çağrılar şöyledir:

.. code-block:: text

   sys_open --> do_sys_open --> do_sys_openat2 --> __get_unused_fd_flags --> alloc_fd --> find_next_fd -->
   find_next_zero_bit

Bu çağrı zincirinde bir dizi içerisinde ilk 0 olan bitin bulunması işlemini ``find_next_zero_bit`` fonksiyonu
yapmaktadır. İlk 0 olan bitin bulunması aslında baştan başlanarak yapılmamaktadır. ``files_struct`` yapısı
içerisindeki ``next_fd`` elemanı aramanın başlatılacağı yeri belirtmektedir. Yani ``next_fd`` elemanının
belirttiği değerden küçük tüm dosya betimleyicileri doludur. Dolayısıyla arama ``full_fds_bits`` dizisinin
hemen başından başlatılmamaktadır. Tabii eğer ``next_fd`` elemanının belirttiği dosya betimleyicisinden daha
küçük bir betimleyici kapatılırsa çekirdek zaten bu ``next_fd`` elemanını güncellemektedir.

Güncel çekirdeklerdeki ``find_next_fd`` fonksiyonu şöyle yazılmıştır:

.. code-block:: c

   static unsigned int find_next_fd(struct fdtable *fdt, unsigned int start)
   {
       unsigned int maxfd = fdt->max_fds; /* always multiple of BITS_PER_LONG */
       unsigned int maxbit = maxfd / BITS_PER_LONG;
       unsigned int bitbit = start / BITS_PER_LONG;
       unsigned int bit;

       /*
        * Try to avoid looking at the second level bitmap
        */
       bit = find_next_zero_bit(&fdt->open_fds[bitbit], BITS_PER_LONG,
                   start & (BITS_PER_LONG - 1));
       if (bit < BITS_PER_LONG)
           return bit + bitbit * BITS_PER_LONG;

       bitbit = find_next_zero_bit(fdt->full_fds_bits, maxbit, bitbit) * BITS_PER_LONG;
       if (bitbit >= maxfd)
           return maxfd;
       if (bitbit > start)
           start = bitbit;
       return find_next_zero_bit(fdt->open_fds, maxfd, start);
   }

Fonksiyonun birinci parametresi ``fdtable`` nesnesinin adresini, ikinci parametresi ise aramanın başlatılacağı
betimleyicinin numarasını belirtmektedir. Fonksiyon önce ikinci düzey bitmap'te arama yapmadan birinci düzey
bitmap'te, dizinin hemen aramanın yapılacağı indeksinde hızlı bir arama yapar. Eğer bu aramadan sonuç elde
edilemezse önce ikinci düzey bitmap'te birinci düzey bitmap için dizi indeksini elde eder, sonra birinci düzey
bitmap'te arama yapar. ``find_next_zero_bit`` fonksiyonu da güncel çekirdeklerde şöyle tanımlanmıştır:

.. code-block:: c

   unsigned long find_next_zero_bit(const unsigned long *addr, unsigned long size,
                                    unsigned long offset)
   {
       if (small_const_nbits(size)) {
           unsigned long val;

           if (unlikely(offset >= size))
               return size;

           val = *addr | ~GENMASK(size - 1, offset);
           return val == ~0UL ? size : ffz(val);
       }

       return _find_next_zero_bit(addr, size, offset);
   }

Buradaki ``small_const_nbits`` fonksiyonu ``find_next_fd`` fonksiyonundaki ilk hızlı aramanın ve birinci düzey
bitmap'teki aramanın yapılabilmesi için kontrol sağlamaktadır. Yani arama tek bir dizi elemanı üzerinde
yapılacaksa bu ``if`` deyiminin doğru olduğu kısım çalıştırılacaktır. Eğer arama birden fazla dizi elemanı
üzerinde yapılacaksa bu durumda arama ``_find_next_zero_bit`` fonksiyonuna yaptırılmaktadır. Bu fonksiyon da
şöyle tanımlanmıştır:

.. code-block:: c

   unsigned long _find_next_zero_bit(const unsigned long *addr, unsigned long nbits,
                                     unsigned long start)
   {
       return FIND_NEXT_BIT(~addr[idx], /* nop */, nbits, start);
   }

   #define FIND_NEXT_BIT(FETCH, MUNGE, size, start)                             
   ({                                                                           \
       unsigned long mask, idx, tmp, sz = (size), __start = (start);            \
                                                                                \
       if (unlikely(__start >= sz))                                             \
           goto out;                                                            \
                                                                                \
       mask = MUNGE(BITMAP_FIRST_WORD_MASK(__start));                           \
       idx = __start / BITS_PER_LONG;                                           \
                                                                                \
       for (tmp = (FETCH) & mask; !tmp; tmp = (FETCH)) {                        \
           if ((idx + 1) * BITS_PER_LONG >= sz)                                 \
               goto out;                                                        \
           idx++;                                                               \
       }                                                                        \
                                                                                \
       sz = min(idx * BITS_PER_LONG + __ffs(MUNGE(tmp)), sz);                   \
   out:                                                                         \
       sz;                                                                      \
   })

Burada dizi elemanlarında arama ``FIND_NEXT_BIT`` makrosuyla yapılmıştır. Tabii bu makro içerisindeki döngü
ancak birinci düzey bitmap aramasında çalıştırılacaktır.

Burada şöyle bir özet yapmak istiyoruz:

1. Çekirdek hemen ikinci düzey bitmap'e (``full_fds_bits``) yönelmez. Önce ``open_fds`` dizisinde tek bir
   ``unsigned long`` elemanda hızlı bir arama yapar.

2. Eğer yukarıdaki arama başarısız olursa bu durumda önce ikinci düzey bitmap'te (``full_fds_bits``) ilk 0
   olan bitin indeksi elde edilir. Birinci düzey bitmap'te (``open_fds``) yalnızca bu indeksteki
   ``unsigned long`` dizi elemanında arama yapılır.

3. ``find_next_zero_bit`` fonksiyonu ``unsigned long`` dizisinin yalnızca tek bir elemanında mı yoksa belli
   bir elemandan itibaren dizinin geri kalan tüm elemanlarında mı arama yapılacağına ``small_const_nbits``
   çağrısıyla karar vermektedir.

Peki yukarıdaki kodlarda bitmap dizisinin belli bir ``unsigned long`` elemanında işlemcinin özel makine
komutlarıyla arama işlemi tam nerede yapılmaktadır? İşte yukarıdaki kodlar incelenirse makine dili düzeyinde
aramanın ``ffz`` fonksiyonunda ve ``__ffs`` fonksiyonunda yapıldığı görülecektir.

Thread'ler, Fork ve Dosya Betimleyicileri
------------------------------------------

POSIX sistemlerinde dolayısıyla da Linux çekirdeğinde thread'lerin ayrı dosya betimleyici
tabloları yoktur. Dosya betimleyicileri ve dosya betimleyici tablosu prosese özgüdür. Bir thread
yaratıldığında thread'e ilişkin ``task_struct`` nesnesinin ``fs`` ve ``files`` gibi elemanları,
onu yaratan thread'in ``task_struct`` nesnesinden sığ kopyalamayla kopyalanmaktadır. Dolayısıyla
aslında prosesin bütün thread'leri açık dosyalara ilişkin aynı veri yapısı nesnelerini
kullanmaktadır:

.. code-block:: c

   struct task_struct {
       /* ... */

       /* Filesystem information: */
       struct fs_struct        *fs;

       /* Open file information: */
       struct files_struct     *files;

       /* ... */
   };

Yeni ``task_struct`` nesnesi yaratılıp diğer ``task_struct`` nesnesinden sığ kopyalama
yapıldığında ``files`` göstericisinin de aslında aynı ``files_struct`` nesnesini göstereceğine
dikkat ediniz. Yani toplamda aslında proses için tek bir ``files_struct`` nesnesi bulunmaktadır.

``fork`` işlemi sırasında ise tamamen alt proses için yeni bir ``files_struct`` nesnesi ve yeni
bir dosya betimleyici tablosu (fd dizisi) yaratılmaktadır. Ancak üst prosesin dosya betimleyici
tablosundaki adresler yeni yaratılan alt prosesteki dosya betimleyici tablosuna kopyalanmaktadır.
Böylece üst prosesin dosya betimleyici tablosunun aynı numaralı betimleyicileriyle alt prosesin
dosya betimleyici tablosunun aynı numaralı betimleyicileri aynı dosya nesnelerini gösteriyor
durumda olur. Tabii artık üst ve alt proseslerin yeni açacağı dosyalar onlara özgü olacaktır.
Paylaşılan dosya nesneleri yalnızca ``fork`` öncesinde açılmış olanlardır.


Dosya Sistemi Temel Nesneleri
------------------------------

Şimdiye kadar açık dosyalara ilişkin çekirdeğin oluşturduğu veri yapıları hakkında şu bilgileri
edindik:

- Açık dosyalara ilişkin ``task_struct`` içerisindeki veri yapıları.
- Dosya betimleyicilerinin anlamı ve dosya betimleyicisi yoluyla dosya nesnelerine nasıl
  erişildiği.
- En düşük boş betimleyicinin elde edilme biçimi.

Şimdi dosya sisteminin diğer önemli veri yapıları üzerinde duracağız.


Dosya Nesnesi, inode Nesnesi ve dentry Nesnesi
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Çekirdek açık bir dosya üzerinde read/write gibi işlemleri yaparken dosyanın son okunma tarihi,
son güncelleme tarihi, dosya uzunluğu gibi bilgileri de güncelleyeceğine göre bu bilgilere nasıl
erişmektedir? Dosyaların uzunluk, erişim hakları, tarih-zaman bilgisi gibi metadata bilgileri
diskte tutulmaktadır. (Ext dosya sistemlerinde bu bilgilerin diskte tutulduğu yere inode blok
denilmektedir.) Çekirdek dosya açılırken dosyanın bu metadata bilgilerini diskten okuyarak
bellekte ``inode`` isimli bir yapı nesnesinin içerisine yerleştirmektedir. Biz dosyaların
metadata bilgilerinin tutulduğu bu *inode nesnesi* türünden nesnelere *inode nesnesi* de
diyeceğiz.

Peki bir dosya açıldığında dosyanın dosya sistemindeki yeri çekirdek tarafından nasıl
saklanmaktadır? Çekirdek her dosya açıldığında o dosyanın dizin girişi bilgilerini (yani dosya
sisteminde nerede olduğu bilgisini ve bazı diğer bilgileri) ismine *dentry* denilen bir yapı
nesnesine yerleştirmektedir.

Dosya sistemi nesnelerini şöyle özetleyebiliriz:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Nesne
     - Açıklama
   * - **Dosya Nesnesi** (``struct file``)
     - Açılmış dosyalar üzerinde işlem yapmak için gereken tüm bilgilerin tutulduğu nesne.
   * - **inode Nesnesi** (``struct inode``)
     - Dosyanın diskteki metadata bilgilerini tutan nesne.
   * - **dentry Nesnesi** (``struct dentry``)
     - Dosyanın dosya sistemi üzerindeki yerini ve buna ilişkin bazı bilgileri tutan nesne.


Nesneler Arası İlişki
~~~~~~~~~~~~~~~~~~~~~~

Uzunca bir süre (2.6'ya kadar ve 2.6'lı versiyonlar da dahil olmak üzere) dosya nesnesinin
(``file`` yapısının) içerisinde dentry nesnesinin adresi, dentry nesnesinin içerisinde de o dizin
girişinin inode nesnesinin adresi tutuluyordu. Daha sonraları dosya nesnesinin içerisinde de
doğrudan inode nesnesinin adresi tutulmaya başlanmıştır:

.. graphviz::

   digraph file_objects {
       rankdir=LR;
       node [shape=box, style="rounded,filled", fillcolor="#D6E8FA",
             fontname="DejaVu Sans", margin="0.3,0.2"];
       edge [color="#444444", fontname="DejaVu Sans", fontsize=9];

       file   [label="struct file\n(Dosya Nesnesi)", fillcolor="#FFF3CD"];
       dentry [label="struct dentry\n(dentry Nesnesi)", fillcolor="#D6E8FA"];
       inode  [label="struct inode\n(inode Nesnesi)",  fillcolor="#D5F5D5"];

       file   -> dentry [label="f_path.dentry"];
       dentry -> inode  [label="d_inode"];
       file   -> inode  [label="f_inode (doğrudan erişim)", style=dashed];
   }

UNIX/Linux sistemlerinde bir dosya sistemi kök dizinde bir yere mount edilebilmektedir. Çekirdeğin
bazı durumlarda bir dosyanın hangi dosya sisteminin içerisinde bulunduğunu anlaması da
gerekebilmektedir. 2.6 çekirdeklerinden itibaren de dosyanın dentry nesnesinin adresiyle
vfsmount bilgileri ``path`` isimli bir yapıya yerleştirilmiş ve ``file`` yapısının içerisindeki
``f_path`` elemanında tutulmaya başlanmıştır:

.. code-block:: c

   struct file {
       /* ... */

       fmode_t             f_mode;
       unsigned int        f_flags;
       loff_t              f_pos;
       atomic_long_t       f_count;    /* güncel çekirdeklerde: file_ref_t f_ref */
       struct path         f_path;
       struct inode       *f_inode;

       /* ... */
   };

   struct path {
       struct vfsmount *mnt;
       struct dentry *dentry;
   } __randomize_layout;


Dosya Nesnesi Elemanları
~~~~~~~~~~~~~~~~~~~~~~~~~

Açık bir dosyanın ``open`` POSIX fonksiyonunda kullanılan açış bayrakları (``O_`` ile başlayan
bayraklar) ``file`` yapısının ``f_flags`` elemanında saklanmaktadır. Örneğin:

.. code-block:: c

   fd = open("test.txt", O_RDWR|O_APPEND);

Buradaki ``O_RDWR`` ve ``O_APPEND`` bayrakları ``file`` yapısının ``f_flags`` elemanında
saklanmaktadır. Bu ``f_flags`` elemanının daha çabuk işleme sokulabilecek yeniden düzenlenmiş
hali yapının ``f_mode`` elemanında saklanmaktadır.

Okuma yazma işlemlerinin *dosya göstericisi (file pointer)* denilen bir offset'ten itibaren
yapıldığını anımsayınız. Dosya göstericisinin konumu da ``file`` yapısının ``f_pos`` elemanında
tutulmaktadır.

Dosya nesnelerini birden fazla betimleyici gösterebilmektedir. Örneğin ``dup`` ve ``dup2`` POSIX
fonksiyonları aynı dosya nesnesini gösteren farklı bir betimleyicinin oluşturulmasına yol
açmaktadır. Bu durumda ``close`` fonksiyonu ile dosya kapatıldığında dosya hemen silinmez. Çünkü
onu kullanan başka betimleyiciler de bulunuyor olabilir. İşte ``file`` yapısının içerisindeki
referans sayacı (uzun süre ``f_count``, güncel çekirdeklerde ``f_ref`` ismiyle) o dosya
nesnesinin kaç betimleyici tarafından gösterildiği bilgisini tutmaktadır. Her betimleyici
``close`` fonksiyonu ile kapatıldığında bu sayaç 1 eksiltilir; sayaç 0'a düştüğünde dosya nesnesi
silinir.


inode ve dentry Önbellekleri
-----------------------------

Her açılan yeni dosya için çekirdek yeni bir dosya nesnesi yaratmaktadır. Ancak aynı dosyalar
açıldığında bu dosyalar için tek bir dentry ve inode nesnesi oluşturmaktadır. Bunun için ``open``
fonksiyonuyla bir dosya açıldığında çekirdeğin bu dosyaya ilişkin dentry nesnesi ve inode nesnesi
daha önce yaratılmış mı diye bir araştırma yapması gerekmektedir.

İşte çekirdek dentry ve inode nesneleri için ayrı önbellek (cache) sistemleri oluşturmaktadır.
Bunlara Linux sistemlerinde *dentry önbelleği (dentry cache)* ve *inode önbelleği (inode cache)*
denilmektedir. Bir dosya açıldığında çekirdek o dosyaya ilişkin dentry ve inode nesneleri zaten
bu önbellek sistemlerinde varsa hiç diske gitmeden doğrudan bu önbelleklerden onları alıp
kullanmaktadır.

Bir dosyayı onu açmış olan bütün prosesler kapatmış olsa bile o dosyaya ilişkin dentry ve inode
nesneleri bu önbellek sistemlerinde kalmaya devam edebilir. Çünkü dosyalar (özellikle bazı
merkezi dosyalar) farklı prosesler tarafından defalarca açılıp kullanılabilmektedir. (Örneğin
``/etc/passwd`` dosyası pek çok proses tarafından dolaylı bir biçimde açılıp kullanılabilmektedir.)
Bu tür durumlarda onların bu önbellekler içerisinde biriktirilmesi sistem performansını oldukça
iyileştirmektedir.

Linux'taki bu tür önbellek sistemlerinde önbellekten çıkarma için genel olarak *LRU (Least
Recently Used)* denilen *önbellek yer değiştirme (cache replacement) algoritması* işletilmektedir.
Yani önbellekten toplamda en az kullanılanlar değil son zamanlarda en az kullanılanlar
çıkartılmaktadır.

Bu noktada *dentry önbelleği* ve *inode önbelleği* ile *sayfa önbelleği (page cache)* arasındaki
ilişkiye de değinelim. Sayfa önbelleği disk blokları temelinde organize edilen ve her türlü disk
bloğunun transfer edilmesinde kullanılan aşağı seviyeli bir önbellek sistemidir. Halbuki dentry
ve inode önbellekleri yalnızca dentry ve inode elemanlarından oluşan önbelleklerdir. Bir dosya
açıldığında eğer o dosyaya ilişkin dentry ve inode nesneleri dentry ve inode önbelleklerinde
yoksa diskten elde edilmektedir. Tabii bu amaçla disk okuması yapılmadan önce bu disk bloklarının
sayfa önbelleğinde olup olmadığına da bakılmaktadır.


open() Fonksiyonunun İşleyişi
-------------------------------

Geldiğimiz noktaya kadarki konuları dikkate aldığımızda ``open`` fonksiyonuyla bir dosyanın
açılması durumunda sırasıyla şunların yapıldığını söyleyebiliriz:

1. Prosesin dosya betimleyici tablosunda boş bir betimleyici hızlı bir biçimde bulunur.
2. Bir dosya nesnesi (``struct file`` nesnesi) yaratılır ve elemanlarına gerekli ilkdeğerler
   verilir.
3. Dosyaya ilişkin dentry nesnesi ve inode nesnesi dentry önbelleğinde ve inode önbelleğinde
   yoksa diskte arama yapılarak yaratılır ve bunların adresleri dosya nesnesine yerleştirilir.
4. Dosya nesnesinin adresi dosya betimleyici tablosuna (fd dizisine) yerleştirilir ve yerleştirilen
   dizi indeksi dosya betimleyicisi olarak geri döndürülür.


Prosesin Kök ve Çalışma Dizini
--------------------------------

Bir prosesin kök dizininin ve çalışma dizininin proses kontrol bloğunda yani ``task_struct``
nesnesinde tutulduğunu belirtmiştik. Güncel çekirdeklerde bu bilgi şöyle tutulmaktadır:

.. code-block:: c

   struct task_struct {
       /* ... */

       struct fs_struct *fs;

       /* ... */
   };

   struct fs_struct {
       /* ... */
       struct path root, pwd;

       /* ... */
   } __randomize_layout;

   struct path {
       struct vfsmount *mnt;
       struct dentry *dentry;
   } __randomize_layout;

Görüldüğü gibi çekirdek prosesin kök dizinin ve çalışma dizininin bilgisini yol ifadesi biçiminde
değil dentry nesnesi biçiminde tutmaktadır.


Dosya Sistemi Veri Yapılarına İlişkin Testler
----------------------------------------------

Şimdi dosya sisteminin temel veri yapıları üzerinde görmüş olduğumuz konulara ilişkin bazı
testler yapalım. Bu testleri yapmak için bir aygıt sürücü yazarak ioctl yoluyla gerçekleştireceğiz.
(Kursumuzda kullandığımız Linux makinedeki çekirdek sürümü 6.9.2'dir.)


ioctl_test1 ve ioctl_test2: Dosya Göstericisini Okuma
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

İlk örneğimizde bir dosya betimleyicisine ilişkin dosya nesnesini elde ederek onun ``f_pos``
elemanını yazdırmaya çalışalım. Dosya nesnesindeki ``f_pos`` elemanının dosya göstericisinin
değerini tuttuğunu anımsayınız.

**Düşük seviyeli erişim (ioctl_test1):**

.. code-block:: c

   static long ioctl_test1(struct file *filp, unsigned long arg)
   {
       struct file *f;
       int fd = (int) arg;

       if (fd < 0 || fd >= current->files->fdt->max_fds) {
           printk(KERN_INFO "file descriptor is not valid!..\n");
           return -EBADF;
       }

       f = current->files->fdt->fd[fd];
       if (f == NULL) {
           printk(KERN_INFO "file descriptor is not valid!..\n");
           return -EBADF;
       }

       printk(KERN_INFO "File pointer offset: %lld\n", (long long)f->f_pos);

       return 0;
   }

Burada dosya betimleyicisinden hareketle dosya nesnesine ``current->files->fdt->fd[fd]`` ifadesiyle
erişilmiştir. Ancak bu erişim aslında güvenli değildir. Çünkü tam bu erişim yapılırken dosya
betimleyici tablosu büyütülürse ya da bu betimleyici üzerinde işlem yapılırsa kodumuz kararsız
bir durumla karşı karşıya kalır. Genel olarak çekirdeğin uyguladığı senkronizasyon mekanizmasına
uygun hareket etmek gerekir.

Çekirdek nesneleri üzerinde işlem yapacak kişi nesnenin referans sayacını artırmazsa çekirdek onu
boşaltabilir. Linux çekirdeklerinde sayacı artırarak nesneyi elde eden fonksiyonlar *get* soneki
ile, sayacı azaltarak nesneyi bırakan fonksiyonlar ise *put* soneki ile isimlendirilmiştir.

**fget/fput kullanımı (ioctl_test2):**

Yukarıdaki testi daha güvenli bir biçimde ``fget`` ve ``fput`` fonksiyonlarını kullanarak da
yapabiliriz:

.. code-block:: c

   static long ioctl_test2(struct file *filp, unsigned long arg)
   {
       struct file *f;
       int fd = (int) arg;

       if ((f = fget(fd)) == NULL) {
           printk(KERN_INFO "file descriptor is not valid!..\n");
           return -EBADF;
       }

       printk(KERN_INFO "File pointer offset: %ld\n", (long)f->f_pos);

       fput(f);

       return 0;
   }

``fget`` isimli yüksek seviyeli çekirdek fonksiyonu dosya betimleyicisinden hareketle bize dosya
nesnesini RCU mekanizmasını kullanarak dosya nesnesinin sayacını da artırarak vermektedir. ``fput``
fonksiyonu da sayacı azaltarak dosya nesnesini geri bırakmaktadır. Bu fonksiyonların prototipleri:

.. code-block:: c

   struct file *fget(unsigned int fd);
   void fput(struct file *);

Bu fonksiyonların prototipleri ``include/linux/file.h`` dosyası içerisindedir. Güncel çekirdeklerde
``fget`` fonksiyonunun tanımlaması ``fs/file.c`` dosyası içerisinde, ``fput`` fonksiyonunun
tanımlaması ise ``fs/file_table.c`` içerisinde yapılmıştır. ``fget`` ve ``fput`` fonksiyonları
export edildiği için aygıt sürücüler içerisinde de kullanılabilmektedir.

Güncel çekirdeklere ``fget`` ve ``fput`` işlemlerini daha etkin gerçekleştirmek için ``fdget`` ve
``fdput`` isimli fonksiyonlar da eklenmiştir. Her ne kadar yeni çekirdeklerde ``fdget`` ve
``fdput`` daha hızlı çalışıyorsa da ``fget`` ve ``fput`` basit arayüzü ve kullanım kolaylığı
nedeniyle tercih edilebilir.


dup Gerçekleştirimi: ioctl_test3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Şimdi de ``dup`` POSIX fonksiyonunun işlevini yerine getiren (yani ``sys_dup`` sistem fonksiyonu
gibi çalışan) bir fonksiyonu kendimiz yazalım. Bunun için bir ioctl kodu oluşturabiliriz. Bu ioctl
kodu kullanıcı modundan çağrılırken ``ioctl`` fonksiyonunun üçüncü parametresine aşağıdaki gibi
bir yapı nesnesinin adresini geçebiliriz:

.. code-block:: c

   struct FDDUP {
       int fd;
       int fd_dup;
   };

Burada yapının ``fd`` elemanı çiftlenecek dosya betimleyicisini belirtmektedir. ``fd_dup``
elemanı ise çiftleme sonucunda elde edilecek yeni betimleyiciyi belirtmektedir. Bu elemanların
``dup`` fonksiyonu ile ilişkisini şöyle temsil edebiliriz:

.. code-block:: c

   fd_dup = dup(fd);

Dosya betimleyicisini çiftleyen ioctl kodu test amaçlı olarak şöyle yazılabilir:

.. code-block:: c

   static long ioctl_test3(struct file *filp, unsigned long arg)
   {
       struct file *f;
       struct fdtable *fdt;
       struct file **fd_table;
       struct FDDUP fddup;
       int i;

       f = NULL;

       if (copy_from_user(&fddup, (struct FDDUP *)arg, sizeof(fddup)) != 0)
           return -EFAULT;

       fdt = current->files->fdt;
       fd_table = fdt->fd;

       if (fddup.fd < 0 || fddup.fd >= fdt->max_fds)
           return -EBADF;
       if (fd_table[fddup.fd] == NULL)
           return -EBADF;

       for (i = 0; i < fdt->max_fds; ++i)
           if (fd_table[i] == NULL) {
               f = fd_table[fddup.fd];
               fd_table[i] = f;
               ++f->f_count.counter;     /* atomic_long_inc(&f->f_count); */
               fddup.fd_dup = i;
               break;
           }
       if (f == NULL)
           return -EMFILE;

       if (copy_to_user((struct FDDUP *)arg, &fddup, sizeof(fddup)) != 0)
           return -EFAULT;

       return 0;
   }

Kursumuzun yapıldığı 6.9.2 çekirdeğinde dosya nesnesinin sayacının ``file`` yapısının içerisinde
şöyle tutulduğunu anımsatalım:

.. code-block:: c

   struct file {
       /* ... */

       atomic_long_t       f_count;

       /* ... */
   };

Burada ``atomic_long_t`` türü bir yapı biçiminde bildirilmiştir:

.. code-block:: c

   typedef struct {
       long counter;
   } atomic_long_t;

Bu ``atomic_long_t`` türüyle belirtilen değerler üzerinde işlemler atomik düzeyde özel
fonksiyonlarla yapılmaktadır. Bu konuyla ilgili önemli birkaç fonksiyon:

.. code-block:: c

   void atomic_long_set(atomic_long_t *v, long i);
   long atomic_long_read(const atomic_long_t *v);
   void atomic_long_inc(atomic_long_t *v);
   void atomic_long_dec(atomic_long_t *v);

``atomic_t`` ve ``atomic_long_t`` türleri hakkında ayrıntıları başka bir başlıkta ele alacağız.

Fonksiyonumuzdaki döngüde aslında mantıksal bir kusur da vardır. Biz döngüde yalnızca o andaki
dosya betimleyici tablosunda arama yaptık. Halbuki çekirdek aslında başlangıçta küçük bir dosya
betimleyici tablosunu tutarken daha sonra bunu gerektiğinde proses limitinin izin verdiği kadar
yükseltebilmektedir.


Yüksek Seviyeli Fonksiyonlarla dup: ioctl_test4
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Testi yaptığımız makinedeki Linux çekirdeğinde anımsayacağınız gibi ilk boş betimleyiciyi hızlı
bir biçimde bulabilmek için iki düzey bitmap kullanılıyordu. Bu versiyonlarda ilk boş
betimleyiciyi bulan ``get_unused_fd_flags`` isimli yüksek seviyeli bir çekirdek fonksiyonu
bulunmaktadır. Bu fonksiyon export edildiği için aygıt sürücülerden de kullanılabilmektedir:

.. code-block:: c

   int get_unused_fd_flags(unsigned flags)
   {
       return __get_unused_fd_flags(flags, rlimit(RLIMIT_NOFILE));
   }
   EXPORT_SYMBOL(get_unused_fd_flags);

``get_unused_fd_flags`` fonksiyonu aynı zamanda gerektiğinde dosya betimleyici tablosunu büyütme
işlemini de kendisi yapmaktadır. ``flags`` parametresi ya ``O_CLOEXEC`` biçiminde ya da ``0``
biçiminde geçilebilmektedir.

Ayrıca RCU mekanizması eşliğinde dosya nesnesini (``struct file`` nesnesini) dosya betimleyici
tablosuna yerleştiren export edilmiş ``fd_install`` isimli yüksek seviyeli bir çekirdek fonksiyonu
da bulunmaktadır:

.. code-block:: c

   void fd_install(unsigned int fd, struct file *file);

Böylece yukarıdaki fonksiyonu şu hale getirebiliriz:

.. code-block:: c

   static long ioctl_test4(struct file *filp, unsigned long arg)
   {
       struct file *f;
       struct FDDUP fddup;

       if (copy_from_user(&fddup, (struct FDDUP *)arg, sizeof(fddup)) != 0)
           return -EFAULT;

       if ((f = fget(fddup.fd)) == NULL)
           return -EBADF;

       if ((fddup.fd_dup = get_unused_fd_flags(0)) < 0) {
           fput(f);
           return fddup.fd_dup;
       }

       if (copy_to_user((struct FDDUP *)arg, &fddup, sizeof(fddup)) != 0) {
           fput(f);
           return -EFAULT;
       }

       fd_install(fddup.fd_dup, f);

       return 0;
   }


Tam Sürücü Kodu
~~~~~~~~~~~~~~~~

Yukarıdaki test işlemlerine ilişkin tam aygıt sürücü kodu aşağıda verilmiştir.

**test-driver.h**

.. code-block:: c

   #ifndef TEST_DRIVER_H_
   #define TEST_DRIVER_H_

   #include <linux/stddef.h>
   #include <linux/ioctl.h>

   struct FDDUP {
       int fd;
       int fd_dup;
   };

   #define TEST_DRIVER_MAGIC       't'
   #define IOC_TEST1               _IOR(TEST_DRIVER_MAGIC, 0, int)
   #define IOC_TEST2               _IOR(TEST_DRIVER_MAGIC, 1, int)
   #define IOC_TEST3               _IOWR(TEST_DRIVER_MAGIC, struct FDDUP)
   #define IOC_TEST4               _IOWR(TEST_DRIVER_MAGIC, 3, struct FDDUP)

   #endif

**test-driver.c**

.. code-block:: c

   #include <linux/module.h>
   #include <linux/kernel.h>
   #include <linux/fs.h>
   #include <linux/cdev.h>
   #include <linux/fdtable.h>
   #include <linux/file.h>
   #include "test-driver.h"

   MODULE_LICENSE("GPL");
   MODULE_AUTHOR("Kaan Aslan");
   MODULE_DESCRIPTION("test-driver");

   static int test_driver_open(struct inode *inodep, struct file *filp);
   static int test_driver_release(struct inode *inodep, struct file *filp);
   static ssize_t test_driver_read(struct file *filp, char *buf, size_t size, loff_t *off);
   static ssize_t test_driver_write(struct file *filp, const char *buf, size_t size, loff_t *off);
   static long test_driver_ioctl(struct file *filp, unsigned int cmd, unsigned long arg);

   static long ioctl_test1(struct file *filp, unsigned long arg);
   static long ioctl_test2(struct file *filp, unsigned long arg);
   static long ioctl_test3(struct file *filp, unsigned long arg);
   static long ioctl_test4(struct file *filp, unsigned long arg);

   static dev_t g_dev;
   static struct cdev g_cdev;
   static struct file_operations g_fops = {
       .owner          = THIS_MODULE,
       .open           = test_driver_open,
       .read           = test_driver_read,
       .write          = test_driver_write,
       .release        = test_driver_release,
       .unlocked_ioctl = test_driver_ioctl
   };

   static int __init test_driver_init(void)
   {
       int result;

       printk(KERN_INFO "test-driver module initialization...\n");

       if ((result = alloc_chrdev_region(&g_dev, 0, 1, "test-driver")) < 0) {
           printk(KERN_INFO "cannot alloc char driver!...\n");
           return result;
       }
       cdev_init(&g_cdev, &g_fops);
       if ((result = cdev_add(&g_cdev, g_dev, 1)) < 0) {
           unregister_chrdev_region(g_dev, 1);
           printk(KERN_ERR "cannot add device!...\n");
           return result;
       }

       return 0;
   }

   static void __exit test_driver_exit(void)
   {
       cdev_del(&g_cdev);
       unregister_chrdev_region(g_dev, 1);

       printk(KERN_INFO "test-driver module exit...\n");
   }

   static int test_driver_open(struct inode *inodep, struct file *filp)
   {
       printk(KERN_INFO "test-driver opened...\n");
       return 0;
   }

   static int test_driver_release(struct inode *inodep, struct file *filp)
   {
       printk(KERN_INFO "test-driver closed...\n");
       return 0;
   }

   static ssize_t test_driver_read(struct file *filp, char *buf, size_t size, loff_t *off)
   {
       printk(KERN_INFO "test-driver read...\n");
       return 0;
   }

   static ssize_t test_driver_write(struct file *filp, const char *buf, size_t size, loff_t *off)
   {
       printk(KERN_INFO "test-driver write...\n");
       return 0;
   }

   static long test_driver_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)
   {
       long result;

       printk(KERN_INFO "test_driver_ioctl...\n");

       switch (cmd) {
           case IOC_TEST1:
               result = ioctl_test1(filp, arg);
               break;
           case IOC_TEST2:
               result = ioctl_test2(filp, arg);
               break;
           case IOC_TEST3:
               result = ioctl_test3(filp, arg);
               break;
           case IOC_TEST4:
               result = ioctl_test4(filp, arg);
               break;
           default:
               result = -ENOTTY;
       }

       return result;
   }

   static long ioctl_test1(struct file *filp, unsigned long arg)
   {
       struct file *f;
       int fd = (int)arg;

       if (fd < 0 || fd >= current->files->fdt->max_fds) {
           printk(KERN_INFO "file descriptor is not valid!..\n");
           return -EBADF;
       }

       f = current->files->fdt->fd[fd];
       if (f == NULL) {
           printk(KERN_INFO "file descriptor is not valid!..\n");
           return -EBADF;
       }

       printk(KERN_INFO "File pointer offset: %ld\n", (long)f->f_pos);
       return 0;
   }

   static long ioctl_test2(struct file *filp, unsigned long arg)
   {
       struct file *f;
       int fd = (int)arg;

       if ((f = fget(fd)) == NULL) {
           printk(KERN_INFO "file descriptor is not valid!..\n");
           return -EBADF;
       }

       printk(KERN_INFO "File pointer offset: %ld\n", (long)f->f_pos);
       fput(f);
       return 0;
   }

   static long ioctl_test3(struct file *filp, unsigned long arg)
   {
       struct file *f;
       struct fdtable *fdt;
       struct file **fd_table;
       struct FDDUP fddup;
       int i;

       f = NULL;

       if (copy_from_user(&fddup, (struct FDDUP *)arg, sizeof(fddup)) != 0)
           return -EFAULT;

       fdt = current->files->fdt;
       fd_table = fdt->fd;

       if (fddup.fd < 0 || fddup.fd >= fdt->max_fds)
           return -EBADF;
       if (fd_table[fddup.fd] == NULL)
           return -EBADF;

       for (i = 0; i < fdt->max_fds; ++i)
           if (fd_table[i] == NULL) {
               f = fd_table[fddup.fd];
               fd_table[i] = f;
               ++f->f_count.counter;     /* atomic_long_inc(&f->f_count); */
               fddup.fd_dup = i;
               break;
           }
       if (f == NULL)
           return -EMFILE;

       if (copy_to_user((struct FDDUP *)arg, &fddup, sizeof(fddup)) != 0)
           return -EFAULT;

       return 0;
   }

   static long ioctl_test4(struct file *filp, unsigned long arg)
   {
       struct file *f;
       struct FDDUP fddup;

       if (copy_from_user(&fddup, (struct FDDUP *)arg, sizeof(fddup)) != 0)
           return -EFAULT;

       if ((f = fget(fddup.fd)) == NULL)
           return -EBADF;

       if ((fddup.fd_dup = get_unused_fd_flags(0)) < 0) {
           fput(f);
           return fddup.fd_dup;
       }

       if (copy_to_user((struct FDDUP *)arg, &fddup, sizeof(fddup)) != 0) {
           fput(f);
           return -EFAULT;
       }

       fd_install(fddup.fd_dup, f);

       return 0;
   }

   module_init(test_driver_init);
   module_exit(test_driver_exit);

**Makefile**

.. code-block:: makefile

   obj-m += ${file}.o

   all:
   	make -C /lib/modules/$(shell uname -r)/build M=${PWD} modules
   clean:
   	make -C /lib/modules/$(shell uname -r)/build M=${PWD} clean

**load** (yükleyici betik)

.. code-block:: bash

   #!/bin/bash

   module=$1
   mode=666

   /sbin/insmod ./${module}.ko ${@:2} || exit 1
   major=$(awk "\$2 == \"$module\" {print \$1}" /proc/devices)
   rm -f $module
   mknod -m $mode $module c $major 0

**unload** (kaldırıcı betik)

.. code-block:: bash

   #!/bin/bash

   module=$1

   /sbin/rmmod ./${module}.ko || exit 1
   rm -f $module

**app.c** (test uygulaması)

.. code-block:: c

   #include <stdio.h>
   #include <stdlib.h>
   #include <stdint.h>
   #include <fcntl.h>
   #include <unistd.h>
   #include <sys/ioctl.h>
   #include "test-driver.h"

   void exit_sys(const char *msg);

   int main(int argc, char *argv[])
   {
       int fd_dev;
       int fd;
       struct FDDUP fddup;
       off_t pos;

       if (argc != 2) {
           fprintf(stderr, "wrong number of arguments!..\n");
           exit(EXIT_FAILURE);
       }

       if ((fd_dev = open("test-driver", O_RDONLY)) == -1)
           exit_sys("open");

       if ((fd = open(argv[1], O_RDONLY)) == -1)
           exit_sys("open");
       lseek(fd, 100, 0);

       fddup.fd = fd;
       if (ioctl(fd_dev, IOC_TEST4, &fddup) == -1)
           exit_sys("ioctl");

       pos = lseek(fddup.fd_dup, 0, 1);
       printf("%jd\n", (intmax_t)pos);

       close(fd);
       close(fddup.fd);
       close(fd_dev);

       return 0;
   }

   void exit_sys(const char *msg)
   {
       perror(msg);
       exit(EXIT_FAILURE);
   }

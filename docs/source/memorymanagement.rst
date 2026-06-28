===========================
Bellek Yönetimi - I. Bölüm
===========================

Bu bölümde Linux çekirdeklerinin *bellek yönetimi (memory management)* alt sistemini inceleyeceğiz.
Bellek yönetimi modern işletim sistemlerinde oldukça karmaşık ve ayrıntılı bir konudur. Dolayısıyla
bu bölüm kitabımızda önemli bir yr kaplayacaktır. Bu nedenle biz konuyu iki bölüme ayırıp ele almayı 
uygun gördük. 

Modern işletim sistemlerinin bellek yönetimlerini ele almadan önce bazı temel konuların gözden
geçirilmesi gerekmektedir. Biz de bu birinci bölümde önce bu temel konuları gözden geçireceğiz. Ondan sonra
Linux çekirdeğinin bellek yönetimini ele alacağız.

İşlemcilerin Sayfalama Mekanizması
==================================

Linux işletim sisteminin tam olarak çalışabilmesi için ilgili işlemcinin *sayfalama (paging)* mekanizmasına sahip
olması gerekir. CPU'nun sayfalama mekanizması ve bununla ilişkili olan özellikleri barındıran kısmına mantıksal
olarak *MMU (Memory Management Unit)* de denilmektedir. *uClinux (microcontroller Linux)* isimli proje ile Linux
çekirdeğinin sayfalama mekanizmasına sahip olmayan mikrodenetleyiciler için kullanımı mümkün hale getirilmiştir.
Ancak bu durumda çekirdeğin pek çok işlevselliği devre dışı kalmaktadır. Projenin geliştirilmesi durdurulmuş gibi
gözükmektedir. Ancak Linux çekirdekleri zaman içerisinde bu projenin açtığı yol sayesinde
``CONFIG_MMU=n`` konfigürasyon parametresiyle sayfalama mekanizması devre dışı bırakılarak da derlenebilmektedir.
Fakat yukarıda da belirttiğimiz gibi bu durumda çekirdeğin sağladığı pek çok işlevsellik devre dışı
bırakılmaktadır.

Intel 80386 ile birlikte sayfalama mekanizmasına sahip olmuştur. ARM işlemcilerinin Cortex A *(Application)*
profilleri sayfalama mekanizmasına sahiptir. Diğer güçlü işlemcilerin hemen hepsinde sayfalama mekanizması
bulunmaktadır. Aşağıda sayfalama mekanizmasına sahip önemli işlemciler bir tablo biçiminde verilmektedir:

.. list-table:: Sayfalama Mekanizmasına Sahip Önemli İşlemciler
   :header-rows: 1
   :widths: 18 35 47

   * - Mimari
     - Öne Çıkan İşlemciler
     - Notlar
   * - x86 / x86-64
     - Intel 80386+, AMD64, Core, Xeon
     - 80286'da segmentasyon, 80386'da sayfalama eklendi
   * - ARM (A-profil)
     - Cortex-A5/7/8/9/15/53/55/72/76, ARM11, ARM926EJ-S
     - M-profil (Cortex-M) MMU içermez; A-profil içerir
   * - AArch64
     - Cortex-A35/A55/A72/A78, Apple M1/M2/M3, Qualcomm Snapdragon
     - ARMv8-A ve üzeri; 4 seviyeli sayfa tablosu (4K/16K/64K)
   * - MIPS
     - MIPS32/64, Loongson
     - TLB tabanlı yazılım destekli MMU (donanım page-walk yoktur)
   * - PowerPC / POWER
     - POWER8/9/10, e500, e600, Freescale MPC serisi
     - Hash tabanlı ve radix tabanlı iki farklı MMU modeli mevcuttur
   * - SPARC
     - SPARC V8, UltraSPARC T1/T2/T3, LEON3/4 (Gaisler)
     - Sun-4u MMU; Solaris ve Linux tarafından kullanılır
   * - RISC-V (G/S)
     - SiFive U54/U74, StarFive JH7110, Milk-V Pioneer
     - Sv32 (32-bit), Sv39/Sv48/Sv57 (64-bit) sayfalama şemaları
   * - LoongArch
     - Loongson 3A5000/3A6000
     - Çin yapımı; MIPS'ten türedi; Linux 5.19'dan itibaren destekli
   * - s390 / z
     - IBM z13/z14/z15/z16
     - Segment + sayfa tablosu; 5 seviyeye kadar destekler
   * - Alpha
     - DEC Alpha 21064/21164/21264
     - Tarihi; 64-bit öncü mimari; Linux 5.18'de kaldırıldı
   * - PA-RISC
     - HP PA-7000, PA-8000 serisi
     - HP-UX ve Linux (parisc) destekli
   * - Itanium (IA-64)
     - Intel Itanium 2
     - VHPT (Virtual Hash Page Table); Linux 6.7'de kaldırıldı
   * - m68k (020+)
     - Motorola 68020/30/40/60
     - 68000/08/10 MMU içermez; 68020 ve üzeri içerir

Bu tablodaki işlemcilerin hepsinde işlemci reset edildiğinde sayfalama mekanizması *kapalı (disabled)*
durumdadır. Sayfalama mekanizmasını çalışır hale getirmek genellikle işlemcinin belli bir kontrol yazmaçındaki
belli bir biti 1 yaparak sağlanmaktadır.

İşlemcilerdeki sayfalama mekanizması aynı zamanda *sanal bellek (virtual memory)* kullanımını da mümkün hale
getirmektedir. Yani sayfalama mekanizmasına sahip olmayan işlemcilerde aynı zamanda sanal bellek kullanımı da
mümkün olamamaktadır.

Sayfalama mekanizmasına sahip olan (ve bu mekanizmanın aktif edildiği) işlemcilerde makine kodlarındaki adresler
RAM'de gerçek fiziksel adres belirtmemektedir. Bu adreslere *sanal adres (virtual address)*, *doğrusal adres
(linear address)* ya da *mantıksal adres (logical address)* denilmektedir. Biz kursumuzda bu adreslere
*sanal adresler* diyeceğiz. Örneğin C'de aşağıdaki gibi bir atama işlemi yapılmış olsun:

.. code-block:: c

   x = 100;

Derleyici de bu deyimi 32 bit Intel işlemcilerinde aşağıdaki gibi makine komutlarına dönüştürmüş olsun:

.. code-block:: asm

   MOV EAX, 100
   MOV [x_addr], EAX

Burada ``x_addr`` ifadesi ``x`` değişkeninin bellekteki adresini belirtmektedir. Ancak bu adres gerçek fiziksel
adres değildir, sanal bir adrestir. İşlemci çalışırken sanal adresleri *sayfa tablosu (page table)* denilen bir
tabloya başvurarak önce gerçek fiziksel adrese dönüştürür, sonra erişimi yapar. Aynı anda çalışan iki farklı
programdaki aynı sanal adresler aynı fiziksel adresi belirtmezler (yani böyle bir zorunluluk yoktur). Çünkü
işlemci bu sanal adresleri izleyen paragraflarda açıklayacağımız gibi farklı sayfa tablolarına başvurarak farklı
fiziksel adreslere dönüştürmektedir. (Örneğin biz bir C programını derlediğimizde makine kodlarındaki tüm
adresler sanal adreslerdir. Bu programı biz birden fazla kez çalıştırdığımızda aslında çalışan programlardaki
sanal adresler aynı olsa da program çalışırken erişilen fiziksel adreslerin birbirleriyle ilgisi yoktur.)

Biz yukarıda sayfalama mekanizmasına sahip olan işlemcilerde reset işlemi yapıldığında başlangıçta sayfalama
mekanizmasının pasif durumda olduğunu belirtmiştik. Sayfalama mekanizması pasif durumdayken program içerisindeki
sanal adresler artık gerçekten fiziksel adresleri belirtmektedir. Yani bu durumda işlemci *sayfa tablosuna*
başvurarak bir dönüştürme yapmaya çalışmamaktadır. Sayfalama mekanizması Linux sistemleri boot edilirken işletim
sisteminin yükleyici kodları tarafından aktif hale getirilmektedir.

Bir sayfa belli uzunlukta ardışıl byte'tan oluşmaktadır. Sayfa büyüklükleri işlemciden işlemciye ve aynı
işlemcide onların modlarına göre değişebilmektedir. En yaygın kullanılan sayfa büyüklüğü 4K (4096 byte)'dır.
Ancak yukarıda da belirttiğimiz gibi işlemciler değişik modlarda değişik sayfa büyüklüklerini
destekleyebilmektedir. 4K sayfa büyüklüğü pek çok işlemci tarafından (ama hepsi tarafından değil)
desteklenmektedir. Bu büyüklük halen en uygun sayfa büyüklüğü olarak kabul edilmektedir. (Ancak bellek
miktarları arttıkça daha büyük sayfalar daha uygun hale gelmeye başlayabilecektir.)

32 Bit Intel işlemcileri tarafından desteklenen sayfa büyüklükleri şunlardır:

.. list-table:: 
   :header-rows: 1
   :widths: 40 60

   * - Sayfa Büyüklüğü
     - Kullanım Alanı
   * - 4 KB
     - Standart bellek yönetimi
   * - 4 MB
     - Büyük çekirdek eşlemeleri
   * - 2 MB
     - 4 GB üzeri fiziksel RAM

64 Bit Intel işlemcileri tarafından desteklenen sayfa büyüklükleri şöyledir:

.. list-table:: 
   :header-rows: 1
   :widths: 40 60

   * - Sayfa Büyüklüğü
     - Kullanım Alanı
   * - 4 KB
     - Standart bellek yönetimi
   * - 2 MB
     - Büyük çekirdek eşlemeleri, hugepages (TLB verimliliği)
   * - 1 GB
     - Büyük veri tabanları, HPC iş yükleri
   * - 4 KB / 2 MB / 1 GB
     - 57-bit sanal adres alanı, çok büyük bellek sunucuları

32 Bit ARM işlemcileri tarafından desteklenen sayfa büyüklükleri şöyledir:

.. list-table:: 
   :header-rows: 1
   :widths: 40 60

   * - Sayfa Büyüklüğü
     - Kullanım Alanı
   * - 4 KB
     - Standart bellek yönetimi, Linux varsayılan sayfası
   * - 64 KB
     - Gömülü sistemler, DMA tampon bölgeleri
   * - 1 MB
     - Çekirdek doğrudan eşleme, bootloader bellek haritası
   * - 16 MB
     - Büyük fiziksel bellek bloklarının eşlenmesi

64 Bit ARM işlemcileri tarafından desteklenen sayfa büyüklükleri ise şöyledir:

.. list-table:: 
   :header-rows: 1
   :widths: 40 60

   * - Sayfa Büyüklüğü
     - Kullanım Alanı
   * - 4 KB
     - Standart bellek yönetimi
   * - 2 MB
     - Büyük çekirdek eşlemeleri, hugepages, TLB verimliliği
   * - 1 GB
     - Büyük veri tabanları, HPC iş yükleri
   * - 16 KB
     - Apple Silicon (macOS/iOS), özel çekirdek yapılandırması
   * - 32 MB
     - Apple Silicon büyük bellek eşlemeleri
   * - 64 KB
     - Gömülü sistemler, DMA, büyük TLB entry verimliliği
   * - 512 MB
     - Büyük fiziksel bellek bloklarının eşlenmesi

Buradan da görüldüğü gibi 32 bit, 64 bit Intel ve ARM işlemcileri 4K sayfa büyüklüklerini desteklemektedir.
Linux tarafından bu işlemcilerde temel olarak 4K büyüklüğünde sayfalar kullanılmaktadır.

Son olarak yaygın tüm işlemcilerin desteklediği sayfa büyüklüklerini de aşağıdaki tabloda veriyoruz:

.. list-table:: 
   :header-rows: 1
   :widths: 35 65

   * - İşlemci
     - Sayfa Büyüklükleri
   * - Intel IA-32 (x86)
     - 4 KB, 4 MB, 2 MB (PAE modunda)
   * - Intel/AMD x86-64
     - 4 KB, 2 MB, 1 GB
   * - ARM (AArch32)
     - 4 KB, 64 KB, 1 MB, 16 MB
   * - ARM (AArch64)
     - 4 KB, 16 KB, 64 KB, 2 MB, 32 MB, 512 MB, 1 GB
   * - RISC-V (Sv32)
     - 4 KB, 4 MB
   * - RISC-V (Sv39)
     - 4 KB, 2 MB, 1 GB
   * - RISC-V (Sv48)
     - 4 KB, 2 MB, 1 GB, 512 GB
   * - RISC-V (Sv57)
     - 4 KB, 2 MB, 1 GB, 512 GB, 256 TB
   * - PowerPC (32-bit)
     - 4 KB, 256 KB, 512 KB, 1 MB, 2 MB, 4 MB, 8 MB, 16 MB
   * - PowerPC / POWER (64-bit)
     - 4 KB, 64 KB, 16 MB, 16 GB
   * - IBM S/390 / z/Arch
     - 4 KB, 1 MB, 2 GB
   * - Alpha (AXP)
     - 8 KB, 64 KB, 512 KB, 4 MB
   * - SPARC (32-bit)
     - 4 KB, 256 KB, 16 MB
   * - SPARC64 / UltraSPARC
     - 8 KB, 64 KB, 512 KB, 4 MB, 32 MB, 256 MB, 2 GB
   * - MIPS (32-bit)
     - 4 KB, 16 KB, 64 KB, 256 KB, 1 MB, 4 MB, 16 MB, 64 MB
   * - MIPS (64-bit)
     - 4 KB, 16 KB, 64 KB, 256 KB, 1 MB, 4 MB, 16 MB, 64 MB
   * - IA-64 (Itanium)
     - 4 KB, 8 KB, 16 KB, 64 KB, 256 KB, 1 MB, 4 MB, 16 MB, 64 MB, 256 MB
   * - PA-RISC (HP)
     - 4 KB, 16 KB, 64 KB, 256 KB, 1 MB, 4 MB, 16 MB, 64 MB
   * - m68k (Motorola)
     - 4 KB
   * - OpenRISC
     - 8 KB
   * - LoongArch
     - 4 KB, 16 KB, 64 KB, 2 MB, 1 GB
   * - Xtensa
     - 4 KB, 16 KB, 64 KB, 256 KB, 1 MB, 4 MB

Biz anlatımlarımızda sayfa büyüklüğünün 4K olduğunu varsayacağız.

Sayfalama mekanizması aktif hale getirildiğinde artık işlemci fiziksel bellekteki her sayfaya 0'dan itibaren
bir sayfa numarası karşılık getirmektedir. Örneğin 32 bit Intel ya da ARM işlemcilerinde 4K'lık sayfalar
kullanıldığında fiziksel belleğin ilk 4K'lık bölgesi 0'ıncı sayfa ikinci 4K'lık bölgesi 1'inci sayfa
biçiminde numaralandırılmaktadır:

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Fiziksel Adres Alanı
     - Sayfa No
   * - 00000000  -  00000FFF
     - 0
   * - 00001000  -  00001FFF
     - 1
   * - 00002000  -  00002FFF
     - 2
   * - 00003000  -  00003FFF
     - 3
   * - ...
     - ...
   * - FFFFE000  -  FFFFEFFF
     - 1048574
   * - FFFFF000  -  FFFFFFFF
     - 1048575

32 bit bir sistemde sayfa büyüklükleri 4K olduğunda toplam 2³² ÷ 2¹² = 2²⁰ = 1.048.576 = 1048576 sayfanın
bulunduğuna dikkat ediniz.

Sayfa Tabloları ve Sanal Adreslerin Fiziksel Adreslere Dönüştürülmesi
---------------------------------------------------------------------

Sayfalama mekanizması aktif hale getirildiğinde artık işlemci makine kodlarındaki adresleri *sayfa tablosu
(page table)* denilen bir tabloya bakarak fiziksel adrese dönüştürmektedir. Sayfa tablolarının organizasyonu
kademeli bir biçimdedir. Biz önce bu dönüşümün nasıl yapıldığını açıklayabilmek için sanki sayfa tablosunu
tek kademeymiş gibi ele alacağız. Sonra bu kademeli yapı hakkında bilgi vereceğiz.

32 bit bir sistemdeki sayfa tablosunun işlevini kolay anlayabilmek için onun şöyle bir yapıda olduğunu
düşünebiliriz (buradaki değerler hex sistemdedir):

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Sanal Sayfa No
     - Fiziksel Sayfa No
   * - 00000
     - 01000
   * - 00001
     - 10401
   * - 00002
     - 11301
   * - ...
     - ...
   * - 1A400
     - 10045
   * - 1A401
     - 3F17A
   * - 1A402
     - 2417B
   * - ...
     - ...

32 bit işlemcinin program içerisindeki sanal adresi nasıl fiziksel adrese dönüştürdüğünü açıklayalım. Örneğin
işlemci aşağıdaki gibi bir makine komutuyla karşılaşmış olsun:

.. code-block:: asm

   MOV EAX, [1A4005A0]

Buradaki ``1A4005A0`` adresi sanal bir adrestir. İşlemci sayfa tablosuna başvurarak bu sanal adresi fiziksel
adrese dönüştürecektir. Bunun için işlemci önce sanal adresi sayfa büyüklüğüne (yani 4096'ya bölerek) hangi
sanal sayfaya ilişkin olduğunu belirler. Bu bölmenin ikilik (ya da 16'lık) sistemde yapılması oldukça kolaydır.
32 bitlik bir sayı 12 kere sağa ötelenirse ya da onun düşük anlamlı 12 biti atılırsa 4096'ya bölünmüş olur.
32 bitlik bir sayının sağındaki 12 bitin aynı zamanda sayının 4096'ya bölümünden elde edilen kalan değeri
olduğuna dikkat ediniz. İşte işlemci 32 bitlik sanal adresi 20 bitlik ve 12 bitlik iki kısma ayırmaktadır.
Örneğin ``1A4005A0`` sanal adresi iki kısma şöyle ayrılmaktadır:

.. code-block:: text

   1A400 5A0

Buradaki ``1A400`` değeri sanal sayfa numarasını, ``5A0`` değeri ise o sanal sayfanın başından itibaren sayfa
offset'ini belirtmektedir. İşte işlemci bu örnekte önce sayfa tablosuna başvurarak ``1A400`` sanal sayfaya
karşı gelen fiziksel sayfa numarasını, bu fiziksel sayfa numarasına da sayfa offset'ini ekleyerek gerçek
fiziksel adresi elde eder. Örneğimizdeki sayfa tablosuna göre ``1A4005A0`` sanal adres ile işlemci aslında
``100455A0`` adresine erişecektir.

Şimdi bir programın tamamının (genellikle böyle olmaz) fiziksel RAM'e yüklendiğini düşünelim. Bu durumda
prosesin sanal bellek alanı ardışıl olacaktır ancak aslında prosesin fiziksel bellekteki yerleşimi ardışıl
olmayacaktır. Örneğin program içerisinde ``malloc`` fonksiyonu ile 8K'lık bir tahsisat yapmış olalım. Bu
durumda aslında tahsis edilen alan iki sayfa uzunluğundadır. ``malloc`` bize sanal adresi vermektedir. Yani
``malloc`` fonksiyonunun verdiği sanal adresten itibaren 8K'lık alanı biz programcı olarak ardışıl bir
biçimde kullanabiliriz. Ancak arka planda aslında bu tahsis edilen alan iki sayfaya bölündüğü için fiziksel
RAM'de ardışıl olmak zorunda değildir. Aynı durum programın makine kodlarının bulunduğu bölümler için de
yerel değişkenlerin tutulduğu stack için de geçerlidir.

Peki işlemci sayfa tablosunun yerini nasıl bilmektedir? İşte işlemcilerde özel bir yazmaç sayfa tablosunun
yerini göstermektedir. Örneğin Intel işlemcilerinde ``CR3`` yazmacı sayfa tablosunun fiziksel adresini
gösterir. Yani Intel işlemcilerinde işlemci her zaman sayfa tablosuna ``CR3`` yazmacının gösterdiği yerden
erişmektedir. ARM işlemcileri de benzer biçimde sayfa tablosuna ``TTBR0_EL1`` ve ``TTBR1_EL1`` yazmaçlarının
gösterdiği yerden erişmektedir. Tabii sayfa tablolarını oluşturan ve bu yazmaca sayfa tablolarının başlangıç
adresini yerleştiren işletim sistemidir.

Sayfalama mekanizmasını kullanan işletim sistemlerinde her proses için (thread için değil) ayrı bir sayfa
tablosu oluşturulmaktadır. İşletim sistemi *thread'ler arası geçiş (context switch)* oluştuğunda eğer
çalışmasına ara verilen thread'le geçilen thread farklı proseslere ilişkinse sayfa tablosunun yerini gösteren
yazmacı (Intel işlemcilerindeki ``CR3`` yazmacı) değiştirerek yeni geçilen thread'in artık kendi prosesine
ilişkin sayfa tablosunu göstermesini sağlamaktadır. Örneğin sistemde o anda P1, P2 ve P3 olmak üzere üç
proses çalışıyor olsun. Bu durumda işletim sistemi bu üç proses için üç farklı sayfa tablosu oluşturacaktır.
Bu üç prosesin thread'leri de aşağıdaki gibi olsun:

.. image:: _static/proses-thread-diagram.png
   :alt: Proses ve Thread Hiyerarşisi
   :align: center
   :width: 70%

Eğer şu anda ``T11`` thread'i çalışıyorsa işlemcinin ilgili yazmacı (Intel'deki ``CR3`` yazmacı) P1
prosesinin sayfa tablosunu gösteriyor durumdadır. Thread'ler arası geçiş oluşup ``T12`` thread'i çalışmaya
başlayınca ``T12`` thread'i de P1 prosesinin bir thread'i olduğu için kullanılan sayfa tablosu (yani
Intel'deki ``CR3`` yazmacı) değiştirilmez. Ancak ``T12`` thread'inden ``T21`` thread'ine geçilirken işletim
sistemi işlemcinin ilgili yazmacını değiştirerek işlemcinin artık P2 prosesinin sayfa tablosunu göstermesini
sağlamaktadır.
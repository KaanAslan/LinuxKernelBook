===========================
Bellek Yönetimi (I. Bölüm)
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
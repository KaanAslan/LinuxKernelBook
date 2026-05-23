===========================================
Çekirdeğin Derlenmesi
===========================================

Bu bölümde ayrıntılı bir biçimde Linux çekireğinin derlenmesi sürecini ele alacapız.

Çekirdek Davranışını Değiştirme Yöntemleri
===========================================

Linux çekirdeğinin kodlarına dokunmadan onunla ilgili bazı davranış değişikliklerinin yapılması
temelde beş biçimde sağlanabilmektedir:

**1. Çekirdek modülleri ve aygıt sürücüler yoluyla**

Çekirdek modunda çalışan *çekirdek modülleri (kernel modules)* ve *aygıt sürücüler (device drivers)*
yoluyla davranış değişikliği oluşturulabilmektedir. İşletim sistemlerinin çoğu çekirdeğin bir parçası
gibi işlev görecek kodların yüklenmesine ve çalıştırılmasına olanak sağlamaktadır. Bu yöntemde
çekirdeğin yeniden derlenmesine gerek yoktur. Zaten çekirdek modülleri ve aygıt sürücüleri çalışmakta
olan çekirdek içerisine yüklenmektedir. Çekirdek modüllerini ve aygıt sürücüleri *kasalı bilgisayarlardaki
genişleme yuvalarına takılan kartlara benzetebiliriz.* Nasıl takılan bu kartlar donanımın bir parçası
haline geliyorsa çekirdek modülleri ve aygıt sürücüler de çekirdeğin bir parçası haline gelmektedir.
Linux'taki çekirdek modüllerinin ve aygıt sürücülerinin yazımı kursumuzun konularına dahil değildir.

**2. Çekirdek komut satırı parametreleri yoluyla**

Çekirdek yüklenip başlatılırken (initialize ederken) ismine *çekirdek komut satırı parametreleri
(kernel command line parameters)* denilen parametreler yoluyla çekirdeğin davranışı
değiştirilebilmektedir. Çekirdek komut satırı parametreleri *önyükleyici tarafından* çekirdeğe
iletilmektedir. Linux çekirdeğinin pek çok komut satırı parametresi vardır. Bu parametreler yoluyla
çekirdekte bazı davranış değişiklikleri oluşturulabilmektedir. Bunun için de çekirdeğin yeniden
derlenmesi gerekmez.

**3. Konfigürasyon parametreleri yoluyla**

Çekirdek derlenirken çekirdek kodlarına hiç dokunmadan bazı konfigürasyon parametreleri ile oynanarak
çekirdekte davranış değişiklikleri oluşturulabilmektedir. Çekirdek konfigüre edilirken bazı alt
sistemler çekirdekten çıkartılabilmekte, bazı alt sistemler üzerinde ince ayarlar yapılabilmektedir.
Tabii çekirdek konfigüre edilirken her ne kadar biz çekirdek kodlarını değiştirmiyor olsak da aslında
sembolik sabitler yoluyla arka planda derleme işlemine sokulan kodlar üzerinde de değişikler yapılmış
olmaktadır. O halde çekirdeğin konfigüre edilmesinin iki amacı vardır:

- Çekirdek içerisindeki alt sistemlere ilişkin bileşenlerin çekirdeğe eklenmesini ve çekirdekten
  çıkartılmasını sağlamak.
- Çekirdeğin üzerinde bazı davranış değişikliklerini oluşturmak.

Çekirdek konfigüre edildikten sonra yeniden derlenmelidir. Yani bu yöntem çekirdeğin yeniden
derlenmesini gerektirmektedir.

**4. Çekirdek kodlarında doğrudan değişiklik yaparak**

Çekirdek kodlarında doğrudan değişiklikler yapılıp çekirdek yeniden derlenebilir. Bu çekirdekte
davranış değişikliği oluşturmak için kullanılan en aşağı seviyeli yöntemdir.

**5. Çekirdek çalışırken komutlar ve mekanizmalar yoluyla**

Nihayet çekirdek çalışırken de çekirdeğin davranışı bazı komutlarla (bu komutlar bazı mekanizmaları
ve sistem fonksiyonlarını kullanmaktadır), konfigürasyon dosyalarıyla ve bazı mekanizmalarla da
(örneğin *proc* ve *sys* dosya sistemi yoluyla) çekirdek davranışları değiştirilebilmektedir. Tabii
bunun için de çekirdeğin yeniden derlenmesi gerekmez. Örneğin sistem çalışırken bir prosesin
açabileceği dosya sayısını *proc* dosya sistemi yoluyla şöyle değiştirebiliriz:

.. code-block:: bash

   $ echo 2048 | sudo tee /proc/sys/fs/file-max


.. rubric:: ── 5. Ders · 02 Ağustos 2025, Cumartesi ──

Çekirdek Komut Satırı Parametreleri
=====================================

Linux'ta çekirdek komut satırı parametreleri birbirinden boşluklarla ayrılmış yazılardan
oluşmaktadır. Bazı parametrelerin argümanları yoktur, bazılarının vardır. Eğer parametrenin bir
argümanı varsa *parametre=değer* biçiminde (``=`` karakteri boşluksuz olarak kullanılmalıdır),
yoksa yalnızca *parametre* biçiminde belirtilmektedir. Çekirdek komut satırı parametreleri tek
bir yazı biçiminde çekirdeğe aktarılmaktadır. Çekirdek bu komut satırı parametrelerini kendini
kullanıma hazır hale getirmenin (kendini initialize etmenin) ön aşamalarında parse eder ve bu
değerleri yapılandırma amacıyla kullanır. Tabii çekirdeğin komut satırı parametreleri tipik olarak
önyükleyici (bootloader) tarafından çekirdeğe iletilmektedir. Örneğin çekirdek komut satırı
parametreleri aşağıdaki gibi bir görünümde olabilir:

.. code-block:: text

   console=serial0,115200 console=tty1 root=PARTUUID=382d6f16-02 rootfstype=ext4 fsck.repair=yes
   rootwait quiet splash plymouth.ignore-serial-consoles cfg80211.ieee80211_regdom=TR

Linux çekirdeğinin onlarca farklı komut satırı parametresi vardır. Bunların çoğu spesifik konulara
ilişkindir ve ancak çekirdeğin yapısını iyi bilen kişiler tarafından anlamlandırılabilmektedir. Tabii
bazı parametrelerin anlamları herkes tarafından anlaşılacak kadar açıktır. Çekirdek parametrelerinin
dokümantasyonuna aşağıdaki bağlantıdan erişebilirsiniz:

   https://www.kernel.org/doc/html/v4.14/admin-guide/kernel-parameters.html

Linux çekirdeği komut satırı parametrelerini parse ederken gerçekte olmayan (yani çekirdek tarafından
kullanılmayan) bir parametre gördüğünde onu dikkate almamaktadır. Ancak biz kendi parametrelerimizin de
çekirdek tarafından saklanmasını sağlayabiliriz. Bu konunun bazı ayrıntıları vardır.

Biz kursumuzda çeşitli bölümlerde çekirdeğin bazı komut satırı parametreleri hakkında bazı
açıklamalarda bulunacağız.


Çekirdeği Yeniden Derlemenin Gerektiği Durumlar
================================================

Bazı durumlarda çekirdeğin sıfırdan derlenmesi gerekebilmektedir. Çekirdeğin yeniden derlenmesinin
gerektiği tipik durumlar şunlardır:

- Bazı çekirdek modüllerinin ve aygıt sürücülerin çekirdek imajından çıkartılması ve dolayısıyla
  çekirdeğin küçültülmesi için.
- Yeni birtakım modüllerin ve aygıt sürücülerin çekirdek imajına eklenmesi için.
- Çekirdeğe tamamen başka birtakım özelliklerin ve alt sistemlerin eklenmesi için.
- Çekirdek üzerinde çekirdek komut satırı parametreleriyle sağlanamayacak bazı konfigürasyon
  değişikliklerinin yapılabilmesi için.
- Çekirdek kodlarında yapılan değişikliklerin etkin hale getirilmesi için.
- Çekirdeğe yama (patch) yapılması için.
- Yeni çıkan çekirdek kodlarının kullanılabilir hale getirilmesi için ya da eski çekirdeklerin
  kullanımını sağlamak için.


Çekirdek Derlemesi Hakkında
============================

Bu bölümde çekirdek kodlarının nasıl derleneceği ve derlenmiş olan çekirdekle sistemin nasıl boot
edileceği üzerinde duracağız.


Çapraz Derleme
--------------

Çekirdek derlemesi o anda çalışılan platform için yapılabileceği gibi başka bir platform için de
yapılabilmektedir. Aşağı seviyeli yazılım terminolojisinde başka bir sistem için yapılan derleme
işlemlerine *çapraz derleme (cross compile)* denilmektedir. Örneğin Intel tabanlı PC'lerde ARM
işlemcilerinin bulunduğu gömülü aygıtlar için Linux çekirdeğini derlemek isteyebiliriz. Bu bir
çapraz derleme faaliyetidir. Çapraz derleme işlemleri için *çapraz araç zincirlerinin (cross
toolchains)* kullanılması gerekmektedir. Linux çekirdeğinin derlenmesinde yalnızca C derleyicisi
değil pek çok yardımcı programlara da gereksinim duyulmaktadır.


Çekirdek Kaynak Kodlarının İndirilmesi
---------------------------------------

Çekirdeğin derlenmesi için öncelikle çekirdek kaynak kodlarının derleme yapılacak bilgisayara
indirilmesi gerekir. Bazı dağıtımlar default durumda çekirdeğin kaynak kodlarını da kurulum sırasında
makineye çekmektedir. Çekirdek kodları resmi olarak ``kernel.org`` sitesinde bulundurulmaktadır.
Tarayıcıdan ``kernel.org`` sitesine girip ``pub/linux/kernel`` dizinine geçtiğinizde tüm yayınlanmış
çekirdek kodlarını göreceksiniz. İndirmeyi tarayıcıdan doğrudan yapabilirsiniz. Eğer indirmeyi komut
satırından *wget* programıyla yapmak istiyorsanız aşağıdaki URL'yi kullanabilirsiniz:

.. code-block:: text

   https://cdn.kernel.org/pub/linux/kernel/[MAJOR_VERSION].x/linux-[VERSION].tar.xz

Buradaki ``MAJOR_VERSION`` 3, 4, 5, 6 gibi tek bir sayıyı belirtmektedir. ``VERSION`` ise çekirdeğin
büyük ve küçük numaralarını belirtmektedir. Örneğin biz çekirdeğin 6.9.2 versiyonunu komut satırından
şöyle indirebiliriz:

.. code-block:: bash

   $ wget https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.9.2.tar.xz


Sıkıştırma Formatları ve tar Komutu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Çekirdek kodları indirildikten sonra açılması gerekir. Açma işlemi *tar* komutuyla aşağıdaki gibi
yapılabilir:

.. code-block:: bash

   $ tar -xvJf linux-5.15.12.tar.xz

UNIX/Linux sistemlerinde kullanılan *tar* programı sıkıştırma yapmamaktadır. Yalnızca dosyaları uç uca
ekleyip onları tek bir dosya haline getirmektedir. Bu sayede dosyalar dosya sisteminde daha az yer
kaplar hale getirilmektedir. Aynı zamanda onların iletilmesi ve kopyalanması da kolaylaştırılmaktadır.
Sıkıştırma programları ise aslında tek bir dosyayı sıkıştırmaktadır. O halde UNIX/Linux sistemlerinde
kullanıcılar bir grup dosyayı sıkıştırmak için önce onları tar'layıp tek dosya haline getirirler, sonra
bu dosyayı sıkıştırırlar. Bu işlemler sonucunda dosya uzantısı ``.tar.gz`` gibi, ``.tar.xz`` gibi
dosyanın hem tar'lanmış hem de sıkıştırılmış olduğunu belirten biçimde olur. Açım sırasında da önce
sıkıştırılan dosyalar açılır, buradan ``.tar`` dosyası elde edilir; sonra da bu ``.tar`` dosyasının
içerisindeki dosyalar dışarı çıkartılır.

Linux'ta çeşitli sıkıştırma formatları kullanılmaktadır:

- **gzip** — uzantı: ``.gz``
- **bz2** — uzantı: ``.bz2``
- **xz** — uzantı: ``.xz``
- **zip** — uzantı: ``.zip`` ya da ``.z``

Bu formatlar sıkıştırma bakımından farklı performans göstermektedir. Ancak formatın sıkıştırma
performansı ne kadar yüksekse işlem yapma süresi de o kadar uzun olmaktadır. Tipik sıkıştırma
performans sıralaması şöyledir:

.. code-block:: text

   xz  >  bz2  >  gzip ≈ zip

Yani en iyi sıkıştırma *xz* formatında, daha sonra *bz2* formatında, daha sonra da *gzip*
formatındadır. *gzip* ile *zip* aynı algoritmaları kullandığından performansları birbirine benzerdir.

Her format için ayrı araçlar mevcuttur:

.. list-table::
   :header-rows: 1
   :widths: 20 25 25

   * - Format
     - Sıkıştırma
     - Açma
   * - gzip
     - ``gzip``
     - ``gunzip``
   * - bz2
     - ``bzip2``
     - ``bunzip2``
   * - xz
     - ``xz``
     - ``unxz``
   * - zip
     - ``zip``
     - ``unzip``

*tar* programının en çok kullanılan seçenekleri şunlardır: ``-c`` (tar'lamak için), ``-x`` (açmak
için), ``-v`` (ayrıntılı çıktı), ``-f`` (``.tar`` dosyasını belirtmek için; seçenek listesinin
sonunda olmalıdır).

.. warning::

   ``-f`` seçeneğinin seçenek listesinde en sonda yer alması gerektiğine dikkat ediniz.

**gzip ile örnekler:**

.. code-block:: bash

   # Yalnızca tar'lama:
   $ tar -cf test.tar x.txt y.txt z.txt

   # Tek adımda tar'la + gzip sıkıştır (-z seçeneği):
   $ tar -cvzf test.tar.gz x.txt y.txt

   # Aç:
   $ tar -xvzf test.tar.gz

.. note::

   *gzip* ve *gunzip* programlarının kaynak dosyayı sildiğine dikkat ediniz.

**bzip2 ile örnekler:**

.. code-block:: bash

   # Tek adımda tar'la + bzip2 sıkıştır (-j seçeneği):
   $ tar -cvjf test.tar.bz2 x.txt y.txt

   # Aç:
   $ tar -xvjf test.tar.bz2

**xz ile örnekler:**

.. code-block:: bash

   # Tek adımda tar'la + xz sıkıştır (-J seçeneği, büyük harf):
   $ tar -cvJf test.tar.xz x.txt y.txt

   # Aç:
   $ tar -xvJf test.tar.xz

.. note::

   *tar* seçeneklerinde ``-z`` gzip için, ``-j`` bzip2 için, ``-J`` (büyük harf) xz için
   kullanılmaktadır.


Dağıtıma Özgü Çekirdek Kaynak Kodları
---------------------------------------

Dağıtımlar (Ubuntu, Mint, Fedora gibi) çekirdek kodlarında küçük değişiklikler ve kendilerine özgü
özelleştirmeler ve yamamalar da yapabilmektedir. Debian tabanlı sistemlerde o anda makinede yüklü olan
mevcut çekirdeğin ilgili dağıtıma ilişkin kaynak kodlarını indirmek için aşağıdaki komutu
kullanabilirsiniz:

.. code-block:: bash

   $ sudo apt-get install linux-source

Burada yükleme ``/usr/src`` dizinine yapılacaktır. Ancak bu komut doğrudan sıkıştırılmış dosyayı
indirmektedir; açım yapmamaktadır. Ayrıca belirli bir versiyona ilişkin kaynak kodlar da indirilebilir.
Bunun için komutta ``linux-source`` argümanına istenilen versiyonun majör, minör ve patch numarası
``-majör.minör.patch`` biçiminde eklenir. Örneğin:

.. code-block:: bash

   $ sudo apt-get install linux-source-6.8.0

.. note::

   Bu biçimde indirilen çekirdek kaynak kodları Debian ya da Ubuntu depolarından indirilmektedir.
   Bunlar bu dağıtımlar tarafından yamanmış kodlardır. Örneğin Mint'te çalışıyorsanız indirdiğiniz
   kodlar Ubuntu için yamanmış kodlar olacaktır.

**BBB (BeagleBone Black) için:**

BBB için bazı özelleştirmelerin de yapılmış olduğu kaynak kodların indirilip derlenmesi birtakım
kolaylıklar sağlamaktadır:

.. code-block:: bash

   $ git clone https://github.com/beagleboard/linux.git

**Raspberry Pi için:**

Raspberry Pi'a özgü daha güncel aygıt sürücüler ve aygıt ağacı dosyalarını içeren Linux kaynak
kodlarının projenin kendi sitesinden indirilmesi daha uygun olur:

.. code-block:: bash

   $ git clone --depth=1 https://github.com/raspberrypi/linux.git


Çekirdek Versiyon Numaralandırması
====================================

Linux kaynak kodlarının versiyonlanması eskiden daha farklıydı. Çekirdeğin 2.6 versiyonlarından sonra
versiyon numaralandırma sistemi değiştirildi. Eskiden (2.6 ve öncesinde) versiyon numaraları çok yavaş
ilerletiliyordu. 2.6 sonrasındaki yeni versiyonlamada versiyon numaraları daha hızlı ilerletilmeye
başlanmıştır. Bugün kullanılan Linux versiyonları nokta ile ayrılmış üç sayıdan oluşmaktadır:

.. code-block:: text

   Majör.Minör.Patch

Buradaki *majör numara* büyük ilerlemeleri, *minör numara* ise küçük ilerlemeleri belirtmektedir.
Eskiden (2.6 ve öncesinde) tek sayı olan minör numaralar *geliştirme versiyonlarını (ya da beta
versiyonlarını)*, çift olanlar ise stabil hale getirilmiş dağıtılan versiyonları belirtiyordu. Ancak
2.6 sonrasında artık tek ve çift minör numaralar arasında böyle bir anlam farklılığı kalmamıştır.
*Patch numarası* birtakım böceklerin giderildiği ya da çok küçük yeniliklerin çekirdeğe dahil edildiği
versiyonları belirtmektedir.

Linux kaynak kodları konfigüre edilip derlendiğinde çekirdek imajının ismine bir alan daha
eklenebilmektedir. Bu alana biz *Extra* alanı diyeceğiz. Bu durumda çekirdek imaj ismi şu hale
gelecektir:

.. code-block:: text

   Majör.Minör.Patch-Extra

*Extra* için ``-rcX``, ``-stable``, ``-custom``, ``-generic`` gibi sözcükler kullanılabilir. Bu
*extra* alanı tamamen derleme işlemini yapan kişi ya da kurumun isteğine göre belirlenmiş bir
alandır:

- *rcX* — *release candidate* (yayın adayı) anlamındadır; ``X`` bir sayı belirtir.
- *stable* — dağıtılan sürümün *kararlı sürüm* olduğunu belirtir.
- *custom* — sistem programcısının çekirdekte birtakım değişiklikler yaptığını belirtir.
- *generic* — çekirdeğin *genel kullanım için konfigüre edilmiş* olduğunu belirtir; dağıtımlar
  tarafından sıkça kullanılır.
- *realtime* — genellikle gerçek zamanlı bir yapılandırmada kullanılmaktadır.

*generic* ve *realtime* sözcüklerinin öncesinde ``-N-`` biçiminde bir sayı da bulunabilmektedir. Bu
sayı dağıtıma özgü yama ya da derleme numarasını belirtmektedir. Örneğin:

.. code-block:: text

   6.8.0-51-generic

Burada ``-51`` yapılandırmaya özgü bir numarayı, ``-generic`` ise yapılandırmanın genel kullanım için
olduğunu belirtmektedir.

Çalışmakta olan Linux sistemi hakkında bilgiler *"uname -a"* komutu ile elde edilebilir:

.. code-block:: bash

   $ uname -a
   Linux kaan-virtual-machine 5.15.0-91-generic Ubuntu SMP Tue Nov 14 13:30:08 UTC 2023 x86_64 x86_64 x86_64 GNU/Linux

Bu bilgi içerisinden yalnızca çekirdek versiyonu görüntülenmek isteniyorsa *"uname -r"* seçeneği
kullanılmalıdır:

.. code-block:: bash

   $ uname -r
   6.8.0-51-generic

Buradan biz çekirdeğin ``6.8.0`` sürümünün kullanıldığını anlıyoruz. Burada genel yapılandırılmış bir
çekirdek söz konusudur. ``51`` sayısı dağıtıma özgü yama ya da derleme numarasını belirtir.

Daha önceden de belirttiğimiz gibi *uname* komutu bu bilgileri *proc* dosya sisteminin içerisinden
almaktadır. Örneğin:

.. code-block:: bash

   $ cat /proc/version
   Linux version 5.15.0-91-generic (buildd@lcy02-amd64-045) (gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0,
   GNU ld (GNU Binutils for Ubuntu) 2.38) #101-Ubuntu SMP Tue Nov 14 13:30:08 UTC 2023


Derleme Araçları
=================

Bilindiği gibi büyük projelerin derlenmesi için *build otomasyon araçları (build automation tools)*
denilen araçlar kullanılmaktadır. Bunların en yaygın kullanılanı *make* denilen araçtır. Linux
çekirdeklerinin derlenmesi de *make* aracı ile yapılmaktadır. Ancak Linux çekirdeklerinin derlenmesinde
projeye özgü bazı yapılar ve yöntemler de kullanılmıştır. Buna *KConfig sistemi* ya da *KBuild sistemi*
denilmektedir. (*KConfig* sistemi ya da *KBuild* sistemi Linux çekirdeğinin dışında aşağı seviyeli pek
çok proje tarafından da kullanılmaktadır.) Biz önce çekirdek derleme işleminin hangi adımlardan
geçilerek yapılacağını göreceğiz. Sonra çekirdeğin önemli konfigürasyon parametreleri üzerinde biraz
duracağız. Sonra da çekirdekte bazı değişiklikler yapıp sistemin değiştirilmiş çekirdekle açılmasını
sağlayacağız.


Çekirdek Derleme Adımları
==========================

Linux'ta çekirdek derlemesi tipik olarak aşağıdaki aşamalardan geçilerek gerçekleştirilmektedir.


Adım 1: Gerekli Araçların Kurulması
-------------------------------------

Derleme öncesinde derlemenin yapılacağı makinede bazı programların yüklenmiş olması gerekmektedir.
Çünkü *KBuild* sistemi yalnızca binary araçları değil bazı başka kütüphaneleri ve araçları da
kullanmaktadır. Çekirdeğin derlenmesi için gerekebilecek programları şöyle yükleyebilirsiniz
(burada Debian türevi bir dağıtımın kullanıldığını varsayacağız):

.. code-block:: bash

   $ sudo apt update
   $ sudo apt install build-essential libncurses-dev bison flex libssl-dev libelf-dev dwarves


Adım 2: Kaynak Kodların İndirilmesi ve Açılması
-------------------------------------------------

Çekirdek kodları indirilir ve açılır. Biz bu konuyu yukarıda ele almıştık. İndirmeyi şöyle
yapabiliriz:

.. code-block:: bash

   $ wget https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.9.2.tar.xz
   $ tar -xvJf linux-6.9.2.tar.xz

Bu işlemden sonra ``linux-6.9.2`` isminde bir dizin oluşturulacaktır.


.. rubric:: ── 6. Ders · 03 Ağustos 2025, Pazar ──

Adım 3: Çekirdeğin Konfigüre Edilmesi
---------------------------------------

Çekirdek derlenmeden önce konfigüre edilmelidir. Çekirdeğin konfigüre edilmesi birtakım çekirdek
özelliklerinin belirlenmesi anlamına gelmektedir. Bu belirmeler konfigürasyon dosyası yoluyla
yapılmaktadır. Konfigürasyon dosyası kaynak kod ağacının kök dizininde (örneğimizde ``linux-6.9.2``
dizini) ``.config`` ismiyle bulunmalıdır.

Bu ``.config`` dosyası default durumda kaynak dosyaların kök dizininde yoktur; derlemeyi yapacak
kişi tarafından oluşturulması gerekmektedir. Çekirdek konfigürasyon parametreleri oldukça fazladır
ve bunların bazılarının anlamlandırılması özel bilgi gerektirmektedir. Çekirdek konfigürasyon
parametreleri çok fazla olduğu için bazı genel amaçları karşılayacak biçimde default değerlerle
önceden oluşturulmuş konfigürasyon dosyaları kaynak kod ağacında ``arch/<mimari>/configs`` dizininin
içerisinde bulunmaktadır. Örneğin Intel x86 mimarisi için bu default konfigürasyon dosyaları şöyledir:

.. code-block:: bash

   $ ls arch/x86/configs
   hardening.config  i386_defconfig  tiny.config  x86_64_defconfig  xen.config

64 bit Linux sistemleri için ``x86_64_defconfig`` dosyasını kullanabiliriz. O halde bu dosyayı
kaynak dosyaların bulunduğu kök dizine ``.config`` ismiyle kopyalayabiliriz (bütün işlemlerde
çekirdek kaynak kodlarının kök dizininde bulunduğumuzu varsayıyoruz):

.. code-block:: bash

   $ cp arch/x86/configs/x86_64_defconfig .config

.. note::

   Linux kaynak kodlarındaki default konfigürasyon dosyaları minimalist biçimde konfigüre
   edilmiştir. Bu nedenle pek çok modül bu default konfigürasyon dosyalarında işaretlenmiş değildir.
   Bu tür denemeleri zaten çalışan çekirdeğin derlenmesinde kullanılan konfigürasyon dosyalarından
   hareketle yaparsanız daha fazla modül dosyası oluşturulabilir ancak daha az zahmet çekebilirsiniz.

Burada bir noktaya dikkatinizi çekmek istiyoruz. Çekirdek kaynak kodlarındaki
``arch/<platform>/configs`` dizinindeki ``x86_64_defconfig`` konfigürasyon dosyası ``.config``
ismiyle kopyalandıktan sonra ayrıca *"make menuconfig"* ya da *"make oldconfig"* gibi bir işlemle
onun satırlarına eklenecek çekirdekte bulunan yeni birtakım özelliklere ilişkin bazı default
değerlerin de eklenmesi gerekir.

Linux sistemlerinde genel olarak ``/boot`` dizini içerisinde ``config-<çekirdek_sürümü>`` ismiyle
mevcut çekirdeğe ilişkin konfigürasyon dosyası bulundurulmaktadır.

``.config`` dosyasını oluşturmanın alternatif yolları şöyle özetlenebilir:

``make defconfig``
   Çalışılan sisteme uygun olan konfigürasyon dosyasını temel alarak mevcut donanım bileşenlerini
   de gözden geçirerek sistemin açılması için gerekli minimal bir konfigürasyon dosyasını ``.config``
   ismiyle oluşturur. Örneğin 64 bit Intel sisteminde ``make defconfig`` çalıştırıldığında
   ``arch/x86/configs/x86_64_defconfig`` dosyası temel alınır.

``make oldconfig``
   Bu seçeneği kullanmak için kaynak kök dizinde ``.config`` dosyasının bulunuyor olması gerekir.
   *KConfig* dosyalarındaki ve kaynak dosya ağacındaki diğer değişiklikleri de göz önüne alarak bu
   eski ``.config`` dosyasını yeni versiyona uyumlandırmaktadır. Başka bir deyişle *"make oldconfig"*
   eski bir konfigürasyon dosyasını yeni çekirdekler için uyumlandırmaktadır.

``make <platform>_defconfig``
   Belli bir platformun default konfigürasyon dosyasını ``.config`` dosyası olarak kaydeder. Örneğin
   Intel makinelerinde çalışırken BBB için ``make bb.org_defconfig`` komutu uygulanabilir.

``make modules``
   Yalnızca modülleri (aygıt sürücü dosyaları) derler; çekirdek derlemesi yapmaz. Yalnızca *make*
   işlemi zaten aynı zamanda bu işlemi de yapmaktadır.

``make uninstall``
   *"make install"* işlemi ile yapılanları geri alır.

Aşağıdaki *make xxxconfig* komutları seyrek kullanılmaktadır:

``make allnoconfig``
   Tüm seçenekleri *hayır (no)* olarak ayarlar (minimal özellikler).

``make allyesconfig``
   Tüm seçenekleri *evet (yes)* olarak ayarlar (maksimum özellikler).

``make allmodconfig``
   Tüm aygıt sürücülerin çekirdeğin dışında modül biçiminde derleneceğini belirtir.

``make localmodconfig``
   Sistemde o anda yüklü modüllere dayalı bir yapılandırma dosyası oluşturur.

``make silentoldconfig``
   Yeni seçenekler için onları görmezden gelir; yeni özellikler ``.config`` dosyasına yansıtılmaz.

``make dtbs``
   Kaynak kod ağacında ``/arch/platform/boot/dts`` dizinindeki aygıt ağacı kaynak dosyalarını
   derler ve ``dtb`` dosyalarını elde eder. Gömülü sistemlerde bu işlemin yapılması ve her çekirdek
   versiyonuyla o versiyonun ``dtb`` dosyasının kullanılması tavsiye edilir.

Pek çok dağıtım o anda yüklü olan çekirdeğe ilişkin konfigürasyon dosyasını ``/boot`` dizini
içerisinde ``config-$(uname -r)`` ismiyle bulundurmaktadır. Örneğin kursun yapılmakta olduğu Mint
dağıtımında ``/boot`` dizininin içeriği şöyledir:

.. code-block:: text

   $ ls /boot
   config-6.8.0-51-generic      initrd.img.old
   System.map-6.8.0-51-generic  efi
   grub                         vmlinuz
   initrd.img                   vmlinuz-6.8.0-51-generic
   initrd.img-6.8.0-51-generic

Buradaki ``config-6.8.0-51-generic`` dosyası çalışmakta olduğumuz çekirdekte kullanılan
konfigürasyon dosyasıdır. Bu dosya sistem açılırken herhangi bir biçimde kullanılmamaktadır (yani bu
dosyayı silseniz hiçbir sorun oluşmaz). Bu dosya o çekirdeği yeniden derleyecek kişiler için
kolaylık sağlamak amacıyla bulundurulmaktadır.

Eğer çalışılan sistemdeki konfigürasyon dosyasını temel alacaksanız bu dosyayı Linux kaynak
kodlarının bulunduğu kök dizine ``.config`` ismiyle kopyalayabilirsiniz:

.. code-block:: bash

   $ cp /boot/config-$(uname -r) .config

Eski bir konfigürasyon dosyasını yeni bir çekirdekle kullanmak için ayrıca *"make oldconfig"*
işleminin de yapılması gerekmektedir. Bir sonraki adımda göreceğimiz *"make menuconfig"* işlemi
aynı zamanda *"make oldconfig"* işlemini de kendi içerisinde barındırmaktadır.


Adım 4: Konfigürasyon Değişikliklerinin Yapılması
--------------------------------------------------

Elimizde pek çok değerin set edilmiş olduğu ``.config`` isimli bir konfigürasyon dosyası vardır.
Artık bu konfigürasyon dosyasından hareketle yalnızca istediğimiz özellikleri değiştirebiliriz.
Bunun için *"make menuconfig"* komutunu kullanabiliriz:

.. code-block:: bash

   $ make menuconfig

Bu komutla birlikte text ekranda konfigürasyon seçenekleri listelenecektir. Tabii buradaki seçenekler
``.config`` dosyasındaki içerikten hareketle oluşturulmuş durumdadır. Bunların üzerinde değişiklikler
yaparak ``.config`` dosyasını yeniden save edebiliriz. Aslında *"make menuconfig"* işlemi hiç
``.config`` dosyası oluşturulmadan doğrudan da yapılabilmektedir. Bu durumda hangi sistemde
çalışılıyorsa o sisteme özgü default konfigürasyon dosyası temel alınmaktadır. Biz en azından
``General Setup/Local version - append to kernel release`` seçeneğine ``-custom`` gibi bir sonek
girmenizi, böylece yeni çekirdeğe ``-custom`` soneki iliştirmenizi tavsiye ederiz.

.. note::

   *"make menuconfig"* işlemi zaten *"make oldconfig"* işlemini de kendi içerisinde
   barındırmaktadır. Dolayısıyla *"make menuconfig"* yapıyorsanız ayrıca *"make oldconfig"*
   işlemini yapmanıza gerek yoktur.

Peki biz hazır bir ``.config`` dosyasını kaynak kod ağacının kök dizinine kopyaladıktan sonra hiç
*"make menuconfig"* ya da *"make oldconfig"* yazmazsak ne olur? Bu durumda sorun çıkmayabilir. Eğer
kaynak kod çekirdeği yeniyse *make* işlemi sırasında *"make oldconfig"* gibi bir işlem de
yapılmaktadır. Ancak ``.config`` dosyasını kök dizine kopyaladıktan sonra *"make menuconfig"* ya da
*"make oldconfig"* işlemini yapmanızı salık veriyoruz.

``.config`` dosyası elde edildiğinde çekirdek imzalamasını ortadan kaldırmak için dosyayı açıp
aşağıdaki özellikleri aşağıda gösterildiği gibi değiştirebilirsiniz (bunların bazıları zaten default
durumda aşağıdaki gibi olabilir):

.. code-block:: text

   CONFIG_SYSTEM_TRUSTED_KEYS=""
   CONFIG_SYSTEM_REVOCATION_KEYS=""
   CONFIG_SYSTEM_TRUSTED_KEYRING=n
   CONFIG_SECONDARY_TRUSTED_KEYRING=n

   CONFIG_MODULE_SIG=n
   CONFIG_MODULE_SIG_ALL=n
   CONFIG_MODULE_SIG_KEY=""

Çekirdek imzalaması konusu daha ileride ele alınacaktır.

Derlenecek çekirdeklere yerel bir versiyon belirteci ve numarası da atanabilmektedir. Bu işlem
*"make menuconfig"* menüsünde ``General Setup/Local version - append custom release`` seçeneği
kullanılarak ya da ``.config`` dosyasında ``CONFIG_LOCALVERSION`` satırı düzenlenerek yapılabilir.
Örneğin:

.. code-block:: text

   CONFIG_LOCALVERSION="-custom"

Bu işlemle artık çekirdek sürümüne ``-custom`` sonekini eklemiş olduk.


Adım 5: Derleme
-----------------

Derleme işlemi için *make* komutu kullanılmaktadır:

.. code-block:: bash

   $ make

Eğer derleme işleminin birden fazla CPU ya da çekirdek ile yapılmasını istiyorsanız
``-j<cpu_sayısı>`` seçeneğini komuta dahil edebilirsiniz. Çalışılan sistemdeki CPU sayısının *nproc*
komutuyla elde edildiğini anımsayınız. O halde derleme için *make* komutunu şöyle kullanabiliriz:

.. code-block:: bash

   $ make -j$(nproc)

Derleme işlemi bittiğinde ürün olarak çekirdek imajı, çekirdek tarafından yüklenecek olan modül
dosyaları ve diğer bazı dosyalar elde edilmiş olur. Derleme işleminden sonra oluşturulan dosyalar
ve yerleri şöyledir (buradaki ``<çekirdek_sürümü>``, *"uname -r"* ile elde edilecek yazıyı
belirtiyor):

- **Sıkıştırılmış Çekirdek İmajı:** ``arch/<platform>/boot`` dizininde ``bzImage`` ismiyle
  oluşturulmaktadır. Denemeyi yaptığımız Intel makinede dosyanın yol ifadesi
  ``arch/x86_64/boot/bzImage`` biçimindedir. (Ancak buradaki dosya x86_64 platformu için
  ``arch/x86/boot/bzImage`` dosyasına sembolik link de yapılmış olabilir.)

- **Çekirdeğin Sıkıştırılmamış ELF İmajı:** Kaynak kök dizininde ``vmlinux`` ismiyle
  oluşturulmaktadır.

- **Çekirdek Modülleri (Aygıt Sürücü Dosyaları):** ``drivers``, ``fs`` ve ``net`` dizinlerinin
  altındaki dizinlerde bulunur. Ancak *"make modules_install"* ile bunların hepsi belirli bir
  dizine çekilebilir.

- **Çekirdek Sembol Tablosu:** Kaynak kök dizininde ``System.map`` ismiyle bulunur. Çekirdek sembol
  tablosundan yalnızca çekirdek debug edilirken faydalanılmaktadır. Bu dosya silinse bile sistemin
  çalışmasında bir sorun oluşmaz.

.. note::

   Derleme süresini uzatan en önemli etken çekirdek konfigüre edilirken seçilen modül (aygıt sürücü)
   sayısıdır. Pek çok dağıtım "belki ileride lazım olur" gerekçesiyle konfigürasyon dosyalarında
   çok sayıda modülü dahil etmektedir. Bu nedenle bir dağıtımın konfigürasyon dosyasını kullandığınız
   zaman çekirdek derlemesi uzayacaktır. Çekirdek kodlarındaki platforma özgü default konfigürasyon
   dosyaları daha minimalist biçimde oluşturulmuş durumdadır.

   Tabii çekirdek bütünsel olarak bir kez derlendikten sonra çekirdek kodlarında değişiklik yapıp
   çekirdeği yeniden derlemek istediğimizde artık derleme süresi bütünsel derleme kadar uzun
   olmayacaktır.


Adım 6: Modüllerin Kurulması
------------------------------

Farklı dizinlerde oluşturulmuş olan aygıt sürücü dosyalarını (modülleri) belli bir dizine kopyalamak
için *"make modules_install"* komutu kullanılmaktadır. Bu komut seçeneksiz kullanılırsa default olarak
``/lib/modules/<çekirdek_sürümü>`` dizinine kopyalama yapar:

.. code-block:: bash

   $ sudo make modules_install

.. note::

   Eskiden *make* işlemi çekirdek modüllerinin derlenmesini sağlamıyordu. Çekirdek modüllerinin
   derlenmesi için *"make modules"* işlemi gerekiyordu. Ancak çekirdeğin 2.6 versiyonundan itibaren
   *make* işlemi zaten çekirdek modüllerinin de derlenmesini sağlamaktadır.

Ayrıca *"make modules_install"* komutunun modül dosyalarını istediğimiz bir dizine kopyalamasını da
sağlayabiliriz. Bunun için ``INSTALL_MOD_PATH`` çevre değişkeni kullanılmaktadır. Örneğin:

.. code-block:: bash

   $ sudo INSTALL_MOD_PATH=modules make modules_install

Burada aygıt sürücü dosyaları ``/lib/modules/<çekirdek_sürümü>`` dizinine değil, bulunulan yerdeki
``modules`` dizinine kopyalanacaktır.


Adım 7: Aygıt Ağacı Dosyalarının Derlenmesi
---------------------------------------------

Eğer gömülü sistemler için derleme yapıyorsanız kaynak kod ağacında
``arch/<platform>/boot/dts`` dizini içerisindeki aygıt ağacı kaynak dosyalarını da derlemelisiniz.
Aygıt ağacı kaynak dosyalarını derlemek için *"make dtbs"* komutunu kullanabilirsiniz:

.. code-block:: bash

   $ make dtbs

Derlenmiş aygıt ağacı dosyaları ``arch/<platform>/boot/dts`` dizininde ya da bu dizinin altındaki
ilgili vendor dizininde oluşturulacaktır.

.. note::

   Aygıt ağaçları gömülü sistemlerde kullanılmaktadır. Intel tabanlı PC'lerde donanım birimlerinin
   tespit edilmesi otomatik olarak ACPI protokolü yoluyla yapıldığı için aygıt ağacı dosyaları bu
   platformda kullanılmamaktadır. Ancak ARM platformunu kullanan gömülü sistemlerde ya da BBB ve
   Raspberry Pi gibi SBC'lerde aygıt ağaçları kullanılmaktadır.


Adım 8: Kurulum
-----------------

Bizim çekirdek imajını, geçici kök dosya sistemine ilişkin dosyayı ve aygıt ağacı dosyasını ``/boot``
dizinine kopyalamamız gerekir. Ancak aslında bu işlem de *"make install"* komutuyla otomatik olarak
yapılabilmektedir. *"make install"* komutu bu dosyaları ``/boot`` dizinine kopyalamanın yanı sıra
aynı zamanda GRUB önyükleyici programın konfigürasyon dosyalarında da güncellemeler yapıp yeni
çekirdeğin GRUB menüsü içerisinde görünmesini de sağlamaktadır:

.. code-block:: bash

   $ sudo make install

Geçici Kök Dosya Sistemi (initrd)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Burada *geçici kök dosya sistemi* (*"initial ramdisk"* ya da *"initrd"*) diye bir terim kullandık.
Geçici kök dosya sistemi diskteki asıl kök dosya sistemi mount edilene kadar geçici bir süre sanki
diskteki dosya sistemiymiş gibi işlev gören bir RAM disk imajıdır. Tipik Linux sistemlerinde önce
geçici kök dosya sistemi mount edilerek temel dosyalara oradan erişilir. Sonra bu geçici dosya sistemi
RAM'den atılıp diskteki gerçek kök dosya sistemi mount edilmektedir.

Geçici kök dosya sistemine gereksinimi basit bir örnekle anlayabiliriz. Diyelim ki diske erişmekte
kullanılan aygıt sürücüsü çekirdeğin içerisine yerleştirilmemiş olsun, yani dışarıda
``lib/modules/$(uname -r)`` dizininde bir dosya biçiminde bulunuyor olsun. Şimdi çekirdeğin diske
erişebilmesi için bu aygıt sürücüye ihtiyacı olacaktır. Ancak aygıt sürücü de disktedir. İşte böyle
bir durumda bu aygıt sürücüleri de barındıran bir RAM disk dosya sistemi oluşturulmakta ve önyükleyici
tarafından (örneğin GRUB önyükleyicisi) bu dosya da RAM'e yüklenmektedir. Böylece çekirdek artık
diske erişebilir hale gelir.

.. note::

   Eğer çekirdeğin gereksinim duyacağı bütün aygıt sürücü dosyaları konfigürasyon aşamasında
   çekirdeğin içerisine gömülmüşse geçici kök dosya sistemi oluşturmadan da sistem boot edilebilir.
   Ancak bu sırada çözülmesi gereken problemlerle de karşılaşılabilmektedir. Özellikle masaüstü
   sistemlerinde geçici kök dosya sistemi olmadan sistemi boot etmek oldukça zahmetlidir.

Geçici kök dosya sistemi aynı zamanda işletim sistemini *güvenli kipte (safe mode)* açmak için ve
sistem güncellemelerinde de kullanılmaktadır.

Debian türevi dağıtımlarda geçici kök dosya sistemini oluşturmak için *"update-initramfs"* komutu
kullanılmaktadır. Bu komut da *mkinitramfs* komutunu çalıştırmaktadır. Geçici kök dosya sistemi
oluşturulurken bu komutlar işlemlerini kabaca aşağıdaki adımlarla gerçekleştirmektedir:

.. graphviz::

   digraph initramfs {
       rankdir=TB;
       graph [bgcolor="transparent", fontname="Arial", fontsize=11];
       node [shape=box, style="rounded,filled", fillcolor="#dbeafe",
             fontname="Arial", fontsize=10, margin="0.3,0.12", width=5.0];
       edge [arrowsize=0.8, color="#4a5568"];

       s1 [label="1.  Geçici çalışma dizini oluştur  (mktemp -d)"];
       s2 [label="2.  Temel dizin yapısını oluştur\n(dev, proc, sys, bin, sbin, lib, etc...)"];
       s3 [label="3.  busybox veya temel araçları kopyala"];
       s4 [label="4.  Hook'ları çalıştır  (/usr/share + /etc altındakiler)\nHer hook: ihtiyaç duyduğu binary/kütüphane/modülü geçici dizine kopyalar"];
       s5 [label="5.  Çekirdek modüllerini işle\n(initramfs.conf'taki MODULES değerine göre: most | dep | list | none)"];
       s6 [label="6.  /init script'ini yerleştir"];
       s7 [label="7.  Tüm içeriği cpio arşivi olarak paketle"];
       s8 [label="8.  Belirtilen algoritmayla sıkıştır  (gzip / lz4 / xz / zstd)"];
       s9 [label="/boot/initrd.img-<kernel-version> olarak yaz",
           fillcolor="#bbf7d0"];

       s1 -> s2 -> s3 -> s4 -> s5 -> s6 -> s7 -> s8 -> s9;
   }

*"make install"* komutu masaüstü sistemlerde sırasıyla şunları yapmaktadır:

- ``arch/<platform>/boot`` dizinindeki ``bzImage`` çekirdek imajı alınarak hedef ``/boot`` dizinine
  ``vmlinuz-<çekirdek_sürümü>`` ismiyle kopyalanır.
- ``System.map`` dosyası hedef ``/boot`` dizinine ``System.map-<çekirdek_sürümü>`` ismiyle kopyalanır.
- ``.config`` dosyası ``/boot`` dizinine ``config-<çekirdek_sürümü>`` ismiyle kopyalanır.
- Geçici kök dosya sistemine ilişkin dosya oluşturulur ve hedef ``/boot`` dizinine
  ``initrd.img-<çekirdek_sürümü>`` ismiyle kopyalanır.
- Eğer GRUB önyükleyicisi kullanılıyorsa GRUB konfigürasyonu güncellenir ve GRUB menüsüne yeni
  girişler eklenir.

Böylece sistemin otomatik olarak yeni çekirdekle açılması sağlanır.

*"make install"* komutu uygulandığında eğer çekirdeğin versiyon bilgisi aynı ise ``/boot``
dizinindeki bir önceki kurulumun dosyaları ``.old`` uzantısıyla saklanmaktadır. Böylece son
*"make install"* komutundan önceki kuruluma manuel olarak geri dönebilirsiniz. Örneğin yeniden
aynı çekirdek versiyonunu *"make install"* yaptığımızda ``/boot`` dizininin içeriği şöyle
olacaktır:

.. code-block:: text

   kaan@kaan-Huawei:~/Study/LinuxKernel/linux-6.9.2$ ls -l /boot
   total 655480
   -rw-r--r-- 1 root root    287375 Haz  7  2024 config-6.8.0-38-generic
   -rw-r--r-- 1 root root    287766 Ağu 15 11:57 config-6.9.2-custom
   -rw-r--r-- 1 root root    287766 Ağu 15 11:55 config-6.9.2-custom.old
   drwx------ 3 root root      4096 Oca  1  1970 efi
   drwxr-xr-x 6 root root      4096 Ağu 15 11:57 grub
   lrwxrwxrwx 1 root root        23 Ağu 10 11:20 initrd.img -> initrd.img-6.9.2-custom
   -rw-r--r-- 1 root root  73052139 Kas 19  2024 initrd.img-6.8.0-38-generic
   -rw-r--r-- 1 root root 526888758 Ağu 15 11:57 initrd.img-6.9.2-custom
   -rw------- 1 root root   9055262 Haz  7  2024 System.map-6.8.0-38-generic
   -rw-r--r-- 1 root root   8365115 Ağu 15 11:57 System.map-6.9.2-custom
   -rw-r--r-- 1 root root   8365115 Ağu 15 11:55 System.map-6.9.2-custom.old
   lrwxrwxrwx 1 root root        20 Ağu 15 11:57 vmlinuz -> vmlinuz-6.9.2-custom
   -rw-r--r-- 1 root root  14944648 Haz  7  2024 vmlinuz-6.8.0-38-generic
   -rw-r--r-- 1 root root  14819840 Ağu 15 11:57 vmlinuz-6.9.2-custom
   -rw-r--r-- 1 root root  14819840 Ağu 15 11:55 vmlinuz-6.9.2-custom.old
   lrwxrwxrwx 1 root root        24 Ağu 15 11:57 vmlinuz.old -> vmlinuz-6.9.2-custom.old

.. note::

   *"make install"* komutu masaüstü sistemler için kullanılmaktadır. Gömülü sistemlerde tüm
   dosyaların toparlanıp hedef sisteme aktarılması gerekir. Gömülü sistemlerde *"make install"*
   tarafından yapılan işlemleri siz manuel bir biçimde yapabilirsiniz. Tabii gömülü sistemlerde
   GRUB önyükleyicisi yerine ağırlıklı olarak *U-Boot* denilen önyükleyici kullanılmaktadır.
   Dolayısıyla gömülü sistemlerde sistemin yeni çekirdekle açılmasını sağlamak için *U-Boot*
   önyükleyicisini de ayarlamanız gerekecektir.


make modules_install Komutu Detayları
=======================================

*"make modules_install"* komutu yalnızca modül dosyalarını hedef dizine kopyalamakla kalmaz; aynı
zamanda bazı dosyaları da oluşturup onları da hedef dizine kopyalar. Hedef dizinin default
``/lib/modules/<çekirdek_sürümü>`` dizini olduğu varsayımıyla komut sırasıyla şunları yapmaktadır:

- Modül dosyalarını ``/lib/modules/<çekirdek_sürümü>`` dizinine kopyalar.
- ``modules.dep`` isimli dosyayı oluşturur ve bunu ``/lib/modules/<çekirdek_sürümü>`` dizinine
  kopyalar.
- ``modules.alias`` isimli dosyayı oluşturur ve bunu ``/lib/modules/<çekirdek_sürümü>`` dizinine
  kopyalar.
- ``modules.order`` isimli dosyayı oluşturur ve ``/lib/modules/<çekirdek_sürümü>`` dizinine kopyalar.
- ``modules.builtin`` isimli dosyayı ``/lib/modules/<çekirdek_sürümü>`` dizinine kopyalar.

Aslında burada oluşturulan dosyaların bazıları mutlak anlamda bulundurulmak zorunda değildir. Ancak
sistemin öngörüldüğü gibi işlev göstermesi için bu dosyaların ilgili dizinde bulundurulması uygundur.


modules.dep
-----------

Bir aygıt sürücü başka aygıt sürücüleri de kullanıyor olabilir. Yani bir aygıt sürücünün
çalışabilmesi için başka aygıt sürücülerin de yüklü olması gerekebilmektedir. İşte ``modules.dep``
dosyası bir aygıt sürücünün yüklenmesi için başka hangi aygıt sürücülerin yüklenmesi gerektiği
bilgisini tutmaktadır. ``modules.dep`` bir text dosyadır. Satırların içeriği şöyledir:

.. code-block:: text

   <modül_yolu>: <bağımlılık1> <bağımlılık2> ...

Dosyanın içeriğine örnek verebiliriz:

.. code-block:: text

   kernel/arch/x86/crypto/nhpoly1305-sse2.ko.zst: kernel/crypto/nhpoly1305.ko.zst kernel/lib/crypto/libpoly1305.ko.zst
   kernel/arch/x86/crypto/nhpoly1305-avx2.ko.zst: kernel/crypto/nhpoly1305.ko.zst kernel/lib/crypto/libpoly1305.ko.zst
   kernel/arch/x86/crypto/curve25519-x86_64.ko.zst: kernel/lib/crypto/libcurve25519-generic.ko.zst

Eğer bu ``modules.dep`` dosyası olmazsa *modprobe* komutu çalışmaz ve çekirdek modülleri yüklenirken
eksik yükleme yapılabilir. Dolayısıyla sistem düzgün bir biçimde çalışmayabilir. Eğer bu dosya
elimizde yoksa ya da bir biçimde silinmişse *"depmod -a"* komutu ile yeniden oluşturulabilir:

.. code-block:: bash

   $ sudo depmod -a

Siz yüklü olan başka bir çekirdek sürümü için ``modules.dep`` dosyasını oluşturmak istiyorsanız
çekirdek sürümünü de argüman olarak vermelisiniz:

.. code-block:: bash

   $ sudo depmod -a <çekirdek_sürümü>

.. note::

   *depmod* komutunun çalışabilmesi için ``/lib/modules/<çekirdek_sürümü>`` dizininde modül
   dosyalarının bulunuyor olması gerekir. Çünkü bu komut bu dizindeki modül dosyalarını tek tek bulup
   ELF formatının ilgili bölümlerine bakarak modülün hangi modülleri kullandığını tespit ederek
   ``modules.dep`` dosyasını oluşturmaktadır.


modules.alias
--------------

``modules.alias`` dosyası belli bir isim ya da id ile aygıt sürücü dosyasını eşleştiren bir text
dosyadır. Bu dosyanın bulunmaması bazı durumlarda sorunlara yol açmayabilir. Ancak örneğin USB porta
bir aygıt takıldığında bu aygıta ilişkin aygıt sürücünün hangisi olduğu bilgisi bu dosyada
tutulmaktadır. Bu durumda bu dosyanın olmayışı aygıt sürücünün yüklenememesine neden olabilir.
Dosyanın içeriği aşağıdaki formata uygun satırlardan oluşmaktadır:

.. code-block:: text

   alias <tanımlayıcı> <modül_adı>

Örnek bir içerik:

.. code-block:: text

   alias usb:v05ACp*d*dc*dsc*dp*ic*isc*ip*in* apple_mfi_fastcharge
   alias usb:v8086p0B63d*dc*dsc*dp*ic*isc*ip*in* usb_ljca
   alias usb:v0681p0010d*dc*dsc*dp*ic*isc*ip*in* idmouse
   alias usb:v0681p0005d*dc*dsc*dp*ic*isc*ip*in* idmouse
   alias usb:v07C0p1506d*dc*dsc*dp*ic*isc*ip*in* iowarrior
   alias usb:v07C0p1505d*dc*dsc*dp*ic*isc*ip*in* iowarrior

Bu dosya silinirse yine *"depmod -a"* komutu ile oluşturulabilir.


modules.order
--------------

``modules.order`` dosyası aygıt sürücü dosyalarının yüklenme sırasını barındıran bir text dosyadır.
Bu dosyanın her satırında bir çekirdek aygıt sürücüsünün dosya yol ifadesi bulunur. Daha önce
yazılmış aygıt sürücüler daha sonra yazılanlardan daha önce yüklenir. Bu dosyanın olmaması genellikle
bir soruna yol açmaz. Ancak modüllerin belli sırada yüklenmemesi bazı durumlarda bozukluklara da
neden olabilmektedir. Bu dosyanın silinmesi durumunda yine *"depmod -a"* komutuyla oluşturulabilmektedir.


.. rubric:: ── 7. Ders · 09 Ağustos 2025, Cumartesi ──

Manuel Kurulum
===============

Biz *"make install"* komutu ile yapılan işlemleri manuel olarak da yapabiliriz. Aslında çekirdek
imajı ve geçici kök dosya sistemi dosyaları default yerlerin dışında başka yerlerde de
bulundurulabilir; önyükleyiciye bu konuda bilgi verilebilir. Ancak yukarıdaki dosyaların hedef
sistemde bulundurulduğu default yerler şöyledir:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Dosya
     - Hedef Dizin
   * - Çekirdek İmajı
     - ``/boot``
   * - Çekirdek Sembol Tablosu
     - ``/boot``
   * - Modül Dosyaları
     - ``/lib/modules/<çekirdek_sürümü>/kernel``
   * - Geçici Kök Dosya Sistemi Dosyası
     - ``/boot``

İsteğe bağlı olarak aşağıdaki dosyalar da hedef sisteme konuşlandırılabilir:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Dosya
     - Hedef Dizin
   * - Konfigürasyon Dosyası
     - ``/boot``
   * - Modüllere İlişkin Bazı Dosyalar
     - ``/lib/modules/<çekirdek_sürümü>``

Peki yukarıda belirttiğimiz dosyalar hedef sistemdeki ilgili dizinlere hangi isimlerle
kopyalanmalıdır? Tipik isimlendirme şöyle olmalıdır (buradaki ``<çekirdek_sürümü>``, *"uname -r"*
komutuyla elde edilecek olan yazıdır):

- **Çekirdek İmajı:** ``/boot/vmlinuz-<çekirdek_sürümü>`` — örneğin ``vmlinuz-6.9.2-custom``
- **Çekirdek Sembol Tablosu:** ``/boot/System.map-<çekirdek_sürümü>`` — örneğin
  ``System.map-6.9.2-custom``
- **Modüllere İlişkin Dosyalar:** ``/lib/modules/<çekirdek_sürümü>`` dizininin içerisine
- **Konfigürasyon Dosyası:** ``/boot/config-<çekirdek_sürümü>`` — örneğin ``config-6.9.2-custom``
- **Geçici Kök Dosya Sistemi:** ``/boot/initrd.img-<çekirdek_sürümü>`` — örneğin
  ``initrd.img-6.9.2-custom``; *"update-initramfs"* programıyla oluşturulabilir.

Ayrıca bazı dağıtımlarda ``/boot`` dizini içerisindeki ``vmlinuz`` dosyası default olan
``vmlinuz-<çekirdek_sürümü>`` dosyasına, ``initrd.img`` dosyası da
``/boot/initrd.img-<çekirdek_sürümü>`` dosyasına sembolik link yapılmış durumda olabilir. Ancak bu
sembolik bağlantıları GRUB kullanmamaktadır. Aşağıda Intel sistemindeki 6.8.0 çekirdeğinin yüklü
olduğu ``/boot`` dizininin default içeriğini görüyorsunuz:

.. code-block:: text

   $ ls -l /boot
   -rw-r--r-- 1 root root    287375 Haz  7  2024 config-6.8.0-38-generic
   drwx------ 3 root root      4096 Oca  1  1970 efi
   drwxr-xr-x 6 root root      4096 Ağu 15 11:57 grub
   lrwxrwxrwx 1 root root        23 Ağu 10 11:20 initrd.img -> initrd.img-6.8.0-38-generic
   -rw-r--r-- 1 root root  73052139 Kas 19  2024 initrd.img-6.8.0-38-generic
   -rw------- 1 root root   9055262 Haz  7  2024 System.map-6.8.0-38-generic
   lrwxrwxrwx 1 root root        20 Ağu 15 11:57 vmlinuz -> vmlinuz-6.8.0-38-generic
   -rw-r--r-- 1 root root  14944648 Haz  7  2024 vmlinuz-6.8.0-38-generic

Geçici kök dosya sisteminin içerisindeki dosyalar *cpio* denilen bir arşiv formatıyla
arşivlenmektedir. *cpio* arşivi tıpkı *tar* arşivinde olduğu gibi yalnızca dosyaların uç uca
eklenmesiyle oluşturulmaktadır. İsterseniz geçici kök dosya sistemine ilişkin ``initrd-xxx``
dosyalarını açabilirsiniz. Ancak bu dosyaların içeriği dağıtımların versiyonlarına göre
değişebilmektedir. Yeni dağıtımlarda bu ``initrd-xxx`` arşiv dosyası birkaç bölümden oluşmaktadır.
Eğer biz bu dosyayı *cpio* programıyla açmaya çalışırsak bu program yalnızca ilk bölümü açacaktır.
Tüm bölümleri açmak için *unmkinitramfs* programından faydalanabilirsiniz:

.. code-block:: bash

   unmkinitramfs /boot/initrd.img-6.9.2-custom initrd

Bu komutla geçici kök dosya sistemine ilişkin arşiv dosyası ``initrd`` isimli dizinin altına
açılacaktır.


Çekirdek Sürüm Yazısının Belirlenmesi
---------------------------------------

Derleme sonucunda elde ettiğimiz dosyaları manuel isimlendirirken çekirdek sürüm yazısını nasıl
bileceğiz? Bunun için *"uname -r"* komutunu kullanamayız. Çünkü bu komut bize o anda çalışmakta
olan çekirdeğin sürüm yazısını verir. Sürüm yazısı çekirdek imajının içerisine de yazılmaktadır ve
bizim bazı dosyalara verdiğimiz isimlerin çekirdek içerisindeki bu yazıyla uyumlu olması gerekir.

Default olarak ``kernel.org`` sitesinden indirilen kaynak kodlar derlendiğinde çekirdek sürümü
``6.9.2`` gibi üç haneli bir sayılardan oluşmaktadır. Yani yazının sonunda ``-generic`` ya da
``-custom`` gibi sonekler yoktur. Tabii çekirdeği derlemeden önce ``.config`` dosyasında
``CONFIG_LOCALVERSION`` özelliğine bu sürüm numarasından sonra eklenecek bilgiyi girebilirsiniz.

Sürüm yazısını bulmak için sıkıştırılmamış çekirdek dosyası içerisindeki (kaynak kök dizindeki
``vmlinux`` dosyası) string tablosunda ``Linux version`` yazısını aramak yeterlidir:

.. code-block:: bash

   $ strings vmlinux | grep "Linux version"
   Linux version 6.9.2-custom (kaan@kaan-virtual-machine) (gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0,
   GNU ld (GNU Binutils for Ubuntu) 2.38) # SMP PREEMPT_DYNAMIC
   Linux version 6.9.2-custom (kaan@kaan-virtual-machine) (gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0,
   GNU ld (GNU Binutils for Ubuntu) 2.38) #2 SMP PREEMPT_DYNAMIC Thu Dec 5 17:55:14 +03 2024

Buradan sürüm yazısının ``6.9.2-custom`` olduğu görülmektedir. O halde derleme sonucunda elde
ettiğimiz dosyaları manuel biçimde kopyalarken sürüm bilgisi olarak ``6.9.2-custom`` yazısını
kullanmamız gerekir. Çekirdek imajının ``/boot`` dizinine manuel kopyalanması işlemi şöyle
yapılabilir (kaynak kök dizinde bulunduğumuzu varsayıyoruz):

.. code-block:: bash

   $ sudo cp arch/x86_64/boot/bzImage /boot/vmlinuz-6.9.2-custom
   $ sudo cp .config /boot/config-6.9.2-custom

.. note::

   Çekirdek modüllerinin kopyalanması biraz zahmetli bir işlemdir çünkü bunlar derlediğimiz
   çekirdekte farklı dizinlerde bulunmaktadır. Bu kopyalamanın en etkin yolu *"make modules_install"*
   komutunu kullanmaktır. Benzer biçimde çekirdek dosyalarının ve gerekli diğer dosyaların uygun
   yerlere kopyalanması için de en etkin yöntem *"make install"* komutudur.


GRUB Yapılandırması
=====================

Normal olarak *"make install"* yaptığımızda eğer sistemimizde GRUB önyükleyicisi varsa komut GRUB
konfigürasyon dosyalarında da güncellemeler yaparak sistemin yeni çekirdekle açılmasını sağlamaktadır.
Böylece kullanıcı bir menü yoluyla sistemin kendi istediği çekirdekle açılmasını da sağlayabilmektedir.
GRUB menüsü otomatik olarak görüntülenmemektedir. Boot işlemi sırasında ESC tuşuna basılırsa menü
görüntülenir. Eğer GRUB menüsünün her zaman görüntülenmesi isteniyorsa ``/etc/default/grub``
dosyasındaki iki satır aşağıdaki gibi değiştirilmelidir:

.. code-block:: text

   GRUB_TIMEOUT_STYLE=menu
   GRUB_TIMEOUT=5

Buradaki ``GRUB_TIMEOUT`` satırı eğer müdahale yapılmamışsa menünün en fazla 5 saniye
görüntüleneceğini belirtmektedir.

Bu işlemden sonra *update-grub* programı da çalıştırılmalıdır:

.. code-block:: bash

   $ sudo update-grub

Bu tür denemeler yapılırken GRUB menüleri bozulabilmektedir. Düzeltme işlemleri bazı konfigürasyon
dosyalarının düzenlenmesiyle manuel biçimde yapılabilir. Konfigürasyon dosyaları güncellendikten
sonra *update-grub* programı mutlaka çalıştırılmalıdır. Ancak eğer GRUB konfigürasyon dosyaları
konusunda yeterli bilgiye sahip değilseniz GRUB işlemlerini görsel bir biçimde *grub-customizer*
isimli programla da yapabilirsiniz. Bu program Debian depolarında olmadığı için önce aşağıdaki gibi
programın bulunduğu yerin ``apt`` kayıtlarına eklenmesi gerekmektedir:

.. code-block:: bash

   $ sudo add-apt-repository ppa:danielrichter2007/grub-customizer
   $ sudo apt-get update
   $ sudo apt-get install grub-customizer


Çekirdek Derleme Süreci Özeti
================================

Yukarıdaki adımların özeti şöyledir:

1. Çekirdek derlemesi için gerekli olan araçlar kurulur.
2. Çekirdek kodları indirilir ve açılır.
3. Zaten hazır olan konfigürasyon dosyası ``/boot`` dizininden alınarak ``.config`` ismiyle kaynak
   kök dizine kopyalanır.
4. Konfigürasyon dosyası üzerinde *"make menuconfig"* komutu ile değişiklikler yapılır.
5. Eğer çekirdeğin imzalanması istenmiyorsa ``.config`` dosyasındaki ilgili satırlar üzerinde
   değişiklikler yapılır.
6. Çekirdek derlemesi *"make -j$(nproc)"* komutu ile gerçekleştirilir.
7. Modüller ve ilgili dosyalar hedefe *"sudo make modules_install"* komutu ile konuşlandırılır.
8. Çekirdek imajı ve ilgili dosyalar masaüstü sistemlerde *"sudo make install"* komutu ile hedefe
   konuşlandırılır.


Çekirdeğin Sistemden Kaldırılması
====================================

Yeni çekirdeği derleyip sisteme dahil ettikten sonra onu sistemden tamamen çıkartmak için yapılan
işlemlerin tersini yapmak gerekir. Kaldırma işlemi manuel biçimde şöyle yapılabilir:

- ``/lib/modules/<çekirdek_sürümü>`` dizini tamamen silinir.
- ``/boot`` dizinindeki çekirdek sürümüne ilişkin dosyalar silinir.
- ``/boot`` dizininden çekirdek sürümüne ilişkin dosyalar silindikten sonra *update-grub* programı
  ``sudo`` ile çalıştırılmalıdır. Bu program ``/boot`` dizinini inceleyip otomatik olarak ilgili
  girişleri GRUB menüsünden siler. Yani aslında GRUB konfigürasyon dosyaları üzerinde manuel
  değişiklik yapmaya gerek yoktur.

.. note::

   *grub-customizer* programı ile de görsel silme yapılabilir. Ancak bu program ``/boot`` dizini
   içerisindeki dosyaları ve modül dosyalarını silmez; yalnızca ilgili girişleri GRUB menüsünden
   çıkartmaktadır.
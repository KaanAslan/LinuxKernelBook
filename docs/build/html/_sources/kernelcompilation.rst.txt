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


make modules_install Komutu ile İlgili Ayrıntılar 
=================================================

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

Çekirdek Kodları Üzerinde Değişiklik Yapma Yöntemleri
======================================================

Çekirdeği yeniden derlemenin gerekçelerinden bahsetmiştik. Bunlardan biri de çekirdek kodları üzerinde
değişikliklerin yapılmış olmasıydı. Peki çekirdek kodları üzerinde değişiklikler nasıl yapılabilir?
Çekirdek kodları üzerinde değişiklikler tipik olarak dört yolla yapılmaktadır:

1. Çekirdek kodlarındaki zaten var olan bir dosya içerisinde bulunan fonksiyon kodlarında değişiklik
   yapılması.
2. Çekirdek kodlarındaki zaten var olan bir dosya içerisine yeni bir fonksiyon eklenmesi.
3. Çekirdek kodlarındaki bir dizin içerisine yeni bir C kaynak dosyası eklenmesi.
4. Çekirdek kodlarındaki bir dizin içerisine yeni bir dizin ve bu dizinin içerisine de çok sayıda C
   kaynak dosyalarının eklenmesi.

Eğer biz birinci ve ikinci maddedeki gibi çekirdek kodlarına yeni bir dosya eklemiyorsak çekirdeğin
derlenmesini sağlayan make dosyalarında bir değişiklik yapmamıza gerek yoktur. Ancak çekirdeğe yeni bir
kaynak dosya ya da dizin ekleyeceksek bu eklemeyi yaptığımız dizindeki make dosyasında izleyen paragraflarda
açıklayacağımız biçimde bazı güncellemelerin yapılması gerekir. Böylece çekirdek yeniden derlendiğinde bu
dosyalar da çekirdek imajının içerisine eklenmiş olacaktır. Eğer kaynak kod ağacında bir dizinin altına yeni
bir dizin eklemek istiyorsak bu durumda o dizini yine üst dizine ilişkin make dosyasında belirtmemiz ve o
dizinde ayrı bir ``Makefile`` dosyası oluşturmamız gerekir.


KBuild Sistemi ve GNU Make
===========================

GNU Make aracı oldukça ayrıntılı özelliklere sahip bir build aracıdır. Bu aracın ayrıntılarını öğrenmek
ayrı bir çabayı gerektirmektedir. Make dili aslında oldukça aşağı seviyeli bir build dilidir. Bu nedenle
özellikle son yirmi yıldır programcılar doğrudan GNU Make aracını kullanmak yerine daha üst düzey make
araçlarını kullanmayı tercih etmektedir. Bunlardan en yaygın olanlardan biri *CMake* denilen araçtır.
Microsoft ise *MSBuild* isimli kendi tasarladığı build aracını kullanmaktadır.

Make dilinde değişkenler oluşturulabilmektedir. Örneğin:

.. code-block:: makefile

   obj-y = a.o

Burada ``obj-y`` isimli değişken ``a.o`` bilgisini tutmaktadır. Değişkenleri bir çeşit makro gibi
düşünebilirsiniz. Bir değişkene ekleme yapmak için Make dilinde ``+=`` operatörü kullanılmaktadır. Örneğin:

.. code-block:: makefile

   obj-y = a.o
   obj-y += b.o
   obj-y += c.o

Burada artık ``obj-y`` değişkeni ``a.o b.o c.o`` biçiminde olacaktır.

Linux çekirdeğinde özyinelemeli bir make yöntemi kullanılmaktadır. Her dizinde bir ``Makefile`` dosyası
vardır. Bunun içerisindeki ``obj-y`` gibi, ``obj-m`` gibi bazı değişkenler ``+=`` operatörüyle eklenerek
biriktirilmektedir. Bunlar da derleme ve bağlama işlemine sokulmaktadır. Yukarıda da belirttiğimiz gibi
Linux'taki bu build sistemine *KBuild* ya da *KConfig* sistemi denilmektedir.

Bizim Linux'ta ``Makefile`` dosyaları üzerinde gerekli güncellemeleri yapmak için çok fazla bilgiye sahip
olmamız gerekmez. Bazı yönergeleri uygun bir biçimde yerine getirirsek hedefimize ulaşabiliriz.


Makefile Dosyalarının Güncellenmesi
=====================================

Linux kaynak kod ağacında dizinlerin altında ``Makefile`` isimli make dosyaları bulunur. Eğer bir dizinin
altına yeni bir dosya eklenecekse o dizinin içerisinde bulunan ``Makefile`` dosyasının içerisine aşağıdaki
gibi bir satırın eklenmesi gerekir:

.. code-block:: makefile

   obj-y += dosya_ismi.o

Buradaki ``+=`` operatörü ``obj-y`` isimli hedefe ekleme yapma anlamına gelmektedir. ``obj`` sözcüğünün
yanındaki ``-y`` harfi ilgili dosyanın çekirdeğin bir parçası biçiminde çekirdek imajının içerisine
gömüleceğini belirtmektedir. Make dosyalarının bazı satırlarında ``obj-y`` yerine ``obj-m`` de görebilirsiniz.
Bu da ilgili dosyanın ayrı bir modül biçiminde derleneceği anlamına gelmektedir. Eklemeler genellikle
çekirdek imajının içine yapıldığı için biz de genellikle ``obj-y`` kullanırız. Eğer bir dosyanın (aygıt
sürücüler için bu durum söz konusudur) çekirdek imajının içine gömülmesi yerine ayrı bir çekirdek modülü
olarak derlenmesi isteniyorsa bu durumda dosyanın yerleştirildiği dizinin ``Makefile`` dosyasına aşağıdaki
gibi bir eklemenin yapılması gerekir:

.. code-block:: makefile

   obj-m += dosya_ismi.o

Eğer çekirdek kaynak kodlarına tümden bir dizinin eklenmesi isteniyorsa bu durumda önce o dizinin
oluşturulduğu dizindeki ``Makefile`` dosyasına aşağıdaki gibi bir satır eklenmelidir (dizin isminden
sonra ``/`` karakterini unutmayınız):

.. code-block:: makefile

   obj-y += dizin_ismi/

Tabii bu ekleme bir modül biçiminde de olabilirdi:

.. code-block:: makefile

   obj-m += dizin_ismi/

Fakat bu ekleme tek başına yetmemektedir. Bu ekleme yapıldıktan sonra ayrıca yaratılan dizinde ``Makefile``
isimli bir dosyanın oluşturulması ve o dosyanın içerisinde o dizindeki kaynak dosyaların da belirtilmesi
gerekmektedir. Örneğin biz ``drivers`` dizininin altında ``mydriver`` isimli bir dizin oluşturup onun da
içerisine ``a.c``, ``b.c`` ve ``c.c`` dosyalarını eklemiş olalım. Bu durumda önce ``drivers`` dizini
içerisindeki ``Makefile`` dosyasına aşağıdaki gibi bir satır ekleriz:

.. code-block:: makefile

   obj-y += mydriver/

Sonra da ``mydriver`` dizini içerisinde ``Makefile`` isimli bir dosya oluşturup bu dosyanın içerisinde
de dizin içerisindeki dosyaları belirtiriz. Örneğin:

.. code-block:: makefile

   obj-y += a.o
   obj-y += b.o
   obj-y += c.o


Kconfig Dosyaları
==================

Kaynak kod ağacında ``Makefile`` dosyasının dışında build sistemiyle ilgili ``Kconfig`` isimli dosyalar
da bulunmaktadır. Bu dosyaların içerisinde ilgili dosyaların ya da dizinlerin konfigürasyon dosyasına
yansıtılması için gerekli bilgiler bulundurulmaktadır. Örneğin biz eklediğimiz ``mydriver`` dizinindeki
dosyaların çekirdek kodlarına dahil edilip edilmeyeceğini çekirdeği derleyenin konfigürasyon aşamasında
belirlemesini sağlayabiliriz. Bunun için bu ``Kconfig`` dosyasına bir giriş eklememiz gerekir. Böylece
bu giriş de *"make menuconfig"* yapıldığında bir seçenek olarak karşımıza gelecektir. Tabii ekleyeceğimiz
dosya ve dizinleri ``Kconfig`` dosyasında belirtmek zorunda değiliz.

*"make menuconfig"* menüsünde seçenekler için birkaç seçme biçimi bulunmaktadır:

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Gösterim
     - Anlamı
   * - ``[ ]``
     - Seçilebilir ya da seçilmeyebilir. Seçildiğinde ``[*]`` biçiminde gösterilir.
   * - ``< >``
     - Üç konumlu seçenek: boş (seçilmedi), ``<M>`` (modül) ya da ``<*>`` (çekirdek içine gömülü).
   * - ``-*-``
     - Seçilememezlik yapılamaz; ilgili özellik mutlaka çekirdek kodlarında bulunmalıdır.
   * - değer
     - İlgili özellik için doğrudan bir değer girilmektedir.

Tabii *"make menuconfig"* menüsünde yapılan her şey aslında ``.config`` dosyasına yansıtılmaktadır.


Konfigürasyon Seçeneklerinin Kaynak Kodlara Yansıtılması
==========================================================

Peki çekirdeğin konfigüre edilmesi aşamasında *"make menuconfig"* işleminde belirlediğimiz seçenekler
kaynak kodlara nasıl yansıtılmaktadır? Örneğin biz *"make menuconfig"* işleminde bir modülün çekirdek
kodlarına dahil edilmesini ilgili girişi ``*`` ile seçerek sağlayabilmekteyiz. Benzer biçimde biz
konfigürasyon aşamasında bazı çekirdek parametrelerini de değiştirebilmekteyiz. Örneğin *timer tick*
frekansı *"make menuconfig"* menüsünde bir sayı biçiminde belirlenebilmektedir. Peki buradaki belirlemeler
çekirdek kodlarına ve build sistemine nasıl yansıtılmaktadır?

Anımsanacağı gibi *"make menuconfig"* ve diğer config menülerinde yapılan seçimler ``.config`` isimli
bir metin dosyaya kaydedilmektedir. Bu ``.config`` dosyası *özellik=değer* biçiminde satırlardan
oluşmaktadır. Aşağıda dosyanın birkaç satırını görüyorsunuz:

.. code-block:: text

   CONFIG_CC_HAS_ASM_INLINE=y
   CONFIG_CC_HAS_NO_PROFILE_FN_ATTR=y
   CONFIG_PAHOLE_VERSION=125
   CONFIG_IRQ_WORK=y
   CONFIG_BUILDTIME_TABLE_SORT=y
   CONFIG_THREAD_INFO_IN_TASK=y

Çekirdek derlenirken ilk aşamada bu ``.config`` dosyasının içeriği
``include/generated/autoconf.h`` dosyasının içerisine ``#define`` önişlemci komutları biçiminde
aktarılmaktadır. Eğer ilgili konfigürasyon dosyasındaki değer ``y`` ya da ``m`` ise bu ``autoconf.h``
dosyası içerisinde buna ilişkin sembolik sabit 1 olarak görünür. (Başka bir deyişle *"make menuconfig"*
menüsünde ``[*]`` ya da ``<*>`` ya da ``<M>`` seçenekleri için sembolik sabit 1 olur.) Eğer konfigürasyon
dosyasında ilgili seçenek gerçekten bir değer belirtiyorsa ``autoconf.h`` dosyası içerisinde bu sembolik
sabit o değerde olur. Eğer konfigürasyon dosyasında ilgili seçenek ``n`` biçiminde seçilmişse (yani
*"make menuconfig"* menüsünde ilgili seçenek ``[ ]`` ya da ``< >`` biçiminde seçilmişse) bu durumda
ilgili sembolik sabit hiç ``#define`` edilmemiş hale gelir.

Özetle aslında ``.config`` dosyası içerisindeki satırlardan C dilinde anlamlı olan ``#define`` önişlemci
komutları oluşturulmaktadır. Aşağıda üretilmiş olan ``autoconf.h`` dosyasının birkaç satırını görüyorsunuz:

.. code-block:: c

   #define CONFIG_IGB_HWMON 1
   #define CONFIG_ACPI_HOTPLUG_CPU 1
   #define CONFIG_DEV_DAX_KMEM_MODULE 1
   #define CONFIG_RIONET_RX_SIZE 128
   #define CONFIG_USB_SERIAL_KEYSPAN_PDA_MODULE 1
   #define CONFIG_BOOTTIME_TRACING 1

Çekirdeğe ilişkin bir C kodu içerisinde "ilgili seçenek seçilmişse" bir kod parçasını derlemeye dahil
etmek için ``#ifdef`` önişlemci komutundan faydalanabilirsiniz. Örneğin:

.. code-block:: c

   #ifdef CONFIG_XXX
   ...
   #endif

Tabii üretilen bu ``autoconf.h`` dosyası çekirdek kaynak kodlarındaki çeşitli başlık dosyalarında
doğrudan ya da dolaylı bir biçimde eklenmiş durumdadır. Linux kaynak kodları da bu sembolik sabitleri
kullanacak biçimde yazılmıştır. Linux'un kaynak kodlarında ``autoconf.h`` dosyasını bulamazsınız.
Çünkü bu dosya make işlemi sırasında oluşturulmaktadır.


Konfigürasyon Seçeneklerinin Makefile Dosyalarına Yansıtılması
================================================================

Biz yukarıdaki paragrafta ``.config`` dosyasındaki konfigürasyon parametrelerinin nasıl C'ye sembolik
sabitler biçiminde yansıtıldığını gördük. Peki bu konfigürasyon seçenekleri ``Makefile`` dosyalarına
nasıl yansıtılmaktadır? Aşağıda çekirdeğin bir ``Makefile`` içeriğini görüyorsunuz:

.. code-block:: makefile

   obj-$(CONFIG_I8254)             += i8254.o
   obj-$(CONFIG_104_QUAD_8)        += 104-quad-8.o
   obj-$(CONFIG_INTERRUPT_CNT)     += interrupt-cnt.o
   obj-$(CONFIG_RZ_MTU3_CNT)       += rz-mtu3-cnt.o
   obj-$(CONFIG_STM32_TIMER_CNT)   += stm32-timer-cnt.o

Bu satırlar aslında "ilgili konfigürasyon seçenekleri seçilmişse ilgili dosyaların derlemeye dahil
edileceğini" belirtmektedir.

İşte *KBuild* sistemi aynı zamanda bu ``.config`` dosyasından hareketle make programı için anlamlı
olan değişkenler de oluşturmaktadır. Bu değişkenleri yukarıda açıkladığımız sembolik sabitlerle
karıştırmayınız. Bu değişkenler make dili için anlamlı olan make dilinin değişkenleridir. Örneğin eğer
``.config`` dosyasında bir seçenek ``y`` olarak belirtilmişse (başka bir deyişle *"make menuconfig"*
menüsünde seçenek ``[*]`` ya ``<*>`` biçiminde seçilmişse) bu konfigürasyon seçeneği için make dilinde
``y`` değeri, eğer ``m`` olarak belirtilmişse de (başka bir deyişle *"make menuconfig"* menüsünde
seçenek ``<M>`` biçiminde seçilmişse) ``m`` değeri oluşturulmaktadır.

Böylece aslında yukarıdaki make satırları ilgili seçenek ``y`` olarak seçilmişse ``obj-y`` biçimine,
``m`` olarak seçilmişse ``obj-m`` biçimine dönüştürülmektedir. Örneğin:

.. code-block:: makefile

   obj-$(CONFIG_I8254) += i8254.o

Burada ``CONFIG_I8254`` seçeneği ``y`` ise ilgili dosya ``obj-y`` değişkenine dahil olacaktır. Yani
çekirdeğin içerisinde bulunacaktır. Ancak bu ``CONFIG_I8254`` seçeneği ``m`` ise ilgili dosya ``obj-m``
değişkenine dahil olacaktır. Eğer bu seçenek ``n`` ise (yani hiç seçilmemişse) çekirdek build sistemi
ya bu ``CONFIG_I8254`` değişkenini hiç tanımlamamakta ya da bunu ``n`` olarak tanımlamaktadır. Her iki
durumda da artık bu dosya herhangi bir biçimde derlemeye dahil edilmeyecektir.

Çekirdeğe birtakım kodlar ekleyenler eğer eklemeleri ``Kconfig`` dosyası yoluyla konfigürasyona
yansıtmışlarsa bu durumda kendi ``Makefile`` dosyasına bu eklemeleri yukarıdaki gibi girebilirler.
Örneğin biz ``mymodule`` ile temsil ettiğimiz bir modül dosyası oluşturup bu modül dosyasının çekirdek
kodlarına eklenip eklenmeyeceğini konfigürasyonda ``Kconfig`` dosyası yoluyla belirtebiliriz. Bu durumda
``Makefile`` içerisindeki girişi aşağıdaki gibi de oluşturabiliriz:

.. code-block:: makefile

   obj-$(CONFIG_MYMODULE) += mymodule.o

Görüldüğü gibi burada aslında konfigüre eden nasıl seçmişse biz onun seçimini yansıtmış olmaktayız.
``.config`` dosyasında bir özellik ``n`` ise bu durumda ilgili ``Makefile`` satırı şu hale gelecektir:

.. code-block:: makefile

   obj-n += mymodule.o

``obj-n`` biçiminde bir birikim yapılmadığı için zaten bu satır derleme aşamasında dikkate alınmayacaktır.
Ancak bazen sistem programcıları ``y`` durumu için aşağıdaki gibi bir kontrol ile modülü koşullu bir
biçimde de derleme sürecine ekleyebilmektedir:

.. code-block:: makefile

   ifeq ($(CONFIG_MYSYSCALL), y)
       obj-y += mysyscall.o
   endif

Burada eğer konfigürasyon yapılırken ilgili seçenek ``y`` biçiminde (yani ``[*]`` ya da ``<*>``
biçiminde) geçilmişse bu durumda biz de ilgili dosyayı derlemeye dahil etmiş olduk.


.. rubric:: ── 9. Ders · 16 Ağustos 2025, Cumartesi ──

----

Yeni Dizin için Makefile ve Kconfig Dosyaları
===============================================

Bir C dosyasını ya da dizini çekirdek kodlarına ekledikten sonra onun konfigürasyon sırasında (örneğin
*"make menuconfig"* işlemi sırasında) görünebilirliğini sağlamak için ``Kconfig`` dosyalarının
kullanıldığını belirtmiştik. Yani ``Kconfig`` dosyaları yaptığımız değişikliklerin konfigüre
edilebilirliğini sağlamak için kullanılmaktadır. ``Kconfig`` dosyalarının genel formatı için aşağıdaki
bağlantıya başvurabilirsiniz:

   https://docs.kernel.org/kbuild/kconfig-language.html

``Kconfig`` dosyaları tıpkı ``Makefile`` dosyalarında olduğu gibi özyinelemeli biçimde işletilmektedir.
Yani biz çekirdek kaynak kod ağacında bir dizin yaratmayıp zaten var olan bir dizinin içerisine bir ``.c``
dosyası yerleştiriyorsak ``Makefile`` ve ``Kconfig`` dosyaları oluşturmamıza gerek yoktur. Gerekli
işlemleri zaten dizin içerisinde var olan bir ``Makefile`` ve ``Kconfig`` dosyaları üzerinde yapabiliriz.
Ancak eğer biz bir dizin oluşturup onun içerisine dosyalar yerleştireceksek o dizin için bir tane
``Makefile`` ve bir tane de ``Kconfig`` dosyası oluşturmamız gerekir.

Bir dizin yaratıp onun içerisine dosyalar yerleştirirken o dizin için ``Makefile`` ve ``Kconfig``
dosyalarının yazılması gerektiğini belirtmiştik. (Tabii aslında ``Kconfig`` dosyasının bulundurulması
zorunlu değildir. Ancak eklenen özelliğin konfigüre edilebilirliğinin sağlanması için gerekmektedir.)
Bu dosyalar oluşturulduktan sonra dış dizindeki ``Makefile`` ve ``Kconfig`` dosyalarında aşağıda
belirtilen işlemler de yapılmalıdır:

1. Dış dizindeki ``Makefile`` dosyasında alt dizinin dikkate alınacağı aşağıdaki gibi bir satırla
   belirtilmelidir:

   .. code-block:: makefile

      obj-y += <dizin_ismi>/

2. Dış dizinin ``Kconfig`` dosyasında iç dizindeki ``Kconfig`` dosyasının dikkate alınması aşağıdaki
   gibi bir satırın eklenmesiyle sağlanmaktadır (buradaki yol ifadesi çekirdek kodlarının kök dizinine
   göreli olmalıdır):

   .. code-block:: text

      source "drivers/mydriver/Kconfig"

Biz ``Kconfig`` dosyasına yukarıdaki gibi bir giriş yerleştirdiğimizde artık *"make menuconfig"* gibi
konfigürasyon menülerinde eklediğimiz ``Kconfig`` elemanı bir menü seçeneği biçiminde karşımıza
çıkacaktır.

Örneğin biz bir aygıt sürücümüzün dosyalarını çekirdeğin kaynak kod ağacında ``drivers`` dizininin
altına ``mydriver`` dizinini açarak eklemek isteyelim. Bu durumda şunları yapmamız gerekir:

1. ``drivers`` dizini içerisinde ``mydriver`` dizinini yaratıp içerisine ``mydriver.c`` dosyasını
   (belki de ``mydriver.h`` gibi bir başlık dosyasını da) yerleştirmeliyiz.

2. ``drivers/mydriver`` dizininde aşağıdaki gibi bir ``Kconfig`` dosyasını oluşturmalıyız. Buradaki
   ``config MYDRIVER`` satırı aslında make dilinde ``CONFIG_MYDRIVER`` değişkeninin oluşturulmasına yol
   açmaktadır:

   .. code-block:: text

      config MYDRIVER
          tristate "My Driver"
          default y
          help
            Enable this option to include support for My Device Driver.
            It can either be built as a module or statically linked into the kernel.

   Eğer ilgili konfigürasyon seçeneği yes/no biçimindeyse (yani ``[*]`` biçimindeyse) yukarıdaki config
   direktifinde *tristate* yerine *bool* kullanılmalıdır. Örneğin:

   .. code-block:: text

      config MYDRIVER
          bool "My Driver"
          default y
          help
            Enable this option to include support for My Device Driver.

3. Üst dizindeki (``drivers`` dizinindeki) ``Kconfig`` dosyasına aşağıdaki satırı yerleştirmeliyiz:

   .. code-block:: text

      source "drivers/mydriver/Kconfig"

4. ``drivers/mydriver`` dizinindeki ``Makefile`` dosyası içerisine aşağıdaki gibi bir satır eklemeliyiz:

   .. code-block:: makefile

      obj-$(CONFIG_MYDRIVER) += mydriver.o

5. Üst dizindeki (yani ``drivers`` dizinindeki) ``Makefile`` içerisine aşağıdaki gibi bir satır
   eklemeliyiz:

   .. code-block:: makefile

      obj-$(CONFIG_MYDRIVER) += mydriver/

Tabii eğer siz bir dizin yaratmayıp zaten çekirdek kaynak kod ağacındaki bir dizine bir dosya
yerleştiriyorsanız bu durumda ayrı bir ``Kconfig`` dosyasını oluşturmanıza gerek yoktur. Bu durumda
doğrudan yukarıdaki config içeriğini dizinde zaten var olan ``Kconfig`` dosyasına yerleştirebilirsiniz.


Örnek: Çekirdeğe Yeni Modül Ekleme
=====================================

Şimdi çekirdeğe bazı kodlar ekleyip onu yeniden derleyerek bir deneme yapalım. Örneğin çekirdeğe yeni
bir çekirdek modülü ekleyelim ve çekirdeğin o modül gömülü olarak başlatılmasını sağlayalım. Aynı
zamanda bu çekirdek modülünün *"make menuconfig"* ile seçilebilmesini de sağlayalım. Çekirdek
modüllerinin nasıl yazılacağını bilmediğinizi varsayıyoruz. Ancak biz yine de örneğimizde "hiçbir şey
yapmayan iskelet bir çekirdek modülü" oluşturacağız. Bu işlem şu adımlardan geçilerek yapılabilir
(kaynak kod ağacının kök dizininde bulunduğumuzu varsayıyoruz):

**Adım 1:** ``drivers/mydriver`` dizini yaratılır.

**Adım 2:** İskelet bir çekirdek modülü ``mydriver.c`` biçiminde ``drivers/mydriver`` dizininde
aşağıdaki gibi oluşturulur:

.. code-block:: c

   /* mydriver.c */

   #include <linux/module.h>
   #include <linux/kernel.h>

   MODULE_LICENSE("GPL");
   MODULE_AUTHOR("Kaan Aslan");
   MODULE_DESCRIPTION("General Device Driver");

   static int __init mydriver_init(void)
   {
       printk(KERN_INFO "Hello World...\n");
       return 0;
   }

   static void __exit mydriver_exit(void)
   {
       printk(KERN_INFO "Goodbye World...\n");
   }

   module_init(mydriver_init);
   module_exit(mydriver_exit);

**Adım 3:** ``drivers/mydriver`` dizininde ``Kconfig`` dosyası aşağıdaki gibi oluşturulmalıdır.
Burada konfigürasyon makrosunun ismi ``CONFIG_MYDRIVER`` biçiminde olacaktır:

.. code-block:: text

   config MYDRIVER
       tristate "My Character Device Driver"
       default y
       help
         Enable this option to include support for My Device Driver.
         It can either be built as a module or statically linked into the kernel.

**Adım 4:** Üst dizinin (yani ``drivers`` dizininin) ``Kconfig`` dosyasına aşağıdaki ekleme
yapılmalıdır:

.. code-block:: text

   source "drivers/mydriver/Kconfig"

**Adım 5:** ``drivers/mydriver`` dizininde aşağıdaki içeriğe sahip bir ``Makefile`` dosyası
oluşturulmalıdır:

.. code-block:: makefile

   obj-$(CONFIG_MYDRIVER) += my_driver.o

**Adım 6:** Üst dizindeki (``drivers`` dizinindeki) ``Makefile`` dosyasına aşağıdaki satır
eklenmelidir:

.. code-block:: makefile

   obj-$(CONFIG_MYDRIVER) += mydriver/

Artık çekirdeği derleyebiliriz. *"make menuconfig"* menüsünde kendi aygıt sürücümüze ilişkin seçenek
de çıkacaktır.

Çekirdek imzalamasını devre dışı bırakmak için konfigürasyon dosyasındaki satırlarda aşağıdaki
değişiklikleri yapmayı unutmayınız:

.. code-block:: text

   CONFIG_SYSTEM_TRUSTED_KEYS=""
   CONFIG_SYSTEM_REVOCATION_KEYS=""
   CONFIG_SYSTEM_TRUSTED_KEYRING=n
   CONFIG_SECONDARY_TRUSTED_KEYRING=n

   CONFIG_MODULE_SIG=n
   CONFIG_MODULE_SIG_ALL=n
   CONFIG_MODULE_SIG_KEY=""

Yeni çekirdeğimize ``-custom`` ismini de ekleyebiliriz. Daha önceden de belirttiğimiz gibi eğer
çekirdeğin eski versiyonundan konfigürasyon dosyası alınacaksa *"make oldconfig"* uygulanıp o
versiyondan sonra eklenmiş olan özelliklerin gözden geçirilmesi sağlanmalıdır. Ancak *"make menuconfig"*
işlemi zaten *"make oldconfig"* işlemini de içermektedir.

**Adım 7:** Artık çekirdek derlemesi aşağıdaki gibi yapılabilir:

.. code-block:: bash

   $ make -j$(nproc)

**Adım 8:** Derleme işlemi bittikten sonra önce çekirdek modüllerini *"make modules_install"* ile
sonra da çekirdeğin kendisini *"make install"* ile kurabilirsiniz:

.. code-block:: bash

   $ sudo make modules_install
   $ sudo make install

Anımsanacağı gibi *"make install"* komutu artık sistemin yeni çekirdekle açılmasını sağlayacaktır.
*"make install"* aynı zamanda geçici kök dosya sistemini *update-initramfs* komutu ile oluşturup
``/boot`` dizinine yerleştirmektedir. Tabii *update-initramfs* programını siz de gerektiğinde
kullanabilirsiniz. Programın tipik kullanımı şöyledir:

.. code-block:: bash

   $ sudo update-initramfs -c -k <çekirdek_sürümü>

Buradaki *çekirdek_sürümü* yalnızca çekirdeğin numarasını değil ona verdiğiniz ekleri de içermelidir.
(Örneğin ``6.9.2-custom`` gibi.) Bu komut geçici kök dosya sistemini o anda çalışmakta olan sistemin
konfigürasyonunu da dikkate alarak oluşturur ve ``/boot`` dizinine kopyalar. Yukarıda da belirttiğimiz
gibi *"make install"* zaten bu programı çalıştırarak geçici kök dosya sistemini ``/boot`` dizininde
oluşturmaktadır.

Peki çekirdeğin kaynak kodlarına yaptığımız eklemenin gerçekten yapılmış olduğunu nasıl anlayabiliriz?
Bizim yazdığımız iskelet aygıt sürücü kodlarında çekirdek aygıt sürücümüz yüklendiğinde
``mydriver_init`` fonksiyonu çağrılacaktır. Bu fonksiyonun içinde de *printk* isimli çekirdek fonksiyonu
ile biz bir log mesajı yazdırdık. Bu log mesajları *kernel ring buffer* denilen bir kuyruk sistemine
yazılmaktadır. *dmesg* komutuyla bu kuyruk sistemi görüntülenebilir. Eğer *dmesg* yaptığımızda biz bu
mesajları görürsek aygıt sürücümüzün yüklenmiş olduğu sonucunu çıkartabiliriz. Örneğin:

.. code-block:: bash

   $ dmesg | grep "Hello"
   Hello World...

Çekirdeğin içerisine gömülmüş olan modüller ``/proc/modules`` dosyasında görünmezler, dolayısıyla da
*lsmod* komutu ile de bunları göremeyiz. Bunlar için ``/sys/module`` dizininde de bir giriş
oluşturulmamaktadır. *modinfo* komutu ise çekirdeğe ilişkin bazı dosyalara da baktığı için bize bu
konuda bilgi verebilmektedir.


Yeniden Derleme Sonrası Güncellemeler
=======================================

Peki çekirdek kodlarında küçük değişiklikler yaptıktan sonra yeniden *"make modules_install"* ve
*"make install"* işlemlerine gerek var mı? Aslında küçük değişiklikler için bu işlemler yapılmazsa
genellikle bir sorun ortaya çıkmaz. Yeni oluşturulan çekirdek imajı doğrudan eskisinin üzerine
kopyalanabilir. Ancak değişikliğin yerine ve kapsamına göre çekirdeğin sembol tabloları değişebileceği
için genel olarak her derlemeden sonra *"make install"* yapabilirsiniz.

``drivers`` dizininde ``obj-m`` biçiminde değişiklikler yapılmışsa *"make modules_install"* yapılmalıdır.
Yukarıdaki örnekte biz ``drivers`` dizininin içerisine ``obj-y`` ile eklemeler yaptık; bu durumda aslında
*"make modules_install"* yapmaya gerek yoktur. Ancak aygıt sürücüler ``obj-m`` biçiminde ekleniyorsa
*"make modules_install"* komutu uygulanmalıdır. Çekirdeğin modüllerle ilgili olmayan kısımlarında yapılan
değişiklikler için *"make modules_install"* yapılmasına gerek olmadığını bir kez daha belirtmek istiyoruz.
*"make modules_install"* işleminden önce eski ``/lib/modules/<çekirdek_sürümü>`` dizinini *"rm -r"* komutu
ile silmek daha güvenli bir yaklaşımdır.


Çekirdek ve Modül İmzalama
============================

Biz yukarıdaki çekirdek derlemesi sürecinde imzalama (signing) işlemlerini devre dışı bırakmıştık.
Çekirdek kodları ve özellikle de aygıt sürücüler belli imzalara sahip olacak biçimde derlenebilmektedir.
Böylece onlar üzerinde birtakım istenmeyen değişikliklerin yapılmış olduğu değiştirilmiş çekirdeklerin
ya da aygıt sürücülerin yüklenmesi engellenmiş olur. Yukarıda da gördüğünüz gibi çekirdek kodları ve
aygıt sürücülerde bu imzalama işlemi devre dışı da bırakılabilmektedir. Ancak imzalama süreci sistem
güvenliğini artırmaktadır. Bu tür imzalama işlemleri yalnızca Linux sistemlerinde değil diğer UNIX
türevi sistemlerde, Windows ve macOS sistemlerinde de bulunmaktadır.

Çekirdeğin imza kontrolü temel olarak UEFI BIOS (eğer *secure boot* seçeneği aktif ise) ve önyükleyiciler
(örneğin GRUB gibi, U-Boot gibi önyükleyiciler) tarafından yapılmaktadır. Ancak Linux çekirdeği de aygıt
sürücüler ve modüller yüklenirken imza kontrolü uygulayabilmektedir. Biz burada önce modül imzalama
işleminin ve sonra da çekirdek imzalama işleminin nasıl yapılacağı üzerinde duracağız.

İmzalama işlemi tipik olarak şu adımlardan geçilerek yapılmaktadır:

**Adım 1:** İmzalama işlemi için öncelikle *openssl* kütüphanesinin yüklenmiş olması gerekir. Yükleme
işlemi aşağıdaki gibi yapılabilir:

.. code-block:: bash

   $ sudo apt-get install openssl

Daha sonra *openssl* programı ile aşağıdaki gibi bir anahtar çifti ve sertifika dosyası üretilir.
Buradaki ``.key`` dosyası özel anahtarı (private key), ``.crt`` dosyası ise sertifika dosyasını
belirtmektedir. Bu dosyaların uzantıları ``.key``, ``.crt``, ``.pem`` olsa da içeriği PEM (Privacy
Enhanced Mail) formatındadır. Dolayısıyla aslında burada verdiğiniz dosyaların uzantısı herhangi bir
biçimde olabilir:

.. code-block:: bash

   $ openssl req -new -x509 -newkey rsa:2048 -sha256 \
       -keyout signing_key.key -out certs/signing_key.crt \
       -nodes -days 36500 -subj "/CN=Local Kernel Module Key/"

Bu iki dosyanın kaynak kod ağacına aşağıdaki gibi kopyalanması gerekir:

.. code-block:: bash

   $ cp signing_key.key certs/
   $ cp signing_key.crt certs/

Daha sonra konfigürasyon dosyasında imzalama için aşağıdaki değişiklikler yapılmalıdır:

.. code-block:: text

   CONFIG_MODULE_SIG=y
   CONFIG_MODULE_SIG_ALL=y
   CONFIG_MODULE_SIG_SHA256=y
   CONFIG_SYSTEM_TRUSTED_KEYRING=y
   CONFIG_MODULE_SIG_KEY="certs/signing_key.pem"
   CONFIG_SYSTEM_TRUSTED_KEYS="certs/signing_key.crt"

Aslında ``.key`` ve ``.crt`` dosyaları tek bir dosyada da birleştirilebilir:

.. code-block:: bash

   $ cat certs/signing_key.key certs/signing_key.crt > certs/signing_key.pem

Tabii artık ``.config`` dosyasındaki isimleri de şöyle değiştirmeliyiz:

.. code-block:: text

   CONFIG_MODULE_SIG=y
   CONFIG_MODULE_SIG_ALL=y
   CONFIG_MODULE_SIG_SHA256=y
   CONFIG_SYSTEM_TRUSTED_KEYRING=y
   CONFIG_MODULE_SIG_KEY="certs/signing_key.pem"
   CONFIG_SYSTEM_TRUSTED_KEYS="certs/signing_key.pem"

Biz bu işlemlerle aygıt sürücüleri imzalamış olduk. Ancak eğer ``.config`` dosyasında
``CONFIG_MODULE_SIG_FORCE=n`` ise (default durumda genellikle böyledir) bu durum çekirdek log amaçlı
bir uyarı oluştursa da imzalanmamış modülleri yine de yükler. Eğer imzalanmamış modülleri yüklemek
istemiyorsanız ``CONFIG_MODULE_SIG_FORCE=y`` yapmalısınız. (Bu işlem *"make menuconfig"* menüsünde
*Enable loadable module support / Module signature verification / Require modules to be validly signed*
seçeneğinden de yapılabilmektedir.) Bu durumda çekirdek kendi oluşturduğumuz imzayla imzalanmamış olan
modülleri artık yüklemeyecektir.

Eğer biz başkalarının yazdığı bir aygıt sürücüyü yüklerken çekirdeğin uyarı vermesini ya da yüklemeyi
reddetmesini istemiyorsak o aygıt sürücüyü de kendi ürettiğimiz anahtarla (ya da dağıtımın public
anahtarıyla) imzalamalıyız. Bu işlem çekirdek kodlarındaki ``scripts`` dizini içerisinde bulunan
*sign-file* betiği ile yapılmaktadır. Bu betiğin tipik kullanımı şöyledir:

.. code-block:: bash

   $ scripts/sign-file <hash_alg> <private_key.pem> <public_cert.pem> <module.ko>

Örneğin:

.. code-block:: bash

   $ scripts/sign-file sha256 signing_key.pem signing_key.pem mydriver.ko

Peki Ubuntu, Mint gibi dağıtımlar çekirdek imzalaması uygulamakta mıdır? Evet, genel olarak dağıtımlar
kendi özel anahtarlarıyla (private keys) çekirdeği ve aygıt sürücüleri imzalamaktadır. Ancak aygıt
sürücülerin yüklenmesinde imza kontrolünü zorunlu hale getirmemektedir. İmzalama için kullanılacak
public anahtarlar ``/proc/keys`` dosyasında belirtilmektedir.


Çekirdek İmjasının İmzalanması
================================

Biz yukarıdaki işlemleri yaptığımızda yalnızca aygıt sürücüleri imzalamış oluruz. Çekirdeğin kendisinin
imzalanması ayrıca yapılmalıdır. Yukarıda da belirttiğimiz gibi UEFI BIOS'lar ve GRUB gibi önyükleyiciler
çekirdek imajını yüklemeden önce ayarlar uygun biçime getirildiyse çekirdek imzasına bakmaktadır. Eğer
çekirdek imzası yanlışsa (çekirdek dışarıdan kasti ya da yanlışlıkla bozulmuş olabilir) çekirdeği hiç
yüklememektedir.

Çekirdeğin imzalanması için önce anahtar ve sertifikasyon dosyaları aşağıdaki gibi oluşturulur:

.. code-block:: bash

   $ openssl req -new -x509 -newkey rsa:2048 -sha256 \
       -keyout certs/sb-signing.key \
       -out certs/sb-signing.crt \
       -nodes -days 36500 \
       -subj "/CN=Secure Boot Signing Key/"

Sonra da *sbsign* programı ile imzalama aşağıdaki gibi yapılır:

.. code-block:: bash

   $ sbsign --key db.key --cert signing_key.pem --output bzImage.signed arch/x86/boot/bzImage

Eğer bu işlemden sonra *"make install"* yapacaksanız imzalanmış çekirdeği eski ismiyle bulundurmalısınız
(*mv* komutu hedef dosya varsa onu ezerek işlemini yapmaktadır):

.. code-block:: bash

   $ mv arch/x86/boot/bzImage.signed arch/x86/boot/bzImage

Genellikle bu biçimde bir çekirdek imzalaması seyrek olarak yapılmaktadır. Önceki paragrafta biz aygıt
sürücü dosyalarının imzalandığını belirtmiştik. Aynı makinede aygıt sürücüyü derlerken (build ederken)
oluşturulan imza bilgisi de kullanılmaktadır. Yani biz aynı makinede bir aygıt sürücü derlediğimizde
aygıt sürücümüz de zaten imzalanmış olacaktır.


Kök Dosya Sisteminin Oluşturulması
=====================================

Bir Linux sisteminin düzgün bir biçimde açılması için belli dizinlerin kök dosya sisteminde bulunuyor
olması gerekir. Biz bir dağıtımı kurduğumuzda zaten bu kök dosya sistemi de oluşturulmaktadır. Peki
sıfırdan dağıtımı tamamen kurmadan kök dosya sistemini nasıl oluşturulabiliriz? Bu işlem tamamen manuel
biçimde yapılabilir. Yani uygulamacı kök dizin içerisindeki gerekli dizinleri elle yaratır. Sonra
gerekli programları kaynak kodlarından hareketle hedef makine için derler ve onları konuşlandırır. Sonra
yine gerekli birtakım konfigürasyon dosyalarını elle oluşturur. Ancak bu manuel yöntem oldukça zahmetlidir.

Bunun yerine bu işlemi pratik bir biçimde yapan araçlar geliştirilmiştir. Örneğin gömülü sistemlerde
*BusyBox* denilen araç bu amaçla sıkça kullanılmaktadır. Kullanımı da oldukça kolaydır. Gömülü sistemler
için *Buildroot* ve *Yocto* gibi projeler daha genel amaçlar için gerçekleştirilmiştir ancak bunlarla kök
dosya sistemi de oluşturulabilmektedir. Bazı dağıtımların bu işi yapan özel yardımcı programları da vardır.
Örneğin *debootstrap* programı Debian tabanlı kök dosya sistemini İnternet'ten indirerek yerel makinede
oluşturabilmektedir. Ancak bu araçların bazıları esnek değildir. Özellikle gömülü sistemlerde düşük bir
sistem kaynağının olduğu dikkate alındığında bu araçların bazıları minimalist bir kurulum
sağlayamamaktadır.


``debootstrap`` ile Kök Dosya Sistemi Oluşturma
-------------------------------------------------

*debootstrap* programı default olarak sisteminizde yüklü değildir. Bunu aşağıdaki gibi kurabilirsiniz:

.. code-block:: bash

   $ sudo apt-get install debootstrap

*debootstrap* programının pek çok komut satırı argümanı vardır. Biz burada en önemli birkaç argüman
üzerinde duracağız:

- ``--arch``: Hedef CPU mimarisini belirtmektedir. Bu argüman girilmezse o andaki platform temel alınır.
  64 bit Intel platformu için ``amd64``, BBB gibi 32 bit ARM platformu için ``armhf``, 64 bit ARM platformu
  için ``arm64`` girilmelidir.
- İlk seçeneksiz argüman Debian sisteminin varyantını belirtmektedir (örneğin ``bullseye``, ``buster``).
- İkinci komut satırı argümanı hedef kök dosya sisteminin oluşturulacağı dizini belirtmektedir.
- Üçüncü komut satırı argümanı ise paketlerin indirileceği depoyu (repository) belirtmektedir.

Örneğin:

.. code-block:: bash

   $ sudo debootstrap --arch=amd64 --include=systemd bullseye myrootfs http://deb.debian.org/debian/

``--arch`` seçeneği girilmemişse programın çalıştırıldığı makine için kök dosya sistemi indirilip
kurulmaktadır. Default durumda *debootstrap* pek çok paketi kök dosya sistemine dahil ettiği için
paketlerin indirilmesi ve kök dosya sisteminin oluşturulması biraz zaman alacaktır.

Uygulamacı isterse ``--include`` ve ``--exclude`` komut satırı seçenekleriyle birtakım paketleri dahil
edebilir ya da dışlayabilir. Örneğin biz *systemd* dışında *sudo* ve *gcc* paketlerini de aşağıdaki gibi
kuruluma dahil edebiliriz:

.. code-block:: bash

   $ sudo debootstrap --arch=amd64 --include=systemd,sudo,gcc bullseye myrootfs http://deb.debian.org/debian/

*debootstrap* programı ile eğer host makineyle aynı platform için indirme işlemi yapılıyorsa *debootstrap*
önce İnternet'ten gerekli paketleri indirip yerel makinede bir dizin içerisinde kök dosya sistemini
oluşturur. Eğer host makineden farklı bir sistem için indirme yapılıyorsa (örneğin host sistem Intel
tabanlı bir makineyse ve ARM tabanlı bir Debian kök dosya sistemi oluşturulmak isteniyorsa) *debootstrap*
yüklemesini yapmadan önce aşağıdaki gibi *qemu* emülatör paketinin statik versiyonu ve *binfmt* destek
paketi kurulmalıdır:

.. code-block:: bash

   $ sudo apt install qemu-user-static binfmt-support

Bu işlemden sonra *debootstrap* programı yukarıda belirttiğimiz biçimde çalıştırılabilir:

.. code-block:: bash

   $ sudo debootstrap --include=systemd --arch armhf buster myrootfs http://deb.debian.org/debian/

Bu komut hem birinci aşama hem de ikinci aşama işlemleri yapıp bitirecektir. Artık istenildiği zaman
*chroot* işlemi de yapılabilir:

.. code-block:: bash

   $ sudo chroot myrootfs


Geçici Kök Dosya Sisteminin Oluşturulması
------------------------------------------

*debootstrap* programı ile biz Debian kök dosya sistemi için geçici kök dosya sistemi de oluşturabiliriz.
Bunun en pratik yolu kök dosya sistemini kurduktan sonra *chroot* yapıp *update-initramfs* programı ile
geçici kök dosya sistemini oluşturmaktır. Ancak bunun için ``/boot`` ve ``/lib/modules`` dizinlerinin
uygun biçimde oluşturulmuş olması gerekir. *update-initramfs* programı bu dizinlerdeki içerikten
faydalanmaktadır. *update-initramfs* programı *initramfs-tools* isimli pakettedir. *chroot* yaptıktan
sonra öncelikle bu paketi aşağıdaki gibi kurmalısınız:

.. code-block:: bash

   $ sudo apt-get install initramfs-tools

Bundan sonra geçici kök dosya sistemini aşağıdaki gibi oluşturabilirsiniz (Debian kök dosya sisteminin
kökünde olduğumuzu varsayıyoruz):

.. code-block:: bash

   $ update-initramfs -c -k 6.9.2-custom -b .

Burada ``6.9.2-custom`` çekirdeğin sürüm ismidir. Geçici kök dosya sistemi ``initrd.img-6.9.2-custom``
ismiyle bulunulan dizinde oluşturulacaktır. ``-b .`` seçeneği oluşturulacak dosyanın dizinini
belirtmektedir.

.. note::

   Bu tür konuların ayrıntılarına bu kursta girmeyeceğiz. Bu konular daha çok *Gömülü Linux Sistemleri -
   Geliştirme ve Uygulama* kursunun konularını oluşturmaktadır.


Çekirdek Başlık Dosyalarının Kurulumu
=======================================

Aygıt sürücü geliştirirken çekirdeğin kaynak kodlarına gereksinim duyulmaz. Ancak çekirdeğin başlık
dosyalarının geliştirmenin yapıldığı bilgisayarda yüklü olması gerekir. Çekirdek kodlarının kendisini
değil de yalnızca başlık dosyalarını indirmek için aşağıdaki komut kullanılabilir:

.. code-block:: bash

   $ sudo apt install linux-headers-$(uname -r)

Buradaki ``$(uname -r)`` çalışılmakta olan makinedeki çekirdek sürümünü belirtmektedir. Tabii biz
istediğimiz çekirdek sürümünün başlık dosyalarını da indirebiliriz. İndirilen dosyalar ``/usr/src``
dizininin altına ``$(uname -r)`` isimli dizin içerisine yerleştirilmektedir.
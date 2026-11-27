========================================================================================
**Proseslerin ve Thread'lerin Yaratılması** :raw-html:`<br>` **fork ve clone İşlemleri**
========================================================================================

Bu bölümde Linux çekirdeğinde proseslerin ve thread'lerin yaratılması süreci üzerinde duracağız. Bölüm içerisinde önce
proseslerin ve thread'lerin kullanıcı modunda nasıl yaratıldığını anımsatacağız. Sonra bu süreçlerin çekirdek tarafını
ele alacağız.

fork Fonksiyonu
===============

Bilindiği gibi UNIX türevi sistemlerde prosesler kullanıcı alanında ``fork`` isimli POSIX fonksiyonuyla yaratılmaktadır.
``fork`` fonksiyonunun prototipi şöyledir:

.. code-block:: c

    #include <unistd.h>

    pid_t fork(void);

İngilizce *fork* sözcüğü Türkçe *çatal* anlamına gelmektedir. *Akışın çatallanması* gibi bir benzetmeye dayanılarak bu
isim uydurulmuştur.

``fork`` bir prosesin özdeş bir kopyasını oluşturmaktadır. ``fork`` fonksiyonunun çalışmasını şöyle bir analoji ile
açıklayabiliriz. Diyelim ki bir klonlama makinesi var. Bu makine insandaki tüm atomları bire bir kopyalayarak yeni bir
klon oluşturuyor olsun. Bu durumda klonlama makinesine bir kişi girdiğinde makineden iki kişi çıkmaktadır. Makineden
çıkan iki kişinin tüm geçmiş yaşantıları, her şeyi aynı olacaktır. Makineden çıktığında her iki kişi de kendini gerçek
kopya sanabilir. Çünkü klonlama sırasında tüm atomlar (bellek mekanizması nöral düzeyde işlev görmektedir; nöronlar da
neticede atomlardan oluşmaktadır) kopyalanmıştır. Makineden çıkan iki kişinin her şeyi aynıdır. Ancak makineden
çıktıktan sonra artık bunlar farklı olaylarla karşılaşacakları için bellek ve deneyim olarak farklılaşacaklardır. Burada
her ne kadar makineden çıkan iki kişi de kendisinin gerçek kopya olduğunu sanıyorsa da klonlamayı yapan operatör kimin
orijinal olduğunu, kimin onun klonu olduğunu bilmektedir.

İşte ``fork`` fonksiyonunun çalışması yukarıdaki analojiye çok benzemektedir. ``fork`` fonksiyonuna giren akış orada
yeni ve özdeş bir prosesin yaratılmasına yol açmaktadır. Yeni yaratılan prosesin bellek alanı ve proses kontrol bloğu
(``task_struct`` nesnesi) büyük ölçüde üst prosesten kopyalanmaktadır. Yeni yaratılan prosesin akışı ``fork``
içerisinden başlatılmaktadır. Böylece asıl proses ile yeni yaratılan prosesin her ikisi de ``fork`` fonksiyonundan
çıkar. Asıl proses ile yeni yaratılan proses aynı bellek alanına (yani kabaca aynı *code*, *data*, *stack* ve *heap*
alanlarına) sahiptir. ``fork`` çağrısını yapan asıl prosese *üst proses (parent process)*, ``fork`` ile yaratılan yeni
prosese ise *alt proses (child process)* denilmektedir. Tabii üst proses de aslında ``fork`` çağrısı ile başka bir
proses tarafından yaratılmıştır.

Yani ``fork`` fonksiyonunda kabaca şunlar yapılmaktadır:

| **1.** Alt proses için yeni bir proses kontrol bloğu (``task_struct``) yaratılır. ``fork`` işlemini yapan prosesin (üst
    proses) proses kontrol bloğunun (``task_struct``) içeriği yeni yaratılan prosesin (alt proses) proses kontrol bloğuna
    kopyalanır. Böylece üst proses ile yeni yaratılan alt proses aynı özelliklere sahip olmaktadır. Örneğin bu iki prosesin 
    etkin ve gerçek kullanıcı ve grup ID'leri, çalışma dizinleri (*current working directories*), açmış oldukları dosyalara 
    ilişkin bilgiler aynı olur.
    
| **2.** Çekirdek alt proses için üst prosesin sanal bellek alanının özdeş kopyasını oluşturur. Böylece her iki proses de
    içerik olarak aynı *kod* alanına, aynı *data* alanına, aynı *stack* alanına ve aynı *heap* alanına sahip olacaktır.
    Ancak bunlar birbirlerinden ayrıdır.

| **3.** Yeni yaratılan alt proses çalışmaya ``fork`` fonksiyonunun içinden başlar. Her iki akış da (yani ``fork`` uygulayan
    prosesin akışı ve yeni yaratılan alt prosesin akışı da) ``fork`` içerisinden çıkar. Üst proses ``fork``
    fonksiyonundan alt prosesin proses ID'si ile çıkarken alt proses ``0`` ile çıkmaktadır.
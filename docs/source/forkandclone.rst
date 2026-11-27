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

Yukarıdaki işlemler ``fork`` fonksiyonunun içinde yapılmaktadır. ``fork`` fonksiyonundan hem bu fonksiyonu çağıran
proses hem de yeni yaratılan proses çıkmaktadır. Ancak bunların bellek alanları ayrı olduğu için artık birinin yapacağı
değişikliği diğeri görmeyecektir. ``fork`` fonksiyonu, bir klonlama yapmaktadır. Yeni bir prosesi, kendini çağıran
prosesle aynı özelliklerle ve aynı bellek alanı ile yaratmaktadır. ``fork`` sırasında prosesin kontrol bloğu yeni
yaratılan prosese kopyalandığı için üst proses ile alt proses aynı gerçek ve etkin kullanıcı ve grup ID'sine sahip olur.

``fork`` işlemini yapan proses üst proses (parent process) durumundadır. Yeni yaratılan proses ise alt proses (*child
process*) durumundadır. Tabii alt proses yeni bir proses ID'ye sahip olacaktır. Alt prosesin üst prosesi, ``fork``
fonksiyonunu uygulayan proses olacaktır.

``fork`` fonksiyonu başarısız olabilir. (Örneğin kaynak yetersizliği durumunda, kullanıcının proses yaratma limiti
aşıldığı durumda ``fork`` başarısız olabilir.) ``fork`` başarısızlık durumunda ``-1`` değerine geri dönmektedir.

Yukarıda da belirttiğimiz gibi yeni yaratılan prosesin (alt prosesin) akışı da ``fork`` fonksiyonunun içerisinden
başlatılmaktadır. Bu durumda her iki proses de ``fork`` fonksiyonunun içerisinden çıkacaktır. İşte üst proses (yani
``fork`` işlemini yapan proses) alt prosesin ID değeri ile, alt proses ise 0 değeri ile ``fork`` fonksiyonundan
çıkar. Böylece programcı ``fork`` çıkışında üst proses ile alt prosese farklı işlemler yaptırabilmektedir. (Alt prosesin
``fork`` içerisinden ``0`` ile çıkması alt prosesin proses ID'sinin ``0`` olduğu anlamına gelmemektedir. Alt prosesin
proses ID'si alt proses içerisinden ``getpid`` POSIX fonksiyonuyla elde edilebilmektedir.)

``fork`` kullanımına ilişkin tipik kalıp şöyledir:

.. code-block:: c

    pid_t pid;
    /* ... */

    if ((pid = fork()) == -1)
        exit_sys("fork");

    if (pid != 0) {         /* parent process */
        /* ... */
    }
    else {                  /* child process */
        /* ... */
    }

Aşağıdaki örnekte ``fork`` fonksiyonu ile bir proses yaratılmış ve proses ID'ler üst ve alt proseslerde yazdırılmıştır.
Bu örnekte üst proseste ``fork`` fonksiyonunun alt prosesin proses ID değeri ile geri döndüğüne dikkat ediniz. Denemenin
yapıldığı makinede şöyle bir çıktı elde edilmiştir:

.. code-block:: text

    Parent PID: 110303
    Parent's parent PID: 106380
    fork return value: 110304
    Common code...
    Child PID: 110304
    Child's parent PID: 110303
    Common code...

Görüldüğü gibi alt prosesin üst proses ID'si ile üst prosesin proses ID'si aynıdır. Programı kabuk üzerinden
çalıştırdığımız için üst prosesin üst proses ID'si kabuk prosesinin (tipik olarak bash) proses ID'si olacaktır:

.. code-block:: console

    $ ps
       PID TTY        TIME CMD
    106380 pts/2    00:00:00 bash
    110308 pts/2    00:00:00 ps

.. code-block:: c

    #include <stdio.h>
    #include <stdlib.h>
    #include <stdint.h>
    #include <unistd.h>

    void exit_sys(const char *msg);

    int main(void)
    {
        pid_t pid;

        if ((pid = fork()) == -1)
            exit_sys("fork");

        if (pid != 0) {         /* parent process */
            printf("Parent PID: %jd\n", (intmax_t)getpid());
            printf("Parent's parent PID: %jd\n", (intmax_t)getppid());
            printf("fork return value: %jd\n", (intmax_t)pid);
        }
        else {                  /* child process */
            printf("Child PID: %jd\n", (intmax_t)getpid());
            printf("Child's parent PID: %jd\n", (intmax_t)getppid());
        }

        printf("Common code...\n");

        sleep(1);

        return 0;
    }

    void exit_sys(const char *msg)
    {
        perror(msg);
        exit(EXIT_FAILURE);
    }

``fork`` işleminde en fazla kafa karıştıran noktalardan biri ``fork`` fonksiyonundan iki akışın çıkması durumudur.
Burada genellikle yeni öğrenenlerin gözden kaçırdığı birkaç nokta vardır:

| **1.** ``fork`` sırasında ``fork`` işlemini yapan prosesin (yani üst prosesin) tüm bellek alanının (onun kod, data, stack ve
   heap alanlarının) özdeş bir kopyası oluşturulmaktadır. Yani ``fork`` işlemini yapan prosesin kod, data, stack ve heap
   alanlarının hepsi alt proseste de bulunmaktadır. Örneğin:

   .. code-block:: c

       if ((pid = fork()) == -1)
           exit_sys("fork");
       if (pid != 0) {
           /* ... */
       }
       else {
           /* ... */
       }

   Programcının yazdığı bu kodun ``fork`` sonrasındaki kısmı hem üst proses hem de alt proses tarafından
   çalıştırılmaktadır. Yani bu kod hem üst proseste hem de alt proseste bulunacaktır. Bizim buradaki temel amacımız
   ``fork`` çıkışında *kodu aynı olan iki farklı prosese* farklı şeyleri yaptırmaktır. İşte bunu ``fork`` fonksiyonunun
   geri dönüş değerini kontrol ederek sağlayabilmekteyiz.

| **2.** Yeni öğrenen kişilere iki prosesin de ``fork`` fonksiyonundan çıkması tuhaf gelebilmektedir. Aslında burada bir
   tuhaflık yoktur. Şöyle ki: Prosesin yaratılması ve bellek alanlarının kopyalanması zaten ``fork`` içerisinde
   yapılmaktadır. ``fork`` fonksiyonunu çağıran proses (üst proses) ``fork`` fonksiyonundan çıkacaktır. Kopyası
   çıkartılan alt prosesin çalışması da ``fork`` içerisinden başlatılmaktadır. Bu durumda alt proses de ``fork``
   fonksiyonundan çıkacaktır. Çatallanmanın ``fork`` içerisinde yapıldığına dikkat ediniz.

Tabii ``fork`` fonksiyonundan çıkınca artık üst proses ile alt prosesin yaşamları farklı olabilmektedir. Örneğin üst
proses bir global değişkenin değerini değiştirse alt proses bunu değişmiş olarak görmez. Çünkü o global değişkenin üst
proseste ve alt proseste artık farklı kopyaları vardır. Üst proses kendi global değişkenini değiştirmektedir. Yani
``fork`` işleminden çıkıldığında üst ve alt prosesin her şeyi aynı olsa da artık bunlar kendi yollarına gideceklerdir.
(Klon makinesinden çıkar çıkmaz iki kişinin her şeyi aynıdır. Ancak bundan sonra bu kişiler bağımsız kişiler oldukları
için başlarına farklı olaylar gelecektir. Birisinin maruz kaldığı bir duruma diğeri maruz kalmayacaktır.)

Aşağıdaki örnekte ``fork`` işlemi sonrasında üst proses ``g_x`` global değişkenine yeni bir değer atamıştır. Sonra alt
proseste bu global değişkenin değeri yazdırılmıştır. Tabii alt proses üst prosesin yaptığı bu değişikliği görmeyecektir.
Çünkü aslında iki prosesin de bellek alanları tamamen ``fork`` içerisinde klonlama sırasında ayrıştırılmıştır.

.. code-block:: c

    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>

    void exit_sys(const char *msg);

    int g_x = 10;

    int main(void)
    {
        pid_t pid;

        if ((pid = fork()) == -1)
            exit_sys("fork");

        if (pid != 0) {         /* parent process */
            g_x = 100;
        }
        else {                  /* child process */
            sleep(1);
            printf("%d\n", g_x);    /* 10 */
        }

        printf("Common code...\n");

        sleep(1);
        

        return 0;
    }

    void exit_sys(const char *msg)
    {
        perror(msg);
        exit(EXIT_FAILURE);
    }
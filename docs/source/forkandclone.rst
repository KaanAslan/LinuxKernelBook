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
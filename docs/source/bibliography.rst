=========
Kaynaklar
=========

Linux çekirdeği konusunda yararlanabileceğiniz ek kaynakların listesini aşağıda veriyoruz. Bunların arasında en ayrıntılı
olanı *Understandibg the Linux Kernel* kitabıdır. Bu kitabın üç baskısı yapılmıştır. Birincisi çekirdeğin 2.2'li versiyonlarına, 
ikincisi 2.4 versiyonlarına ve üçüncüsü de 2.6'lı versiyonlarına ilişkindir. Ancak 2.6'dan sonra çekirdekte çeşitli alt sistemlerde
değişiklikler yapıldığı için bu kitap Linux çekirdeğinin güncel versiyonlarını tam olarak yansıtmamaktadır. 

İşletim Sistemleri Teorisi
==========================

| [1] A. S. Tanenbaum, *Modern Operating Systems*, 4. baskı.
|     Upper Saddle River, NJ, ABD: Pearson, 2014. ISBN: 978-0-133-59162-0.
| [2] A. S. Tanenbaum ve H. Bos, *Modern Operating Systems*, 3. baskı.
|     Upper Saddle River, NJ, ABD: Prentice Hall, 2007. ISBN: 978-0-136-00663-3.
| [3] A. Silberschatz, P. B. Galvin ve G. Gagne, *Operating System Concepts*, 10. baskı.
|     Hoboken, NJ, ABD: Wiley, 2018. ISBN: 978-1-119-32091-3.
| [4] W. Stallings, *Operating Systems: Internals and Design Principles*, 9. baskı.
|     Upper Saddle River, NJ, ABD: Pearson, 2018. ISBN: 978-0-134-67095-2.
| [5] R. H. Arpaci-Dusseau ve A. C. Arpaci-Dusseau, *Operating Systems: Three Easy Pieces*.
|     Madison, WI, ABD: Arpaci-Dusseau Books, 2018.
|     Çevrimiçi (ücretsiz): https://pages.cs.wisc.edu/~remzi/OSTEP/


Understanding the Linux Kernel
==============================

| [6] D. P. Bovet ve M. Cesati, *Understanding the Linux Kernel*, 1. baskı.
|     Sebastopol, CA, ABD: O'Reilly Media, 2000. ISBN: 978-0-596-00002-5.
| [7] D. P. Bovet ve M. Cesati, *Understanding the Linux Kernel*, 2. baskı.
|     Sebastopol, CA, ABD: O'Reilly Media, 2002. ISBN: 978-0-596-00213-5.
| [8] D. P. Bovet ve M. Cesati, *Understanding the Linux Kernel*, 3. baskı.
|     Sebastopol, CA, ABD: O'Reilly Media, 2005. ISBN: 978-0-596-00565-5.

.. note::

   3. baskı Linux 2.6.11 çekirdeğini kapsar ve serinin son baskısıdır.
   Linux 5.x / 6.x için kernel.org resmi dokümantasyonu ve LWN.net
   makaleleri tamamlayıcı kaynak olarak kullanılmalıdır.

Linux Device Drivers
====================

| [9]  A. Rubini ve J. Corbet, *Linux Device Drivers*, 1. baskı.
|      Sebastopol, CA, ABD: O'Reilly Media, 1998.
| [10] A. Rubini ve J. Corbet, *Linux Device Drivers*, 2. baskı.
|      Sebastopol, CA, ABD: O'Reilly Media, 2001.
| [11] J. Corbet, A. Rubini ve G. Kroah-Hartman, *Linux Device Drivers*, 3. baskı.
|      Sebastopol, CA, ABD: O'Reilly Media, 2005. ISBN: 978-0-596-00590-7.
|      Çevrimiçi (ücretsiz): https://lwn.net/Kernel/LDD3/

.. note::

   3. baskı Linux 2.6 çekirdeğini hedefler ve O'Reilly tarafından
   ücretsiz olarak çevrimiçi yayınlanmaktadır. 4. baskı henüz
   yayınlanmamıştır.

Kernel Internals ve Genel Mimari
================================

| [12] R. Love, *Linux Kernel Development*, 3. baskı.
|      Upper Saddle River, NJ, ABD: Addison-Wesley, 2010. ISBN: 978-0-672-32946-3.
| [13] M. Gorman, *Understanding the Linux Virtual Memory Manager*.
|      Upper Saddle River, NJ, ABD: Prentice Hall, 2004. ISBN: 978-0-131-45348-5.
|      Çevrimiçi (ücretsiz): https://www.kernel.org/doc/gorman/
| [14] W. Mauerer, *Professional Linux Kernel Architecture*.
|      Indianapolis, IN, ABD: Wrox Press, 2008. ISBN: 978-0-470-34343-2.
| [15] G. Kroah-Hartman, *Linux Kernel in a Nutshell*.
|      Sebastopol, CA, ABD: O'Reilly Media, 2006.
|      Çevrimiçi (ücretsiz): http://www.kroah.com/lkn/

Linux Kernel Programming
========================

| [16] K. N. Billimoria, *Linux Kernel Programming: A Comprehensive Guide to Kernel Internals, Writing Kernel Modules, and Kernel Synchronization*,
|      1. baskı. Birmingham, İngiltere: Packt Publishing, 2021.
| [17] K. N. Billimoria, *Linux Kernel Programming Part 2: Writing Character Device Drivers*,
|      1. baskı. Birmingham, İngiltere: Packt Publishing, 2021.

Linux Kernel Debugging
======================

| [18] K. N. Billimoria, *Linux Kernel Debugging: Leverage Proven Tools and Advanced Techniques to Effectively Debug Linux Kernels and Kernel Modules*,
|      1. baskı. Birmingham, İngiltere: Packt Publishing, 2023.

.. note::

   Billimoria'nın üç kitabı ([16], [17], [18]) birbirini tamamlar
   niteliktedir: kernel programlama → karakter sürücüleri → kernel hata
   ayıklama şeklinde doğal bir okuma sırası oluşturur. [18] numaralı
   *Linux Kernel Debugging* kitabı ``ftrace``, ``kprobes``, ``KASAN``,
   ``lockdep`` ve ``kdump`` araçlarını kaynak kod düzeyinde ele alır.

Sistem Programlama ve Kullanıcı Alanı Kaynakları
================================================

| [19] M. Kerrisk, *The Linux Programming Interface*.
|      San Francisco, CA, ABD: No Starch Press, 2010. ISBN: 978-1-593-27220-3.
| [20] W. R. Stevens ve S. A. Rago, *Advanced Programming in the UNIX Environment*,
|      3. baskı. Upper Saddle River, NJ, ABD: Addison-Wesley, 2013. ISBN: 978-0-321-63773-4.
| [21] B. Ward, *How Linux Works: What Every Superuser Should Know*, 3. baskı.
|      San Francisco, CA, ABD: No Starch Press, 2021.
| [22] J. Levine, *Linkers and Loaders*.
|      San Francisco, CA, ABD: Morgan Kaufmann, 2000.

Çevrimiçi Kaynaklar
===================

| [23] The Linux Kernel Organization, "The Linux Kernel Documentation,"
|      Erişim: https://www.kernel.org/doc/html/latest/ [Mayıs 2026].
| [24] M. Gorman, "Understanding the Linux Virtual Memory Manager,"
|      Erişim: https://www.kernel.org/doc/gorman/ [Mayıs 2026].
| [25] LWN.net, "Kernel development news and articles,"
|      Erişim: https://lwn.net [Mayıs 2026].
| [26] LWN.net, "Kernel Index — Memory Management,"
|      Erişim: https://lwn.net/Kernel/Index/#Memory_management [Mayıs 2026].
| [27] Bootlin, "Elixir Cross Referencer — Linux Kernel Source,"
|      Erişim: https://elixir.bootlin.com/linux/latest/source [Mayıs 2026].
| [28] KernelNewbies, "Linux Kernel Newbies,"
|      Erişim: https://kernelnewbies.org [Mayıs 2026].
| [29] R. H. Arpaci-Dusseau ve A. C. Arpaci-Dusseau, "Operating Systems: Three Easy Pieces,"
|      Erişim: https://pages.cs.wisc.edu/~remzi/OSTEP/ [Mayıs 2026].
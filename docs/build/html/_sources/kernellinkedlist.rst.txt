=========================================================
Çekirdekteki Bağlı Liste Gerçekleştirimi
=========================================================

Bu bölümde Linux çekirdeğindeki bağlı liste gerçekleştirimleri üzerinde duracağız.

Bağlı Listeler
==============

Çekirdeğin en önemli veri yapılarından biri bağlı listelerdir. Genel olarak çekirdekteki neredeyse tüm
bağlı listeler *çift bağlı (doubly linked)* biçimde kullanılmaktadır. Önce bağlı listelerin Linux
çekirdeğindeki gerçekleştirimleri üzerinde duracağız.

Aralarında öncelik-sonralık ilişkisi olan veri yapılarına *liste (list)* tarzı veri yapıları denilmektedir.
Örneğin bu tanıma göre diziler de "liste tarzı" veri yapılarıdır. Liste tarzı veri yapılarının en yaygın
kullanılanlarından biri *bağlı liste (linked list)* denilen veri yapısıdır. Önceki elemanın sonraki
elemanın yerini gösterdiği dolayısıyla elemanların ardışıl olma zorunluluğunun ortadan kaldırıldığı
listelere "bağlı liste" denilmektedir. Dizi elemanlarının bellekte fiziksel olarak ardışıl biçimde
bulunduğunu anımsayınız. Bağlı listeler adeta "elemanları bellekte ardışıl olmak zorunda olmayan
diziler" gibidir.

Bağlı listelerin her elemanına *düğüm (node)* denilmektedir. Bağlı listelerde her düğüm sonraki
düğümün yerini tuttuğuna göre ilk elemanın yeri biliniyorsa liste elemanlarının hepsine erişilebilmektedir:

.. graphviz::

   digraph single_linked {
       rankdir=LR;
       graph [bgcolor="transparent", pad="0.2"];
       node  [shape=box, style="rounded,filled", fillcolor="#DDEEFF",
              fontname="monospace", fontsize=12, width=1.0, height=0.5];
       edge  [color="#4477AA", arrowsize=0.9, penwidth=1.5];

       head [label="head", fillcolor="#AACCFF", fontname="monospace bold"];
       n1   [label="node"];
       n2   [label="node"];
       n3   [label="node"];
       n4   [label="node"];
       nil  [label="NULL", shape=plaintext, fontname="monospace", fontcolor="#888888"];

       head -> n1 -> n2 -> n3 -> n4 -> nil;
   }

Her düğümün yalnızca sonraki düğümün değil aynı zamanda önceki düğümün yerini de tuttuğu bağlı
listelere *çift bağlı listeler (doubly linked lists)* denilmektedir. Çift bağlı listelerde belli bir
düğümün adresini biliyorsak yalnızca ileriye doğru değil, geriye doğru da gidebiliriz:

.. graphviz::

   digraph double_linked {
       rankdir=LR;
       graph [bgcolor="transparent", pad="0.2"];
       node  [shape=box, style="rounded,filled", fillcolor="#DDEEFF",
              fontname="monospace", fontsize=12, width=1.0, height=0.5];
       edge  [color="#4477AA", arrowsize=0.9, penwidth=1.5];

       head [label="head", fillcolor="#AACCFF", fontname="monospace bold"];
       n1   [label="node"];
       n2   [label="node"];
       n3   [label="node"];
       n4   [label="node"];
       nil  [label="NULL", shape=plaintext, fontname="monospace", fontcolor="#888888"];

       head -> n1   [dir=both];
       n1   -> n2   [dir=both];
       n2   -> n3   [dir=both];
       n3   -> n4   [dir=both];
       n4   -> nil  [dir=forward];
   }

Çift bağlı listelere ilişkin bir düğümün bellekte daha fazla yer kaplayacağına dikkat ediniz. Çift bağlı
listelerin tek bağlı listelere göre en önemli özelliği "adresi bilinen bir düğümün" silinebilmesidir.
Tek bağlı listelerde bu durum mümkün değildir. Uygulamalarda ve özellikle çekirdek kodlarında buna çok
sık gereksinim duyulmaktadır.

Eğer bir bağlı listede son eleman da ilk elemanı gösteriyorsa bu tür bağlı listelere *döngüsel bağlı
listeler (circular linked lists)* denilmektedir.


Bağlı Listelere Neden Gereksinim Duyulur?
==========================================

Peki bağlı listelere neden gereksinim duyulmaktadır? Diziler varken bağlı listelere gerek var mıdır?
Dizilerle bağlı listeler arasındaki farklılıkları, benzerlikleri ve bağlı listelere neden gereksinim
duyulduğunu birkaç maddede açıklayabiliriz:

1. **Bellek parçalanması sorunu:** Diziler ardışıl alana gereksinim duymaktadır. Ancak belleğin
   bölündüğü (fragmente olduğu) durumlarda bellekte yeteri kadar küçük boş alanlar olduğu halde bunlar
   ardışıl olmadığı için dizi tahsisatı mümkün olamamaktadır. Bu tür durumlarda ardışıllık gereksinimi
   olmayan bağlı listeler kullanılabilir. Özellikle heap gibi bir alanda çok sayıda dinamik dizi bellek
   kullanımı bakımından verimsizliğe yol açabilmektedir. Bu dinamik diziler zamanla büyüdükçe birbirini
   engeller hale gelebilmektedir. İşte uzunluğu baştan belli olmayan çok sayıda dizinin oluşturulacağı
   durumlarda dinamik diziler yerine bağlı listeler bellek kullanımı bakımından toplamda daha iyi
   performans gösterebilmektedir. Dinamik dizilerde büyütme sırasında bloklar yer değiştirebileceği için
   bu işlem yavaştır.

2. **Araya ekleme ve silme verimliliği:** Dizilerde araya eleman ekleme (insert etme) ve aradaki bir
   elemanı silme dizinin kaydırılmasına yol açacağından yavaş bir işlemdir. Teknik olarak dizilerde eleman
   insert etme ve eleman silme O(N) karmaşıklıkta bir işlemdir. Halbuki bağlı listelerde eğer düğümün yeri
   biliniyorsa bu işlem O(1) karmaşıklıkta (yani döngü olmadan tekil işlemlerle) yapılabilmektedir. O halde
   araya eleman eklemenin ve aradan eleman silmenin çok yapıldığı sistemlerde diziler yerine bağlı listeler
   tercih edilebilmektedir. Çekirdek veri yapılarında araya eleman ekleme ve aradan eleman silme gibi
   işlemler çok yoğun yapılmaktadır.

3. **İndeksle erişim yavaşlığı:** Bağlı listelerde belli bir indeksteki elemana erişmek O(N) karmaşıklıkta
   bir işlemdir. Halbuki dizilerde elemana erişim O(1) karmaşıklıkta yani çok hızlıdır. O halde belli bir
   indeks değeri ile elemana erişimin yoğun yapıldığı durumlarda bağlı listeler yerine diziler tercih
   edilmelidir.

4. **Ek bellek maliyeti:** Bağlı listeler toplamda bellekte daha fazla yer kaplama eğilimindedir. Çünkü
   bağlı listenin her düğümü sonraki (ve duruma göre önceki) elemanın yerini de tutmaktadır.

O halde bağlı listeler tipik olarak şu durumlarda dizilere tercih edilmelidir:

- Eleman insert etmenin ve eleman silmenin sık yapıldığı durumlarda.
- Uzunluğu baştan belli olmayan çok sayıda dizinin kullanıldığı durumlarda.
- İndeks yoluyla erişimin az yapıldığı durumlarda.
- Toplam bellek miktarının yeteri kadar fazla olduğu sistemlerde.

İşte tüm yukarıdaki nedenlerden dolayı bağlı listeler çekirdek için en önemli veri yapılarından biridir.


Linux Çekirdeğindeki Bağlı Liste Gerçekleştirimi
==================================================

Linux çekirdeğinde bağlı liste gerçekleştirimi ``include/linux/list.h`` dosyasında yapılmıştır. Bu dosya
içerisindeki fonksiyonlar ``static inline`` biçiminde tanımlanmıştır. Çekirdek derlemesi sırasında
derleyicinin optimizasyon seçeneği ayarlandığı için derleyici buradaki inline fonksiyonları sanki bir makro
gibi koda açmaktadır.

Linux çekirdeğindeki bağlı listelerde düğümler ``list_head`` isimli bir yapıyla temsil edilmektedir:

.. code-block:: c

   struct list_head {
       struct list_head *next;
       struct list_head *prev;
   };

Aslında belli yapılar değil, bu ``list_head`` yapıları bağlı liste içerisinde birbirine bağlanmaktadır:

.. graphviz::

   digraph kernel_list {
       rankdir=LR;
       graph [bgcolor="transparent", pad="0.3"];
       node  [shape=record, style="rounded,filled", fontname="monospace", fontsize=11,
              height=0.6];
       edge  [color="#336699", arrowsize=0.85, penwidth=1.5];

       root [label="{list_head\n(kök) | {<p>prev | <n>next}}",
             fillcolor="#AACCFF"];
       n1   [label="{list_head | {<p>prev | <n>next}}", fillcolor="#DDEEFF"];
       n2   [label="{list_head | {<p>prev | <n>next}}", fillcolor="#DDEEFF"];
       n3   [label="{list_head | {<p>prev | <n>next}}", fillcolor="#DDEEFF"];
       n4   [label="{list_head | {<p>prev | <n>next}}", fillcolor="#DDEEFF"];

       /* next bağlantıları: soldan sağa */
       root:n -> n1:n   [dir=forward, color="#336699"];
       n1:n   -> n2:n   [dir=forward, color="#336699"];
       n2:n   -> n3:n   [dir=forward, color="#336699"];
       n3:n   -> n4:n   [dir=forward, color="#336699"];
       n4:n   -> root:n [dir=forward, color="#336699",
                         constraint=false, style=dashed];

       /* prev bağlantıları: sağdan sola */
       n1:p   -> root:p [dir=forward, color="#AA4444"];
       n2:p   -> n1:p   [dir=forward, color="#AA4444"];
       n3:p   -> n2:p   [dir=forward, color="#AA4444"];
       n4:p   -> n3:p   [dir=forward, color="#AA4444"];
       root:p -> n4:p   [dir=forward, color="#AA4444",
                         constraint=false, style=dashed];
   }

Tabii eğer bu ``list_head`` yapıları başka bir yapının (buna asıl yapı diyelim) içerisindeyse bu durumda
aslında bir ``list_head`` yapısının adresi asıl yapının bir elemanının adresi haline gelmektedir. Biz C'de
bir yapının bir elemanının adresini biliyorsak kolaylıkla o yapının başlangıç adresini elde edebiliriz.
Çünkü yapı elemanları ardışıldır ve standart ``offsetof`` makrosuyla belli bir yapı elemanının yapının
başlangıcından itibaren hangi offset'te bulunduğu bilgisi elde edilebilmektedir. ``offsetof`` makrosu
``<stddef.h>`` içerisinde aşağıdakine benzer biçimde tanımlanmıştır:

.. code-block:: c

   #define offsetof(type, member) ((size_t)&(((type *)0)->member))

``offsetof`` makrosunun birinci parametresi yapının tür ismini, ikinci parametresi ilgili yapı elemanının
ismini almaktadır. Tabii ``offsetof`` makrosu yalnızca ``size_t`` türünden bir byte offset'i vermektedir.
Elemanın adresinin makroyla elde edilen bu değerden çıkartılarak tür dönüştürmesinin yapılması gerekir.
İşte bunun için Linux çekirdeğinde ``container_of`` isimli bir makro bulundurulmuştur. Bu makronun basit
yazımı şöyle yapılabilir:

.. code-block:: c

   #define container_of(ptr, type, member) ((type *)((char *)ptr - myoffsetof(type, member)))

``container_of`` makrosunun birinci parametresi yapı elemanının adresini, ikinci parametresi yapının tür
ismini ve üçüncü parametresi de ilgili yapı elemanının ismini almaktadır. Bu makro ikinci parametresine
girilmiş olan yapı türünden bir adres vermektedir.

``container_of`` makrosunu ``list_entry`` ismiyle de kullanabilirsiniz:

.. code-block:: c

   #define list_entry(ptr, type, member) container_of(ptr, type, member)

Bağlı Liste Başlatma
---------------------

Linux çekirdeğindeki bağlı listeler kullanılırken önce bir başlangıç düğümünün oluşturulması gerekir.
Başlangıç düğümünde ``next`` ve ``prev`` göstericilerinin başlangıç düğümünün kendisini göstermesi
gerekir. Örneğin:

.. code-block:: c

   struct list_head head = {&head, &head};

Bu ilkdeğer verme C'de geçerlidir. Çünkü C'de bir değişken faaliyet alanına ``=`` atomu ile ilkdeğer
verme kısmından önce sokulmaktadır. ``list.h`` dosyasında bu işlemi yapan aşağıdaki gibi bir makro da
bulundurulmuştur:

.. code-block:: c

   #define LIST_HEAD_INIT(name) {&(name), &(name)}

Bu durumda başlangıç düğümü bu makroyla şöyle de oluşturulabilir:

.. code-block:: c

   struct list_head head = LIST_HEAD_INIT(head);

Aslında bu tanımlamanın tamamını yapan aşağıdaki gibi bir makro da bulundurulmuştur:

.. code-block:: c

   #define LIST_HEAD(name) \
       struct list_head name = LIST_HEAD_INIT(name)

O halde biz başlangıç düğümünü basit bir biçimde şöyle oluşturabiliriz:

.. code-block:: c

   LIST_HEAD(head);

Linux'un bağlı liste gerçekleştiriminde ``next`` ve ``prev`` göstericilerinde ``NULL`` adres
kullanılmamıştır. Son düğümün ``next`` göstericisi ``NULL`` yerine başlangıç düğümünü, ilk düğümün
``prev`` göstericisi de ``NULL`` yerine son düğümü göstermektedir. Yani aslında bağlı liste
gerçekleştirimi döngüsel (circular) gibidir. Herhangi bir düğümden başlanarak başlangıç düğümü de
atlanırsa tam dolaşım sağlanabilir. Bağlı listenin başlangıç düğümünün ``prev`` göstericisi de son
düğümü göstermektedir.


Düğüm Ekleme
-------------

Bağlı listenin başına ``list_head`` düğümünü eklemek için ``list_add`` fonksiyonu kullanılmaktadır:

.. code-block:: c

   static inline void list_add(struct list_head *new, struct list_head *head)
   {
       __list_add(new, head, head->next);
   }

Fonksiyonun birinci parametresi eklenecek düğümün adresini, ikinci parametresi başlangıç düğümünün
adresini almaktadır.

Çekirdek kodlarında iki alt tire ile başlayan fonksiyonlar aşağı seviyeli fonksiyonlardır. Yani doğrudan
çağrılmayan ancak başka fonksiyonların içerisinden dolaylı biçimde çağrılan fonksiyonlardır. Buradaki
``__list_add`` fonksiyonu şöyle yazılmıştır:

.. code-block:: c

   static inline void __list_add(struct list_head *new,
                 struct list_head *prev,
                 struct list_head *next)
   {
       if (!__list_add_valid(new, prev, next))
           return;

       next->prev = new;
       new->next = next;
       new->prev = prev;
       WRITE_ONCE(prev->next, new);
   }

Buradaki ``WRITE_ONCE`` makrosu atama işlemini volatile erişimle yapmaktadır. ``WRITE_ONCE(a, b)``
çağrısını ``a = b`` gibi düşünebilirsiniz.

Bağlı listenin sonuna düğüm eklemek için ``list_add_tail`` fonksiyonu kullanılmaktadır:

.. code-block:: c

   static inline void list_add_tail(struct list_head *new, struct list_head *head)
   {
       __list_add(new, head->prev, head);
   }


Liste Dolaşımı
--------------

Peki biz bağlı listeyi nasıl dolaşabiliriz? Başlangıç düğümünü geçerek sürekli ileriye gidersek son
düğüm de başlangıç düğümünü gösterdiğine göre dolaşımı aşağıdaki gibi bir for döngüsüyle yapabiliriz:

.. code-block:: c

   struct list_head *lh;

   for (lh = head.next; lh != &head; lh = lh->next) {
       /* ... */
   }

Tabii böyle bir döngüde dolaşım yapılırken aslında biz her yinelemede ilgili yapının başlangıç adresini
değil ``list_head`` yapısının başlangıç adresini elde ederiz. ``container_of`` makrosu ile bu adresin
yapı adresine dönüştürülmesi gerekir. Örneğin biz ``struct SAMPLE`` türünden yapı nesnelerini birbirine
bağlamış olalım:

.. code-block:: c

   LIST_HEAD(head);

   struct SAMPLE {
       int a;
       struct list_head link;
   };

Eklemeleri şöyle yapmış olalım:

.. code-block:: c

   struct SAMPLE *ps;

   for (int i = 0; i < 10; ++i) {
       if ((ps = (struct SAMPLE *)malloc(sizeof(struct SAMPLE))) == NULL) {
           fprintf(stderr, "cannot allocate memory!...\n");
           exit(EXIT_FAILURE);
       }
       ps->a = i;
       list_add_tail(&ps->link, &head);
   }

.. note::

   Çekirdek kodlarında *malloc* gibi kullanıcı modu fonksiyonları kullanılamaz. Ancak burada yalnızca
   anlaşılır bir test örneği verilmektedir.

``struct SAMPLE`` yapımızdaki ``link`` elemanı ``list_head`` yapılarını birbirine bağlamak için
bulundurulmuştur. Örneğimizdeki ``list_add_tail`` fonksiyonunda ekleme yapılacak düğümün ``SAMPLE``
yapısının içerisindeki ``link`` elemanının adresi olduğuna dikkat ediniz. Şimdi dolaşımı şöyle
yapabiliriz:

.. code-block:: c

   struct SAMPLE *ps;
   struct list_head *lh;

   for (lh = head.next; lh != &head; lh = lh->next) {
       ps = container_of(lh, struct SAMPLE, link);
       /* ... */
   }

Burada artık ``ps`` göstericisi ``list_head`` nesnesini değil ``struct SAMPLE`` nesnesini göstermektedir.
Aslında ``list.h`` dosyası içerisinde buradaki döngüyü oluşturan ``list_for_each`` isimli bir makro da
bulundurulmuştur:

.. code-block:: c

   static inline int list_is_head(const struct list_head *list,
                                  const struct list_head *head)
   {
       return list == head;
   }

   #define list_for_each(pos, head) \
       for (pos = (head)->next; !list_is_head(pos, (head)); pos = pos->next)

Makronun birinci parametresi ``list_head`` türünden bir göstericiyi, ikinci parametresi başlangıç
düğümünün adresini almaktadır. Döngünün her yinelenmesinde bu göstericiye sonraki düğümün ``list_head``
adresi atanmaktadır. Örneğin:

.. code-block:: c

   struct list_head *lh;

   list_for_each(lh, &head) {
       ps = container_of(lh, struct SAMPLE, link);
       printf("%d\n", ps->a);
   }

Aslında çekirdekteki ``list.h`` dosyası içerisinde yukarıdaki dolaşımı tek hamlede yapan
``list_for_each_entry`` isimli bir makro da bulunmaktadır:

.. code-block:: c

   #define list_for_each_entry(pos, head, member)              \
       for (pos = list_first_entry(head, typeof(*pos), member); \
            !list_entry_is_head(pos, head, member);             \
            pos = list_next_entry(pos, member))

Makronun birinci parametresi asıl yapı türünden bir göstericidir; makro her yinelemede bu göstericiye
sonraki düğümün adresini yerleştirmektedir. Makronun ikinci parametresi başlangıç düğümünün adresini,
üçüncü parametresi ise yapı içerisindeki ``list_head`` elemanın ismini belirtmektedir. Bu makronun
eşdeğeri bazı ayrıntılar ihmal edilerek şöyle de yazılabilir:

.. code-block:: c

   #define my_list_for_each_entry(pos, head, member)                                            \
       for (pos = container_of((head)->next, typeof(*pos), member); &(pos)->member != head;     \
           pos = container_of((pos)->member.next, typeof(*pos), member))

.. note::

   C standartlarında bir ifadenin türünü veren bir tür belirleyicisi yoktu. C++'a C++11 ile birlikte
   ``decltype`` ismi ile böyle bir belirleyici eklendi. gcc derleyicileri uzun süredir bu işi yapan
   ``typeof`` isimli belirleyiciyi desteklemektedir. Nihayet C'ye de C23 ile birlikte resmi olarak
   ``typeof`` belirleyicisi eklenmiştir. Makroda türün ``typeof(*pos)`` ifadesiyle elde edildiğine dikkat
   ediniz.

Bu makro ile dolaşım şöyle sağlanabilir:

.. code-block:: c

   struct SAMPLE *ps;

   list_for_each_entry(ps, &head, link) {
       /* ... */
   }

.. tip::

   Bağlı liste makrolarının ve fonksiyonlarının isimlerinin sonunda *entry* sözcüğü varsa bu makro ya da
   fonksiyon asıl yapıya ilişkin adres, yoksa ``list_head`` türünden adres verip almaktadır.

Ayrıca ``list.h`` içerisinde ``list_for_each_entry_safe`` isimli bir döngü makrosu da
bulundurulmuştur. Bu makro eğer liste boşsa hiç dolaşım yapmamaktadır. Makro aşağıdaki gibi
yazılmıştır:

.. code-block:: c

   #define list_for_each_entry_safe(pos, n, head, member)          \
       for (pos = list_first_entry(head, typeof(*pos), member),    \
            n = list_next_entry(pos, member);                       \
            !list_entry_is_head(pos, head, member);                 \
            pos = n, n = list_next_entry(n, member))

Makronun birinci elemanı dolaşımda kullanılacak asıl yapı türünden göstericiyi almaktadır. Makronun
ikinci parametresi de asıl yapı göstericidir. Üçüncü ve dördüncü parametreler sırasıyla kök düğümün
adresi ve bağ düğümünün ismini almaktadır.


Düğüm Silme
------------

Bağlı listeden bir düğümü silmek için ``list_del`` fonksiyonu kullanılmaktadır. Fonksiyon şöyle
tanımlanmıştır:

.. code-block:: c

   static inline void __list_del(struct list_head *prev, struct list_head *next)
   {
       next->prev = prev;
       WRITE_ONCE(prev->next, next);
   }

   static inline void __list_del_entry(struct list_head *entry)
   {
       if (!__list_del_entry_valid(entry))
           return;

       __list_del(entry->prev, entry->next);
   }

   static inline void list_del(struct list_head *entry)
   {
       __list_del_entry(entry);
       entry->next = LIST_POISON1;
       entry->prev = LIST_POISON2;
   }

Fonksiyonun parametresi silinecek düğüme ilişkin ``list_head`` nesnesinin adresini almaktadır. Burada
silinen düğümdeki ``next`` ve ``prev`` göstericilerine özel bazı değerlerin atandığını görüyorsunuz. Bu
değerler silinmiş düğümün kullanılması durumunda *page fault* oluşmasına yol açmaktadır; dolayısıyla bir
çeşit debug mekanizması oluşturmak amacıyla atandıklarını söyleyebiliriz.


Araya Düğüm Ekleme
-------------------

Bağlı listenin arasına düğüm ekleyen ayrı bir insert fonksiyonu yoktur. Zaten ``list_add`` fonksiyonu
araya ekleme işlemini de yapmaktadır. Örneğin biz araya şöyle ekleme yapabiliriz:

.. code-block:: c

   list_add(&ps->link, &ps_insert->link);

Burada ``ps`` eklenecek düğümün asıl yapı adresini, ``ps_insert`` ise önüne eklemenin yapılacağı asıl
yapı adresini belirtmektedir.

Bir bağlı listeyi tümden serbest bırakmak için düğümlerin tek tek serbest bırakılması gerekmektedir.
Buradaki düğümler aslında başka yapıların içerisinde olduğuna göre liste içerisindeki o yapı nesnelerinin
serbest bırakılması gerekir.


Tam Örnek: Kullanıcı Alanında Bağlı Liste Kullanımı
=====================================================

Aşağıda kullanıcı alanında çekirdekteki bağlı liste kullanımına bir örnek verilmiştir.

.. code-block:: c

   #include <stdio.h>
   #include <stdlib.h>
   #include <stddef.h>

   struct list_head {
       struct list_head *next, *prev;
   };

   #define LIST_HEAD_INIT(name) { &(name), &(name) }

   #define LIST_HEAD(name) \
       struct list_head name = LIST_HEAD_INIT(name)

   #define container_of(ptr, type, member) ({          \
           void *__mptr = (void *)(ptr);               \
           ((type *)(__mptr - offsetof(type, member))); })

   #define list_entry(ptr, type, member) \
       container_of(ptr, type, member)

   #define list_entry_is_head(pos, head, member) \
       (&pos->member == (head))

   #define list_first_entry(ptr, type, member) \
       list_entry((ptr)->next, type, member)

   #define list_next_entry(pos, member) \
       list_entry((pos)->member.next, typeof(*(pos)), member)

   #define list_for_each(pos, head) \
       for (pos = (head)->next; !list_is_head(pos, (head)); pos = pos->next)

   #define list_for_each_entry(pos, head, member)              \
       for (pos = list_first_entry(head, typeof(*pos), member); \
           !list_entry_is_head(pos, head, member);              \
           pos = list_next_entry(pos, member))

   #define list_for_each_entry_safe(pos, n, head, member)          \
       for (pos = list_first_entry(head, typeof(*pos), member),    \
            n = list_next_entry(pos, member);                       \
            !list_entry_is_head(pos, head, member);                 \
            pos = n, n = list_next_entry(n, member))

   #define my_list_for_each_entry(pos, head, member)                                        \
       for (pos = container_of((head)->next, typeof(*pos), member); &(pos)->member != head; \
               pos = container_of((pos)->member.next, typeof(*pos), member))

   static inline int list_is_head(const struct list_head *list,
                                  const struct list_head *head)
   {
       return list == head;
   }

   static inline void __list_add(struct list_head *new,
                   struct list_head *prev,
                   struct list_head *next)
   {
       next->prev = new;
       new->next = next;
       new->prev = prev;
       prev->next = new;
   }

   static inline void list_add(struct list_head *new, struct list_head *head)
   {
       __list_add(new, head, head->next);
   }

   static inline void list_add_tail(struct list_head *new, struct list_head *head)
   {
       __list_add(new, head->prev, head);
   }

   static inline void __list_del(struct list_head *prev, struct list_head *next)
   {
       next->prev = prev;
       prev->next = next;
   }

   static inline void __list_del_entry(struct list_head *entry)
   {
       __list_del(entry->prev, entry->next);
   }

   static inline void list_del(struct list_head *entry)
   {
       __list_del_entry(entry);
   }

   LIST_HEAD(head);

   struct SAMPLE {
       int a;
       struct list_head link;
   };

   int main(void)
   {
       struct SAMPLE *ps, *ps_node, *ps_temp, *ps_del, *ps_insert;
       struct list_head *lh;

       for (int i = 0; i < 10; ++i) {
           if ((ps = (struct SAMPLE *)malloc(sizeof(struct SAMPLE))) == NULL) {
               fprintf(stderr, "cannot allocate memory!...\n");
               exit(EXIT_FAILURE);
           }
           ps->a = i;
           list_add_tail(&ps->link, &head);

           if (i == 5)
               ps_del = ps;

           if (i == 7)
               ps_insert = ps;
       }

       list_for_each(lh, &head) {
           ps = container_of(lh, struct SAMPLE, link);
           printf("%d ", ps->a);
       }
       printf("\n");

       list_del(&ps_del->link);

       list_for_each(lh, &head) {
           ps = container_of(lh, struct SAMPLE, link);
           printf("%d ", ps->a);
       }
       printf("\n");

       if ((ps = (struct SAMPLE *)malloc(sizeof(struct SAMPLE))) == NULL) {
           fprintf(stderr, "cannot allocate memory!...\n");
           exit(EXIT_FAILURE);
       }
       ps->a = 100;

       list_add(&ps->link, &ps_insert->link);

       list_for_each(lh, &head) {
           ps = container_of(lh, struct SAMPLE, link);
           printf("%d ", ps->a);
       }
       printf("\n");

       ps_temp = NULL;
       list_for_each_entry_safe(ps, ps_node, &head, link) {
           free(ps_temp);
           ps_temp = ps;
       }

       return 0;
   }


RCU Desteği
===========

Belli bir süreden sonra ``list.h`` dosyasına RCU (Read-Copy-Update) mekanizmasını destekleyecek biçimde
dolaşım yapan ``list_for_each_rcu`` isimli makro da eklenmiştir. Bu makro bir yazıcı varsa okuyucuları
bekletmeden işlem yapabilmeyi sağlamaktadır. *Read-Copy-Update* mekanizması ileride ele alınacaktır.


Eski Çekirdek Sürümlerindeki list.h
=====================================

Çekirdeğin eski sürümlerinde ``list.h`` dosyası oldukça sade idi. Sonra bu dosyanın içeriğinde de bazı
faydalı değişiklikler yapıldı. Ancak bu değişiklikler veri yapısının anlaşılmasını da biraz zorlaştırmıştır.
Örneğin 2.2.26 çekirdeğindeki ``list.h`` dosyası oldukça sade bir biçimde aşağıdaki gibi oluşturulmuştur:

.. code-block:: c

   /* 2.2.26 <list.h> dosyasının içeriği */

   #ifndef _LINUX_LIST_H
   #define _LINUX_LIST_H

   #ifdef __KERNEL__

   /*
    * Simple doubly linked list implementation.
    *
    * Some of the internal functions ("__xxx") are useful when
    * manipulating whole lists rather than single entries, as
    * sometimes we already know the next/prev entries and we can
    * generate better code by using them directly rather than
    * using the generic single-entry routines.
    */

   struct list_head {
       struct list_head *next, *prev;
   };

   #define LIST_HEAD_INIT(name) { &(name), &(name) }

   #define LIST_HEAD(name) \
       struct list_head name = { &name, &name }

   #define INIT_LIST_HEAD(ptr) do { \
       (ptr)->next = (ptr); (ptr)->prev = (ptr); \
   } while (0)

   static __inline__ void __list_add(struct list_head *new,
       struct list_head *prev,
       struct list_head *next)
   {
       next->prev = new;
       new->next = next;
       new->prev = prev;
       prev->next = new;
   }

   static __inline__ void list_add(struct list_head *new, struct list_head *head)
   {
       __list_add(new, head, head->next);
   }

   static __inline__ void list_add_tail(struct list_head *new, struct list_head *head)
   {
       __list_add(new, head->prev, head);
   }

   static __inline__ void __list_del(struct list_head *prev,
                   struct list_head *next)
   {
       next->prev = prev;
       prev->next = next;
   }

   static __inline__ void list_del(struct list_head *entry)
   {
       __list_del(entry->prev, entry->next);
   }

   static __inline__ int list_empty(struct list_head *head)
   {
       return head->next == head;
   }

   static __inline__ void list_splice(struct list_head *list,
                                      struct list_head *head)
   {
       struct list_head *first = list->next;

       if (first != list) {
           struct list_head *last = list->prev;
           struct list_head *at = head->next;

           first->prev = head;
           head->next = first;

           last->next = at;
           at->prev = last;
       }
   }

   #define list_entry(ptr, type, member) \
       ((type *)((char *)(ptr)-(unsigned long)(&((type *)0)->member)))

   #define list_for_each(pos, head) \
       for (pos = (head)->next; pos != (head); pos = pos->next)

   #endif /* __KERNEL__ */

   #endif
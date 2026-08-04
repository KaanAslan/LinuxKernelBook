=================================================================
Sayfa Önbelleği - II. Bölüm :raw-html:`<br>` Geri Yazım İşlemleri
=================================================================

Önceki bölümde sayfa önbelleğindeki sayfalar kirlendiğinde çekirdeğin onları belli periyotlarla diske (blok aygıtına)
flush ettiğini söylemiştik. Bu bölümde bu flush etme mekanizmasının nasıl işletildiği üzerinde duracağız. Linux
çekirdek terminolojisinde kirlenmiş önbellek bloklarının diske yazılması süreci için *flush* sözcüğü yerine daha çok 
*writeback* sözcüğü kullanılmaktadır. Biz de *writeback* sözcüğü yerine Türkçe *geri yazım* sözcüklerini kullanacağız.

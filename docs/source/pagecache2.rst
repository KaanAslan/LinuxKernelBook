=================================================================
Sayfa Önbelleği - II. Bölüm :raw-html:`<br>` Geri Yazım İşlemleri
=================================================================

Önceki bölümde sayfa önbelleğindeki sayfalar kirlendiğinde çekirdeğin onları belli periyotlarla diske (blok aygıtına)
flush ettiğini söylemiştik. Bu bölümde bu flush etme mekanizmasının nasıl işletildiği üzerinde duracağız. Linux
çekirdek terminolojisinde kirlenmiş önbellek bloklarının diske yazılması süreci için *flush* sözcüğü yerine daha çok 
*writeback* sözcüğü kullanılmaktadır. Biz de *writeback* sözcüğü yerine Türkçe *geri yazım* sözcüklerini kullanacağız.

Linux çekirdeğinde geri yazım için evrimsel süreç içerisinde çeşitli modeller kullanılmıştır.
Linux'un 1'li versiyonlarında kullanıma sokulan ilk geri yazım mekanizmasına bdflush/kupdate
denilmektedir. Bu mekanizma 2.6 çekirdeğine kadar kullanılmıştır. Bu mekanizmada kirli tampon
sayısı (o zamanlar sayfa önbelleği yerine tampon önbelleği (buffer cache) kullanılıyordu) bir eşiği
aştığında ``bdflush`` isimli çekirdek thread'i uyandırılıyor ve kirlenmiş tamponları diske geri
yazıyordu. Bu geri yazıma ilişkin parametreler de ``sys_bdflush`` sistem fonksiyonuyla
ayarlanabiliyordu. Daha sonra bu sistem fonksiyonu da kaldırıldı. Aynı zamanda bu versiyonlarda
``kupdate`` ve sonraki ismiyle ``kupdated`` isimli çekirdek thread'i 5 saniyede bir (bu süre de
ayarlanabiliyordu) devreye girip kirlenmiş ve belirli süre geçmiş tamponları diske geri yazıyordu.
Bu sistem tampon (buffer) tabanlıydı ve sayfa önbelleği ile uyumsuzdu.

2.6 çekirdeğiyle birlikte "tampon önbelleği (buffer cache)" yerine merkezi bir "sayfa önbelleği
(page cache)" kullanılmaya başlandı. Tampon (buffer) kullanımı hala geçerliliğini sürdürmekle
birlikte sayfa önbelleği içerisine alınmıştır. Bu dönemde geri yazım için ``pdflush`` isimli
çekirdek thread'leri oluşturulmuştu. Bu thread'ler bir tane değildi ve bir thread havuzu gibi
sayıları artırılıp eksiltilebiliyordu. Tipik olarak havuzda 2 ile 8 arasında değişen ``pdflush``
thread'leri bulunuyordu. Bu tasarımın da iki problemi görülmeye başlandı. Birincisi farklı
``pdflush`` thread'lerinin aynı aygıta yazması durumunda oluşan tıkanıklıktı. İkincisi yavaş bir
aygıtın tüm ``pdflush`` thread'lerini etkilemesi ve sistem performansını düşürmesiydi.

Çekirdeğin 2.6.32 versiyonuyla birlikte 3.10 versiyonuna kadar yine geri yazım mekanizmasında
değişiklikler yapılmıştır. Bu yeni mekanizmada her blok aygıt sürücüsü için (backing device) ayrı
bir *flusher thread* oluşturuldu. Böylece yavaş aygıtlar da kendi *flusher thread*'lerine sahip
oldu. Ancak zamanla bu modelin de dezavantajları görülmeye başlandı. Bu modelde sistemde çok sayıda
blok aygıtı olduğunda (örneğin yüzlerce LUN'lu bir depolama sunucusu) uyuyan yüzlerce çekirdek
thread söz konusu oluyordu. Bu da sistem kaynaklarının kullanımı konusunda bir dezavantaj
oluşturuyordu.

Nihayet çekirdeğin 3.10 versiyonuyla birlikte bugünkü sisteme geçildi. Biz kursumuzda güncel
çekirdeklerde kullanılan bu sistemi ele alacağız. Güncel çekirdeklerde kullanılan geri yazım
sistemi "çalışma kuyrukları (workqueue)" denilen çekirdek mekanizmasını kullanmaktadır. Çalışma
kuyrukları Linux çekirdeğine 2.6 versiyonuyla girdi. Ancak zaman içerisinde bu mekanizma gittikçe
geliştirildi.
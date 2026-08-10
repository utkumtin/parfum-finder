# platforms/

Platform şablonları: `<name>.json` (ör. `shopify.json`, `ticimax.json`). Bilinen bir
e-ticaret altyapısının fingerprint imzası, arama URL şablonu, varyant endpoint'i ve
tipik selector'ları tutar. Bir site profili bu şablonu derin-merge ile override eder
(site kazanır).

Şu an üç şablon var: `ideasoft`, `woocommerce`, `ikas`. Üçü de keşif turunda gerçekten
karşılaşılmış platformlar; karşılaşılmayan platform için spekülatif şablon yazılmaz.

Üçünün de varyantların tam olarak nereden okunacağı yazılı: WooCommerce'in
`data-product_variations` attribute'u, İkas'ın `__NEXT_DATA__` bloğu, İdeasoft'un
`POST /product/related-options` varyant endpoint'i.

`ideasoft.json`'daki `endpoint` bloğu `method: "POST"` taşıyan tek şablon. İdeasoft'un
varyant endpoint'i ürün başına tek istek değil, ölçü seçeneği başına tek istek istiyor:
`body` alanları (`parent_product_id`, `selected_option_group_id`) ürün sayfasından bir
selector'la okunuyor, `option_selector` sayfadaki her ölçü seçeneğinin kendi id'sini
buluyor, ve motor her id için ayrı bir istek atıp satırları birleştiriyor.
`product_price.sale_price` alanı gerçek fiyat olarak seçildi: üç farklı üründe sayfanın
kendi gösterdiği fiyatla karşılaştırılarak doğrulandı, `product_price.price` ise
`sale_price`'ın KDV'siz hali (aradaki oran hep 1,2 - `tax: 20` alanıyla tutarlı).

`out_of_stock`, dükkanın yalnızca tükenen ürün sayfasına yazdığı markup'ın selector'ı.
İki şablonda tanımlı ve ikisi de gerçek sayfadan okundu: İdeasoft tükenen üründe sepet
butonunu `data-selector="stock-warning"` taşıyan "Gelince Haber Ver" butonuyla
değiştiriyor (POST `body`'sinin `parent_product_id`'si tam o butonun üzerinde yaşadığı
için, bu olmadan tükenen her ürün "profil bozulmuş" sayılıyordu), WooCommerce ise
`p.stock.out-of-stock` bildirimi yazıyor. İkas şablonunda yok: karşılaşılmadı, ve
tahminle yazılan selector eşleşmediğinde sessizce hiçbir şey yapmaz. Ayrıntısı
ARCHITECTURE.md §6'daki fail-loud karşı kuralı.

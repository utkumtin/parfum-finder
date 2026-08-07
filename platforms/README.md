# platforms/

Platform şablonları: `<name>.json` (ör. `shopify.json`, `ticimax.json`). Bilinen bir
e-ticaret altyapısının fingerprint imzası, arama URL şablonu, varyant endpoint'i ve
tipik selector'ları tutar. Bir site profili bu şablonu derin-merge ile override eder
(site kazanır).

Şu an üç şablon var: `ideasoft`, `woocommerce`, `ikas`. Üçü de keşif turunda gerçekten
karşılaşılmış platformlar; karşılaşılmayan platform için spekülatif şablon yazılmaz.

Şablonlar bugün yalnızca fingerprint imzasını, varsa arama URL şablonunu ve çıkarım
katmanını taşıyor. Varyantların tam olarak nereden okunacağı (WooCommerce'in
`data-product_variations` attribute'u, İdeasoft'un POST varyant endpoint'i) henüz
yazılamıyor, çünkü `schema/site.schema.json` bu iki şekli tarif edecek alanları
içermiyor. Şema, çıkarım merdivenini yazan adımla birlikte genişleyecek.

`ideasoft.json` bilerek `extraction` yazmıyor: şema `extraction: "endpoint"` görünce
`endpoint` bloğu istiyor, o blok da GET biçiminde ve İdeasoft'un POST isteğini tarif
edemiyor. Şablona yazılsaydı bu platformdaki her site profili yüklenirken patlardı.

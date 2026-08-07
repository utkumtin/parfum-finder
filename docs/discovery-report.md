# Keşif raporu

M2 keşif turunun çıktısı. Altı hedef sitenin her biri için: hangi platform, hangi fetch
stratejisi, hangi çıkarım katmanı, hangi varyant deseni.

Tur tarihi: 2026-08-07. Ölçüm aracı: `parfum-finder discover <anasayfa> --product-url <ürün>`.
Her satırın altındaki kanıt, ölçümü tekrar edecek kişinin aynı sonuca ulaşabilmesi için
yazıldı. Bir alan "bilinmiyor" ise öyle yazıldı, tahmin edilmedi.

---

## Özet tablo

| id | Alan adı | Platform | Strateji | Çalışan katman | Varyant deseni |
|---|---|---|---|---|---|
| `venco` | www.vencosmetic.com | tanımlanamadı (T-Soft benzeri) | `httpx` | 3 — gömülü JS | **C** |
| `decantall` | decantall.com | ikas | `httpx` | 3 — gömülü JS (katman 1 fiyatları veriyor, ml etiketini vermiyor) | **C** |
| `luxurydekant` | luxurydekant.com.tr | WooCommerce | `httpx` | 3 — gömülü JS | **C** |
| `dekantparfum` | www.dekantparfum.com.tr | İdeasoft | `httpx` | 2 — JSON endpoint | **B** |
| `dekantdoktoru` | www.dekantdoktoru.com | İdeasoft | `httpx` | 2 — JSON endpoint | **B** |
| `ruxangroup` | ruxangroup.com | WooCommerce | `httpx` | 1 — JSON-LD | yok (dekant satmıyor) |

### Turun üç ana sonucu

1. **Altı sitenin hiçbiri `curl_cffi` veya `playwright` gerektirmiyor.** Hepsi `httpx` ile
   200 dönüyor, bot koruması ya da JS ile doldurulan gövde yok. Ölçüm her site için üç
   rungu da denedi; `playwright` hiçbir yerde `httpx`'in göremediği bir şey göstermedi.

2. **Katman 1 (JSON-LD) tek başına hiçbir sitede yetmiyor.** Ölçüde ayrışmış fiyat üretebilen
   tek katman hiçbir yerde JSON-LD değil. Detay aşağıda, ama kısaca: iki site sayfada hiç
   JSON-LD taşımıyor, biri sadece fiyat aralığı veriyor, biri fiyatları veriyor ama ml
   etiketlerini vermiyor. Yani `extraction: "jsonld"` yazan bir profil bu altı site için
   ya boş ya yanlış ₺/ml üretir.

3. **Varyant deseni ikiye ayrılıyor:** üç site deseni C (tüm varyant fiyatları sayfadaki bir
   JSON blob'unda), iki site deseni B (fiyatlar ayrı bir istekle geliyor). Desen A (her ölçü
   ayrı arama sonucu satırı) hiçbir sitede saf haliyle görülmedi. Bu, M4'ün "arama sayfası
   yeter" kestirmesini kullanamayacağı anlamına geliyor: her sitede ürün sayfasına ya da
   endpoint'e inmek gerekiyor.

---

## Site detayları

### `venco` — www.vencosmetic.com

- **Platform:** tanımlanamadı. Markup Türk SaaS altyapılarından birine ait
  (`/template/smart/default/`, `/theme/apollo_v1/`, `PRODUCT_PAGE_DATA` global'i,
  `cdnaws.com.tr` CDN'i). Yanıt başlıkları `_ecom_code` ve `ecom_orcode` çerezlerini
  koyuyor; bu çerez adları T-Soft'un imzası olarak biliniyor. Yine de ne HTML'de ne
  başlıklarda platform adını yazan bir dize var, o yüzden isim **doğrulanmadı**. M3'te
  şablon adı buna göre konmamalı; fingerprint denemesi için en umut verici imza
  `_ecom_code` çerezi.
- **Strateji:** `httpx`. Üç rung da 200; `playwright` 62 KB, `httpx` 52 KB, fark sadece JS
  ile eklenen süslemeler.
- **Katman:** 3 (gömülü JS state). Sayfada `PRODUCT_PAGE_DATA = { price: ..., variants:
  {"count":1,"summary":{"1 ML":{...},"2 ML":{...}}} }` var. `summary` her ölçü için
  `in_stock`, `quantity` ve `price_list.fiyat` taşıyor, yani ml + fiyat + stok üçlüsü tek
  fetch'te tam geliyor.
- **Katman 1 neden yetmiyor:** JSON-LD tek bir `Offer` ve tek fiyat (`200.00`) veriyor. Bu
  fiyat seçili ölçünün değil, "ML." birim fiyatının değeri; sayfadaki gerçek ölçü fiyatları
  (2 ML = 425,00 TL, 5 ML = 1.000,00 TL) JSON-LD'de hiç yok.
- **Varyant deseni:** **C**. `<select data-variant-name="Milim Fiyatı">` altında 1/2/3/5/10 ML
  seçenekleri, fiyatlar aynı sayfadaki blob'da.
- **Not:** `summary` içinde stokta olmayan ölçüler de duruyor (`in_stock: false`), yani stok
  bilgisi ayrıca istek gerektirmiyor.

### `decantall` — decantall.com

- **Platform:** **ikas**. Kesin kanıt: bütün görseller `cdn.myikas.com` üzerinden geliyor ve
  sayfa ikas'ın ürün modelini (`variants[].prices[].sellPrice`, `variantValues`,
  `stocks[].stockCount`) gömülü olarak taşıyor. Sitemap `/products.xml` + `/collections.xml`.
- **Strateji:** `httpx`.
- **Katman:** 3 (gömülü JS state). Altı site içinde katman 1'in gerçek varyant fiyatları
  ürettiği tek site burası, ama fiyatları ml'ye bağlayamıyor; o yüzden profil katman 3'e
  yazılmalı, katman 1 de çapraz kontrol için kullanılabilir. Blob'daki `variants` dizisi
  her varyant için `sku`,
  `prices[].sellPrice`, `stocks[].stockCount` ve `variantValues` (ml etiketi) veriyor.
- **Katman 1 kısmen çalışıyor ama yetmiyor:** JSON-LD **4 ayrı `Offer`** ve 4 gerçek fiyat
  veriyor (360 / 600 / 1200 / 1800 TRY, hepsi `InStock`). Ancak offer'lar sadece
  `?vid=<uuid>` ile ayrışıyor, **ml etiketi taşımıyor**. Ölçüler yalnızca markup'ta
  (`span.variant-name` → 3 ml, 5 ml, 10 ml, 15 ml) ve gömülü blob'da. Fiyatı ml'ye
  bağlayamayan bir çıkarım ₺/ml hesaplayamaz, o yüzden profil katman 3'e yazılmalı.
- **Varyant deseni:** **C**.

### `luxurydekant` — luxurydekant.com.tr

- **Platform:** **WooCommerce** (WordPress). `probe` fingerprint'i zaten yakalıyor.
- **Strateji:** `httpx`.
- **Katman:** 3 (gömülü JS state). WooCommerce "variable product" formu bütün varyantları
  escape edilmiş JSON olarak `data-product_variations` attribute'unda taşıyor: her varyant
  için `attributes.attribute_pa_hacim` (3ml / 5ml / 10ml / 30ml), `display_price`
  (180 / 270 / 530 / 1570), `is_in_stock`, `variation_id`.
- **Katman 1 neden yetmiyor:** JSON-LD tek bir `AggregateOffer` veriyor, `lowPrice: 180` ve
  `highPrice: 1570`. Bu iki sayı 3 ml ve 30 ml fiyatları; aradaki 5 ml ve 10 ml JSON-LD'de
  yok. Aralığın alt ucunu ürün fiyatı sanmak bu sitenin ₺/ml'sini üç kat yanlış gösterir.
- **Varyant deseni:** **C**.
- **Turun düzelttiği hata:** İlk `discover` çıktısı bu sayfa için "variant control in markup:
  no" diyordu ve hiç uyarı vermiyordu. Sebep: `discover`'ın varyant seçici dedektörü
  "variant" kelimesi üzerine kuruluydu, WooCommerce ise "variation" yazıyor ve iki kelime
  ortak alt dize içermiyor. Dedektöre `[data-product_variations]`, `[class*="variations_form"]`
  ve `select[name^="attribute_"]` eklendi. Ayrıca sadece aralıktan gelen fiyatlar için ayrı
  bir uyarı eklendi, çünkü eski "sadece 1 fiyat okundu" uyarısı iki uçlu aralıkta tetiklenmiyordu.

### `dekantparfum` — www.dekantparfum.com.tr

- **Platform:** **İdeasoft**. Kanıt: `/idea/jj/<id>/themes/...` varlık yolları,
  `<sürüm>/storefront/assets/javascript/layout/product.js`, sitemap'te
  `xml/sitemap_product_N.xml?sr=<hash>` deseni.
- **Strateji:** `httpx`.
- **Katman:** **2 (platform JSON endpoint)**. Aşağıdaki ortak İdeasoft bölümüne bakın.
- **Katman 1 neden yetmiyor:** Sayfada **hiç** `application/ld+json` yok. Ne anasayfada, ne
  ürün sayfasında. Ürün sayfası doğrudan `discover`'a verilerek de doğrulandı.
- **Varyant deseni:** **B**. `div.variant-list` içinde `span.variant-text` olarak
  2,7 ml / 3 ml / 5 ml / 8 ml / 10 ml ... listeleniyor, hiçbirinin yanında fiyat yok.
- **Not:** Ölçü etiketleri her zaman sade değil: `"2,7 ml - metal sprey"`,
  `"3 ml - plastik sprey"` gibi değerler var. `variant_rules`'un ml çıkarımı bu biçimi
  tolere etmeli.

### `dekantdoktoru` — www.dekantdoktoru.com

- **Platform:** **İdeasoft**. `dekantparfum` ile aynı imzalar, aynı storefront sürümü (8.4.3.0).
- **Strateji:** `httpx`.
- **Katman:** **2 (platform JSON endpoint)**.
- **Katman 1 neden yetmiyor:** Sayfada hiç JSON-LD yok, `dekantparfum` ile birebir aynı durum.
- **Varyant deseni:** **B**. `div.variant-list` içinde 3 ml / 5 ml / 10 ml / 15 ml / 20 ml /
  30 ml, fiyatsız.

#### İdeasoft varyant endpoint'i (iki site için ortak)

Tema JS'i (`storefront/assets/javascript/layout/product.js`) ölçü seçildiğinde şu isteği atıyor:

```
POST /product/related-options
  parent_product_id=<ana ürünün id'si>
  selected_option_group_id=<data-group-id>
  selected_options[]=<data-option-id>
```

`parent_product_id`, ürün sayfasındaki sepete ekle düğmesinin `data-product-id`
attribute'undan; grup ve seçenek id'leri `div.variant-list-group[data-group-id]` ve
`span.variant-text[data-option-id]` attribute'larından okunuyor.

Dönen cevap tek istekte ihtiyaç duyulan her şeyi veriyor:

```json
{"success": true, "data": {"options": [{
  "option_id": 6, "option_title": "3 ml",
  "product_id": 61, "product_name": "Amouage Blossom Love 3 ml",
  "product_url": "/urun/amouage-blossom-love-3-ml",
  "product_sku": "P2ANKDV2A4_66908", "product_stock_amount": 32.0,
  "product_price": {"price": 450.0, "sale_price": 540.0, "currency_abbr": "TL", ...},
  "variant_name": "3 ml"
}]}}
```

İki sitede de doğrulandı (dekantdoktoru: ana ürün 58, dekantparfum: ana ürün 14). Bu, deseni
B'nin doğru çözümü: `playwright`'a düşmeden bütün ölçülerin fiyat ve stoğu alınıyor.

**Dikkat edilecek iki nokta:**

- `product_price` içinde hem `price` hem `sale_price` var ve bu örnekte `sale_price` (540)
  `price`'tan (450) **büyük**. Yani alan adları sezgiye ters; hangisinin sepette tahsil edilen
  tutar olduğu **doğrulanmadı**. Profile yazmadan önce bir üründe elle kontrol edilmeli.
- Her ölçü aslında kendi URL'si olan ayrı bir ürün (`/urun/<slug>-3-ml`). Yani çıkarım
  istenirse ölçü başına ayrı sayfa da çekebilir, ama endpoint tek istekte hepsini verdiği için
  bu gereksiz.

### `ruxangroup` — ruxangroup.com

- **Platform:** **WooCommerce** (Woodmart teması).
- **Strateji:** `httpx`.
- **Katman:** 1 (JSON-LD). Ürün sayfası tek `Offer` ve tek fiyat veriyor, `sku` dolu, stok
  durumu okunabiliyor. Basit ürün olduğu için bu yeterli.
- **Varyant deseni:** yok — ve **bu site dekant satmıyor.**
  - Dört ürün sayfasında `variations_form` / `data-product_variations` bulunamadı, hepsi
    "simple product".
  - `product-sitemap.xml`'deki 24 slug'ın hiçbirinde ml geçmiyor; bir tanesi doğrudan
    `ard-alzaafaran-parfum-80ml-edp`.
  - Örnek ürün (`lattafa-maani`) 1000,00 TL, tek fiyat, stokta değil.
  - Sonuç: tam şişe satan bir Arap markaları mağazası. `sites/targets.txt` zaten
    "Sadece arap markalari var" notunu düşmüş.
  - **Karar kullanıcıya ait:** dekant karşılaştırma listesinde kalacak mı? Kalırsa ₺/ml
    kolonu bu site için tam şişe fiyatı üzerinden hesaplanır ve diğerleriyle kıyaslanamaz.

---

## `discover`'ın bu turda düzelen davranışı

Tur, aracın kendisinde bir hata ortaya çıkardı ve düzeltildi:

- **Varyant seçici dedektörü WooCommerce'i göremiyordu.** Ölçüm, `luxurydekant` için "varyant
  seçici yok" diyordu; gerçekte dört ölçülük bir variable product vardı. Sessiz yanlış ₺/ml'nin
  tam da tarif edilen hali.
- **Sadece aralıktan gelen fiyatlar uyarısızdı.** `AggregateOffer`'ın iki ucu iki fiyat gibi
  sayıldığı için "sadece 1 fiyat okundu" uyarısı tetiklenmiyordu. Artık varyant seçici varken
  hiçbir offer kendi fiyatını söylemiyorsa ayrı bir uyarı çıkıyor.

Dedektör bilerek dar tutuldu: "variation" kelimesine geniş eşleşme, ilgili ürünler
ızgarasındaki tema swatch'larına da takılıyor ve `ruxangroup` gibi varyantsız bir ürünü
varyantlı gösteriyordu.

---

## Açık kalan sorular (M3 / M4 girdisi)

1. **Arama URL şablonu hiçbir site için bilinmiyor.** İdeasoft'ta arama formunun `action`'ı boş
   ve denenen `?/arama?q=`, `/search?q=`, `/index.php?do=search` yolları sonuç döndürmedi.
   `discover`'ın uçtan uca denemesinin arama yarısı hâlâ eksik; bu şablonlar M3'te platform
   şablonlarına yazılmalı.
2. **`venco`'nun platformunun adı.** HTML grep'i ve yanıt başlıkları denendi, ikisi de adı
   yazmıyor. `_ecom_code` çerezi ayırt edici görünüyor ama tek başına isim kanıtı değil.
3. **`probe`'un fingerprint'i ikas ve `venco`'yu tanımıyor**, ikisi de `-` dönüyor. İdeasoft
   `ideasoft?` (soru işaretiyle) dönüyor, imza güçlendirilebilir.
4. **İdeasoft `price` / `sale_price` ayrımı** doğrulanmadı (yukarıya bakın).
5. **Kargo bilgisi hiç toplanmadı** — tasarım gereği. Ücretsiz kargo eşiği, kargo ücreti ve
   notlar her site için elle girilecek.
6. **`ruxangroup` listede kalacak mı?**

## Bu raporun M3 ve M4'e söyledikleri

- **M3'te yazılacak platform şablonları:** `ideasoft` (iki site birden, endpoint'i belli),
  `woocommerce` (iki site, biri variable biri simple), `ikas` (bir site). `venco`'nun platformu
  adlandırılamadığı için şablonsuz, site profiliyle sürülür. Karşılaşılmayan platform
  (Shopify, Ticimax, Opencart) için şablon yazılmaz.
- **M4'te merdivenin öncelikli katmanları:** `endpoint` (İdeasoft) ve `embedded_json` (diğer üçü).
  `jsonld` altı sitenin hiçbirinde tek başına yeterli değil; `css` katmanına ise hiçbir site
  için ihtiyaç görünmüyor.
- **`variant_rules` için gerçek veri:** ölçü etiketleri `3 ml`, `3ml`, `10 ml ` (sonda boşluk),
  `2,7 ml - metal sprey`, `1 ML` biçimlerinde geliyor. Dekant dışı filtresi için sitelerde
  30 ml'lik varyantlar mevcut (`luxurydekant` 30ml, `dekantdoktoru` 30 ml).

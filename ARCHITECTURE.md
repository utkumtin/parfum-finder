# ARCHITECTURE — parfum-finder

## 1. Genel yapı

```
                    ┌──────────────┐
                    │   discover   │  site → profil (asistanlı)
                    └──────┬───────┘
                           │ yazar
                           ▼
        platforms/*.json ──► sites/*.json ◄── hooks/*.py (opsiyonel)
                                 │
                                 │ sürer
                                 ▼
   ┌──────────┐          ┌───────────────┐          ┌──────────┐
   │ matcher  │◄─────────│    engine     │─────────►│ normalize│
   └──────────┘          │ (jenerik      │          └──────────┘
                         │  scraper)     │
                         └───────┬───────┘
                                 │ snapshot
                                 ▼
                          ┌─────────────┐
                          │    store    │  SQLite
                          └──────┬──────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
             ┌─────────────┐           ┌─────────────┐
             │   basket    │           │     tui     │
             │ (optimizer) │──────────►│  (Textual)  │
             └─────────────┘           └─────────────┘
```

### Paket düzeni

```
src/parfum_finder/
├── normalize.py      # sayı/ml parse + format
├── profiles.py       # profil yükleme, jsonschema doğrulama, platform şablonu merge
├── fetch.py          # httpx / curl_cffi / playwright — tek arayüz
├── probe.py          # strateji ölçümü: her stratejiyi dener, kanıtlı rapor üretir
├── extract.py        # çıkarım merdiveni: jsonld → endpoint → embedded → css
├── engine.py         # async orchestration, rate limiting, hata izolasyonu
├── matcher.py        # marka+konsantrasyon zorunlu + fuzzy isim
├── store.py          # SQLite
├── basket.py         # sepet optimizasyonu (saf fonksiyon)
├── discover.py       # keşif script'i
├── validate.py       # profil doğrulama komutu
├── cli.py            # komut girişi
└── tui/
    ├── app.py
    ├── search_screen.py
    └── basket_screen.py

sites/<id>.json        # site profilleri (kullanıcı düzenler) — proje kökünde, src/ dışında
platforms/<name>.json  # platform şablonları (proje ile gelir) — proje kökünde
hooks/<id>.py          # opsiyonel Python override — proje kökünde
fixtures/<id>/         # golden HTML örnekleri — proje kökünde
```

**Not:** paket `src/parfum_finder/` altında (src-layout) — `uv init --package` ile kurulan
proje iskeletiyle örtüşsün ve editable-install sırasında proje kökünün yanlışlıkla
`sys.path`'e sızıp test importlarını bulanıklaştırması engellensin diye. `sites/`,
`platforms/`, `hooks/`, `fixtures/` paketin **dışında**, proje kökünde kalır — bunlar
kullanıcının elle düzenlediği veri/konfigürasyon, dağıtılan Python paketinin parçası değil.

---

## 2. Profil sürücülü tasarım

**Temel karar:** Site başına Python adapter sınıfı **yoktur**. Tek bir jenerik motor,
`sites/<id>.json` profilini okuyup o siteyi sürer.

**Gerekçe:** Sitelerin %90'ı aynı işi farklı selector'larla yapar. Site başına sınıf yazmak
aynı kodu N kez kopyalamaktır; profil, farkı **veri** olarak ifade eder.

### Kaçış kapısı: `hooks/<id>.py`

Profil şemasına koşul, döngü, ifade dili gömmek — yani JSON içinde mini bir programlama
dili yaratmak — bilinen bir anti-pattern'dir. Bunun yerine, profilin yetmediği tuhaf site
için **az sayıda net kanca** içeren opsiyonel bir Python dosyası:

```python
# hooks/ornek_site.py
def before_search(query: str, profile: dict) -> str:
    """Arama sorgusunu göndermeden önce dönüştür."""


def after_search(
    candidates: list[ProductCandidate], html: str
) -> list[ProductCandidate]:
    """Arama sonuçlarını filtrele/düzelt."""


def parse_variants(html: str, profile: dict) -> list[Variant] | None:
    """Varyant çıkarımını tamamen devral. None dönerse jenerik akış devam eder."""
```

Kanca yoksa jenerik akış çalışır. Kanca varsa profil hâlâ geçerlidir — kanca sadece
belirli adımı devralır. **Yeni kanca eklemek kolay olmamalı**: her yeni kanca, profil
şemasının yetersiz kaldığının işaretidir; önce şema genişletilmeye çalışılır.

---

## 3. Çıkarım merdiveni (`extract.py`)

Bir sayfadan ürün verisi çıkarmanın **4 katmanı**, dayanıklılık sırasıyla. `discover`
yukarıdan aşağı dener, **çalışan en üst katmanı** profile yazar.

Merdivenin isimleri ve sırası tek yerde durur: `extract.EXTRACTION_LAYERS`. `engine`
buna göre dağıtım yapar, `validate` bozulan bir profilin hangi alt katmana düşebileceğini
söylerken bunu yürür. Üçüncü bir kopya `schema/site.schema.json`'daki `extraction` enum'ı
olmak zorunda; ikisinin ayrışmadığı testle bağlanmıştır.

### Katman 1 — JSON-LD
`<script type="application/ld+json">` içindeki `Product` / `Offer` nesneleri.
SEO için konur, tema değişse bile korunur. `name`, `offers.price`, `offers.availability`,
çoğu zaman `hasVariant` hazır gelir.

Ele alınacak varyasyonlar (`extract.py`): kök dizi, `@graph` sarmalayıcı, tek `Offer`
vs `AggregateOffer`, `availability` değerinin `https://schema.org/InStock` /
`InStock` / `in_stock` biçimleri.

### Katman 2 — Platform JSON endpoint
Platform biliniyorsa şablondan gelir. Örn. Shopify `/products/<slug>.js` tüm varyantları
fiyat + stok ile tek istekte döner.

**Bu katman, varyant deseni B'nin (bkz. §4) doğru çözümüdür** — Playwright'a düşmeden
AJAX fiyatlarına erişmenin yolu.

### Katman 3 — Gömülü JS state
Sayfadaki `var product = {...}` / `window.__DATA__ = {...}` blob'u. Regex ile yakalanıp
`json.loads` edilir.

### Katman 4 — CSS selector
Son çare. En kırılgan katman; tema değişikliğinde ilk ölen.

> Profil hangi katmanı kullandığını `extraction` alanında saklar. `validate` bir katman
> bozulduğunda **bir alt katmana düşülüp düşülemeyeceğini** raporlar.

---

## 4. Varyant desenleri — statik scraping'in kırıldığı yer

Dekant ölçüleri Türk e-ticaret altyapılarında üç farklı şekilde durur. `discover`'ın
**birincil işi** bu üçünü ayırt etmektir.

| Desen | Görünüm | Çözüm |
|---|---|---|
| **A** | Her ölçü ayrı SKU/ürün — arama sonucunda "…5 ml", "…10 ml" ayrı satırlar | `httpx` + arama sayfası yeter, ürün sayfasına girmeye bile gerek olmayabilir |
| **B** | Tek ürün sayfası + varyant dropdown'u, fiyatlar **AJAX** ile gelir | Katman 2 (JSON endpoint) — bulunamazsa `playwright` |
| **C** | Tek ürün sayfası, tüm varyant fiyatları sayfadaki **JSON blob**'unda gömülü | Katman 1 veya 3 — `httpx` yeter |

**Desen B, `httpx` + CSS ile görülemez.** Bir site B deseninde olup profili CSS katmanına
düşmüşse, tek bir varyant fiyatı (genelde en küçük ml) okunur ve **diğer varyantlar sessizce
kaybolur** — bu, yanlış ₺/ml karşılaştırmasının en sinsi kaynağıdır. `discover` bu durumu
"varyant seçici var ama sadece 1 fiyat bulundu" uyarısıyla işaretler.

### Dekant olmayan ürünlerin filtrelenmesi

`variant_rules.exclude` ile: `Tester`, `Full Şişe`, `Orijinal Şişe`, `Kutulu`, `Set`,
ve `size_ml >= 30`. Bunlar dekant değildir; ₺/ml sıralamasını ve sepet toplamını kirletir.
Filtre profilde tanımlıdır, site özelinde genişletilebilir.

---

## 5. `discover` — keşif akışı

```
discover <url> [--id <slug>]
   │
   ├─ 1. Strateji ÖLÇÜMÜ                              → profil alanı: strategy
   │     httpx → curl_cffi → playwright sırasıyla dener
   │     ilk yeten seçilir (tahmin değil, ölçüm)
   │
   ├─ 2. Platform FINGERPRINT                          → profil alanı: platform
   │     markup imzasından: Ticimax / İdeasoft / Opencart / Shopify / WooCommerce
   │     biliniyorsa platforms/<name>.json şablonu TEMEL alınır
   │
   ├─ 3. Çıkarım merdiveni                             → profil alanı: extraction
   │     jsonld → endpoint → embedded → css, çalışan en üst katman
   │
   ├─ 4. Uçtan uca DENEME
   │     örnek arama + örnek ürün sayfası
   │     çıkarılan alanlar (ad, fiyat, ml, stok) KANITIYLA gösterilir
   │     her alan için güven skoru
   │
   └─ 5. YAZIM
         sites/<id>.json      (düşük güvenli alanlar → needs_review[])
                              + discovered_at, schema_version
                              − shipping bloğu BOŞ bırakılır (elle doldurulur)
         fixtures/<id>/       (golden HTML örnekleri)
```

### Platform şablon kütüphanesi

`platforms/<name>.json` bir platformun bilinen desenlerini tutar: arama URL şablonu,
varyant JSON endpoint'i, tipik selector'lar, fingerprint imzaları.

```jsonc
// platforms/shopify.json (şekil örneği)
{
  "fingerprint": { "any": ["Shopify.theme", "cdn.shopify.com", "/cart/add"] },
  "search": { "url_template": "{base_url}/search?q={query}" },
  "extraction": "endpoint",
  "endpoint": { "product_json": "{product_url}.js", "variants_path": "variants" }
}
```

**Değeri:** Platform tanındığı an profilin büyük kısmı hazır gelir.
**Aynı platformdaki ikinci site neredeyse sıfır emekle eklenir** — keşfin asıl
future-proof kısmı budur.

Merge kuralı: `sites/<id>.json` alanları `platforms/<name>.json` alanlarını **override
eder** (derin merge, site kazanır). Profil `platform: null` ise şablon uygulanmaz.

### Dürüst sınır: bu **asistanlı** keşif, otomatik değil

Tam otomatik selector çıkarımı güvenilir değildir. `discover`:
- Alanları **güven skoruyla önerir**,
- Düşük güvenli olanları profile `"needs_review": ["product.price", ...]` olarak yazar,
- **Kargo eşiği / kargo ücreti / notlar hiç tahmin edilmez** — her zaman elle girilir.

`needs_review` boş olmayan bir profil kullanılabilir ama TUI'de uyarı rozetiyle görünür.

---

## 6. `engine` — orchestration

### Eşzamanlılık modeli

- **Siteler arası paralel** — `asyncio.TaskGroup`, her site bağımsız task
- **Site içinde seri** — site başına `asyncio.Semaphore(1)` + `rate_limit_ms` gecikme
- **Retry** — geçici hatalarda üstel backoff, sınırlı deneme

**Gerekçe:** Hedef siteler küçük butikler. Paralel istek yağmuru hem etik değil hem de
IP banı ile sonuçlanır — ve `curl_cffi` bir rate-limit banını **kurtarmaz**.

En pahalı iki işlem: `discover` ve sepet **Tazele** (N parfüm × M site). Rate limiting'e
en çok orada dikkat edilir; Tazele ilerleme göstergesiyle çalışır.

### Çoklu parfüm aramasi

Arama satırı ` - ` ile ayrılmış birden fazla parfüm alır (`matcher.split_queries`,
en fazla `MAX_QUERIES`). Boşluk şartı var, yoksa `Jean-Paul Gaultier` bölünürdü.

Tarama şekli Tazele ile aynı: **site başına bir task, site içinde parfümler seri.**
`run_site` pacer'ını her çağrıda kendisi kurar, dolayısıyla bir sitenin parfümlerini
paralel başlatmak bütün `rate_limit_ms` gecikmelerini paralele alır ve dükkana tam
olarak engellemeye çalıştığımız isteği patlamasını gönderir.

### Tarama süresi — nereye gidiyor

Bir taramanın maliyeti arama sayfası değil, **her arama sonucu için açılan ürün
sayfası**: site içinde seri ve aralarda `rate_limit_ms` var. Bir dükkanın kataloğunun
büyük kısmı tam şişe, yani o isteklerin çoğu baştan boşa gider. Üç önlem:

| Önlem | Nerede | Ne kazandırır |
|---|---|---|
| Aday ön filtresi (`keep_candidate`) | `engine.search_site` + `matcher.title_could_match` | Listeleme başlığı sorguyla uyuşmayan ürünün sayfası hiç açılmaz |
| Ürün sayfası memo'su (`variants_cache`) | `engine._read_variants` | Aynı ürün iki parfümün sonuç sayfasında çıkarsa bir kez okunur |
| Tek tarayıcı (`fetch.browser_session`) | `fetch` | Playwright gereken sitede sayfa başına chromium açmak yerine tarama boyunca bir tane |

Ön filtre `empty`/`suspect` ayrımını bozmamak için **kanarya** kullanır: hiçbir aday
geçmezse ilk aday yine açılır, böylece "fiyat okuyamadı" kontrolü gerçek bir sayfa
üzerinde çalışmaya devam eder. Ödünü, `variant_control` kontrolünün yalnızca açılan
sayfalar için işlemesi.

### Hata izolasyonu

Bir site patlarsa diğerleri devam eder. Her sitenin sonucu üç durumdan biridir:

```python
@dataclass
class SiteResult:
    site_id: str
    status: Literal["ok", "error", "suspect"]
    variants: list[Variant]
    error: str | None  # status="error" ise
    diagnostic: str | None  # status="suspect" ise: hangi katman başarısız
```

### Fail-loud — sessiz boş sonuç yasaktır

Site tasarım değiştirince selector ölür ve scraper **sessizce boş döner**. Bu, yanlış
"en ucuz" kararının bir numaralı sebebidir: eksik site, "orada yok" gibi görünür.

Kural: aşağıdaki durumlarda sonuç `status="suspect"` olur ve TUI'de **"profil bozulmuş
olabilir"** hatası + hangi katmanın başarısız olduğu gösterilir:

| Durum | Neden şüpheli |
|---|---|
| Arama 0 sonuç döndü ama HTTP 200 ve sayfa dolu | Selector ölmüş olabilir |
| Ürün bulundu, fiyat parse edilemedi | Fiyat selector'ı veya format değişmiş |
| Varyant seçici var ama tek fiyat çıktı | Desen B'ye düşülmüş, varyantlar kayıp (§4) |
| Çıkarım katmanı yanıt verdi ama zorunlu alan boş | Şema değişmiş |

`status="suspect"` bir sitenin sonuçları **sepet hesabına girmez** — eksik sayılır, çünkü
"pahalı" değil "bilinmiyor" durumundadır.

Bunun karşı kuralı da aynı derecede önemli: her seferinde kurt masalı anlatan bir rozeti
kimse okumaz. Aşağıdaki üç kanıt, yukarıdaki satırlardan birini geçersiz kılar ve sonucu
`empty` yapar — üçü de dükkanın kendi markup'ından okunur, profilin selector'larından
değil, çünkü profilden alınan kanıt "burada satılmıyor" ile "artık göremiyoruz"u
ayıramaz:

| Kanıt | Nerede | Neden şüpheli değil |
|---|---|---|
| Sayfa "sonuç bulunamadı" diyor (`_NO_RESULTS_SELECTOR`) | `engine._check_empty_search` | Altı sitenin ikisi bütün kataloğunu mega-menüden geçiriyor: sonuçsuz arama sayfası 138–426 ürün-şekilli node taşıyor, hiçbiri sonuç değil. Sayfanın kendi cevabı, node saymaktan üstündür |
| Açılan sayfada ölçü listesi hiç yok (`engine._page_offers_sizes`) | `engine.search_site` | Düz tam şişe. Bir dükkanın kataloğunun yaklaşık beşte dördü bu, ve o parfümü yalnızca tam şişe satan dükkan her aramada işaretlenirdi |
| Sayfa "stokta yok" diyor (`out_of_stock`) | `engine._page_says_sold_out` | Tükenen üründe bazı temalar sepet butonunu ("Gelince Haber Ver" ile) kaldırıyor; POST varyant endpoint'inin gövde alanı o butonun üzerinde yaşıyor. Bu, profil hakkında değil tek bir parfümün stoğu hakkında bir olgudur |

Satırsız sayfa kuralının sınırı: katman satır ürettiyse (fiyatsız bile olsa) ölçü listesi
kanıtlanmış demektir ve şüphe geri gelir. `out_of_stock` tanımlamayan bir profil eski,
daha katı davranışı korur.

---

## 7. `matcher` — parfüm eşleştirme

**Problem:** Ham başlık benzerliği `Sauvage` / `Sauvage Elixir` / `Eau Sauvage` veya
`Bleu de Chanel EDT` / `EDP` / `Parfum` ayrımını yapamaz. Yüksek skorlu **yanlış** eşleşme,
eşleşmemekten kötüdür — ucuz fiyat gibi görünür ve sepete yanlış ürün girer.

### Algoritma

```
0. Başlığı parantez sınırından AYIR: dışarısı ürünün kendi ismi, içerisi
   taklit ettiği orijinalin referansı (bkz. Klon/orijinal ayrımı)
1. Başlığı normalize et (küçült, TR karakter katlama, gürültü kelimelerini at:
   "dekant", "decant", "parfüm", "ml", "orijinal", "tester")
2. Konsantrasyonu ÇIKAR ve AYIR: EDT | EDP | EDC | Parfum | Extrait | Elixir
3. Markayı ÇIKAR ve AYIR
4. ZORUNLU eşleşme:
      marka         == aranan marka           (exact, normalize sonrası)
      konsantrasyon == aranan konsantrasyon   (belirtilmişse)
5. Kalan isim kısmına rapidfuzz.token_sort_ratio
6. Skor eşiğinin altı → aday listesine girer ama DÜŞÜK GÜVEN işaretlenir
7. Adım 1-6 önce ürünün kendi ismiyle çalışır. Tutmazsa referans yarısıyla
   tekrar denenir; oradan gelen eşleşme `clone_of` ile döner ve asla
   `confident` değildir
```

**`Elixir` neden konsantrasyon listesinde:** `Sauvage Elixir` ayrı bir üründür,
`Sauvage`'ın bir konsantrasyonu gibi davranır. Adım 2'de ayrılması, adım 5'te
`Sauvage` ile `Sauvage Elixir`'in yanlışlıkla eşleşmesini engeller.

**Neden `token_sort_ratio`, `token_set_ratio` değil:** Set oranı alt kümeyi tam
eşleşme sayar; `Sauvage` araması `Eau Sauvage` başlığını 100 ile döndürür ve farklı
bir parfümü tam güvenle verir. Sıralama, fazladan kelimeye bir bedel ödetir. Başlık
yine listede görünür, sadece onay isteyecek şekilde işaretlenir.

### Klon/orijinal ayrımı

Bazı dükkanlar orijinallerin yanında klon da satar ve taklit ettiği parfümü başlıkta
parantez içinde yazar:

```
Armaf – Club De Nuit Untold (Maison Francis Kurkdjian – Baccarat Rouge 540)
```

Parantez bir referanstır, ürünün ne olduğunun parçası değil. İsim sayıldığında eşleşme
**iki yönde birden** bozuluyordu:

| Arama | Parantez isim sayılınca | Ayrıldıktan sonra |
|---|---|---|
| `MFK Baccarat Rouge 540` | Armaf klonu 73 skorla eşleşiyor — marka kontrolü parantez sayesinde geçiyor, klon ucuz olduğu için ₺/ml sıralamasında en üste çıkıyor | Kendi ismiyle reddediliyor, referanstan `clone_of` ile geliyor |
| `Armaf Club de Nuit Woman` | Doğru ürün 59, yanlış `Club De Nuit Bling` 67 — referanstaki kelimeler doğru ürünün skorunu aşağı çekiyor | Doğru ürün 100, en üstte |

**Klon satırı neden gizlenmiyor:** İyi bir klon orijinal yerine alınabilir. Karar
kullanıcınındır; program sadece o satırın ne olduğunu söyler (`KLON ← <orijinal>`).

**Klon satırı neden yazılmıyor:** Farklı bir şişe, farklı bir fiyat. Aranan parfümün
kimliği altına yazılırsa fiyat geçmişinde ani bir düşüş gibi görünür ve sepet tüm
siparişi o rakama göre hesaplar. Baraj `store.write_snapshots` içindedir; hem CLI hem
TUI oradan geçtiği için tek nokta yeter. Aynı nedenle sepete de eklenemez.

**Kuralın bilinen kenarı:** Parantezin *her* kullanımı ayrılır, sadece klon referansı
olanlar değil. `(Tester)` / `(100 ml)` zararsızdır (içerik zaten gürültü ya da ölçü),
ama `Dior Sauvage (Elixir)` gibi bir başlıkta konsantrasyon referans yarısına düşerdi.
Toplanan fixture'larda örneği yok.

### Görünürlük — zorunlu

- Her sonuç satırında **sitedeki ham başlık + eşleşme skoru** gösterilir
- İkisi de saklanır: `match_score` → `products`, `raw_title` → `product_variants`
  (varyant deseni A'da her ml'nin başlığı farklıdır)
- **Düşük skorlu eşleşme sepete sessizce eklenemez** — TUI onay ister
- **Klon satırı `KLON ← <orijinal>` ile işaretlenir**, sepete hiç eklenemez — onay
  diyaloğuna bile düşmez, gerekçesiyle reddedilir

---

## 8. `normalize` — sayı işleme

Uygulamanın doğruluk çekirdeği. Tek bir fonksiyon seti, ağır birim testi.

```python
parse_price(raw: str) -> Decimal      # "1.250,00 TL" → Decimal("1250.00")
parse_size_ml(raw: str) -> Decimal    # "5 ML" → Decimal("5"), "0,5 ml" → Decimal("0.5")
format_price(v: Decimal) -> str       # Decimal("1250") → "1,250.00 ₺"
format_ml(v: Decimal) -> str          # Decimal("1.5") → "1.5 ml"
```

**Giriş toleranslı, çıkış kanonik.** Türkçe (`1.250,00`) ve İngilizce (`1,250.00`)
formatların ikisi de tanınır; ayraç konumu + son gruptaki basamak sayısından çıkarım yapılır.

**Neden kritik:** Naif parse `1.250,00` → `125000` üretir. Bu tek hata hem ₺/ml sıralamasını
hem sepet toplamlarını hem de ücretsiz kargo eşiği kararını bozar — ve **çok inandırıcı
görünür**.

Zorunlu test vakaları: `1.250,00 TL` · `1,250.00` · `250 TL` · `₺1.250` · `250,50` ·
`0,5 ml` · `1.5ml` · `5 ML` · `5cc` · `5 cc`.

`locale` modülü **kullanılmaz** — global durum değiştirir, thread-safe değildir.

---

## 9. `basket` — sepet optimizasyonu

Saf fonksiyon: site erişimi yok, sentetik veriyle tam test edilebilir.

```python
def optimize(
    items: list[BasketItem],                        # perfume, size_ml, qty
    prices: dict[tuple[item_id, site_id], Decimal | None],   # None = eksik/stoksuz
    shipping: dict[site_id, ShippingConfig],        # threshold, cost, notes
) -> BasketReport
```

`BasketReport` içinde:
- **Site başına senaryo:** alt toplam · kargo · genel toplam · kapsanan/toplam ürün ·
  eksik ürün listesi · ücretsiz kargoya kalan tutar
- **En iyi bölünmüş kombinasyon:** ürün→site ataması · site başına alt toplam+kargo ·
  genel toplam

### Neden basit "her ürünü en ucuz siteden al" yanlış

Kargo maliyeti **doğrusal değildir** — site alt toplamı eşiği geçince 0'a düşer.
Bir ürünü daha pahalı bir siteden almak, o sitenin eşiğini aşırıp kargoyu sıfırlayarak
**toplamı düşürebilir**.

### Algoritma

```
1. Site alt-kümeleri üzerinde enumerasyon  (2^M, M ≤ 10 → ≤ 1024 kombinasyon)
2. Her alt-küme için: her ürünü, alt-kümedeki en ucuz siteye ata
3. YEREL İYİLEŞTİRME: her ürünü alt-kümedeki diğer sitelere taşımayı dene;
   genel toplam düşüyorsa kabul et; sabitlenene kadar tekrarla
4. Tüm alt-kümeler arasından en düşük genel toplamı seç
```

Tek-site senaryoları bu enumerasyonun tekil alt-kümeleridir — **ayrı kod yok**.

### Dürüstlük notu — zorunlu

Bu bir **sezgiseldir**, ispatlı optimal değildir. Yerel iyileştirme, eşik etkileşimlerinin
büyük kısmını yakalar ama global optimumu garanti etmez.

TUI bu satırı **"en iyi bulunan kombinasyon"** olarak etiketler, "matematiksel en ucuz"
diye sunmaz.

### Eksik ürün politikası

`prices[(item, site)] is None` → o site için ürün eksik. Site listeden **çıkarılmaz**:
kısmi toplam + `4/5 ürün` rozeti ile gösterilir, eksik ürünler adıyla listelenir.
Tam kapsamlı siteler ayrı grupta üstte durur (kısmi toplam, tam toplamla yanıltıcı
şekilde kıyaslanmasın).

Stoksuz ürün = eksik ürün. `status="suspect"` bir siteden gelen veri = eksik ürün
("pahalı" değil, "bilinmiyor").

---

## 10. Yeni site nasıl eklenir

```bash
# 1. Keşif — profil ve fixture'lar üretilir
parfum-finder discover https://ornek-site.com --id ornek

# 2. Önerilen profili gözden geçir
#    sites/ornek.json içindeki needs_review[] alanlarını kontrol et ve düzelt

# 3. Kargo verisini ELLE gir (asla scrape edilmez)
#    "shipping": { "free_shipping_threshold": 750, "shipping_cost": 89, "notes": "..." }

# 4. Doğrula — offline fixture + canlı site
parfum-finder validate ornek

# 5. Tek site ile deneme araması
parfum-finder search "Dior Sauvage EDP" --site ornek
```

> **Bu dokümanda spekülatif CSS selector veya gerçek site adı yoktur.** Hedef siteler
> henüz belirlenmedi; selector'lar `discover` çıktısından gelecek, tahminden değil.

---

## 11. `validate` — profil bayatlaması

Siteler değişir, profiller bayatlar. `validate` iki modda çalışır:

| Mod | Ne yapar |
|---|---|
| **Offline** | `fixtures/<id>/` altındaki kaydedilmiş HTML'e karşı profili koşturur, beklenen çıktıyla karşılaştırır. Ağ gerektirmez, CI'da çalışır. |
| **Canlı** | Siteye gerçek istek atar, profil hâlâ çalışıyor mu bakar. Bozulmuşsa hangi katmanın (jsonld / endpoint / embedded / css) öldüğünü ve **bir alt katmana düşülüp düşülemeyeceğini** raporlar. |

Ek olarak her profilde `schema_version` ve `discovered_at` bulunur; belirli bir yaştan
eski profiller TUI'de yaş rozetiyle işaretlenir.

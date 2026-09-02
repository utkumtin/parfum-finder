# parfum-finder

Dekant parfüm alışverişi için çoklu-site fiyat/stok karşılaştırma ve sepet optimizasyon
aracı. Tek kullanıcılı, terminal üzerinde çalışan bir TUI.

Kod, [`ARCHITECTURE.md`](ARCHITECTURE.md)'deki modül/akış kararlarını takip eder.

## Kurulum

```bash
uv sync                     # temel bağımlılıklar + dev grubu (ruff, mypy, pytest, pytest-cov)
uv sync --extra browser     # + playwright (opsiyonel, JS-render eden siteler için)
```

`browser` eklentisini kurduktan sonra playwright'ın kendi tarayıcı ikilisi ayrıca
lazım: `uv run playwright install chromium`.

## Kullanım

Alt komutsuz çalıştırmak (`parfum-finder`) doğrudan TUI'yi açar, `tui` komutuyla
aynıdır.

```bash
uv run parfum-finder probe <url>
# bir sitenin hangi fetch stratejisine (http/rendered/vb.) ihtiyaç duyduğunu ölçer

uv run parfum-finder discover <url> --search-url <arama-url> --id <site-id>
# siteyi tarar, JSON-LD/şablon tespitini raporlar, --id verilirse fixtures/<site-id>/
# altına golden fixture olarak kaydeder

uv run parfum-finder validate --live
# sites/ altındaki profilleri fixture'lara karşı (offline) ve --live ile gerçek
# siteye karşı da doğrular

uv run parfum-finder search "Dior Sauvage EDP" --site venco --db data/prices.db
# her siteyi tarar, bulunan fiyatları veritabanına yazar ve satır satır raporlar

uv run parfum-finder search "Dior Sauvage EDP - Creed Aventus - Xerjoff Naxos"
# " - " ile ayırarak tek çalıştırmada en fazla 10 parfüm; aynı sözdizimi arama
# çubuğunda da geçerli

uv run parfum-finder tui --db data/prices.db
# interaktif uygulamayı açar
```

## TUI kısayolları

Arama ekranı:

| Tuş | İşlev |
| --- | --- |
| 1 / 2 / 3 | ml / fiyat / ₺-ml'e göre sırala |
| f | stokta olmayanları filtrele |
| h | fiyat geçmişini göster |
| a | seçili satırı sepete ekle |
| s | sepeti aç |
| escape | arama kutusuna dön |
| q / ctrl+c | çık |

Sepet ekranı:

| Tuş | İşlev |
| --- | --- |
| d | satırı sepetten çıkar |
| + / - | adet artır / azalt |
| r | fiyatları tazele |
| escape | geri |

## Kullanım notları

- `validate` çıkış kodları: `0` her şey temiz, `1` en az bir profil bozuk,
  `2` isteğin kendisi hatalı (var olmayan bir site-id sorulmuş). Varsayılan
  olarak `fixtures/` altındaki kayıtlara karşı offline çalışır; `--live` gerçek
  siteye de gider.
- Her tarama yeni bir `price_snapshots` satırı ekler. Son üç takvim ayındaki
  okumalar eksiksiz tutulur; daha eski kayıtlarda her varyantın UTC ayındaki ilk
  okuması saklanır.
- Bazı dükkanlar orijinallerin yanında klon da satar ve taklit ettiği parfümü
  başlıkta parantez içinde yazar: `Armaf – Club De Nuit Untold (Maison Francis
  Kurkdjian – Baccarat Rouge 540)`. Bir satır aradığınız parfümün klonuysa
  tabloda `KLON ← <orijinal>` etiketiyle görünür. Klon satırları görünür kalır,
  çünkü iyi bir klon orijinal yerine alınabilir; ama farklı bir şişe oldukları
  için ne fiyat geçmişine yazılır ne de sepete eklenebilir.
- Profili bozuk görünen siteler "suspect" (⚠) olarak raporlanır ve sepet
  toplamlarına dahil edilmez. Bunun nedeni fiyatın pahalı değil, bilinmiyor
  olması: sitenin cevabı okunamadığında bir rakam uydurmak yerine o site o
  turda hesaba katılmaz.

## Masaüstü arayüz (geliştirme)

Arka uç ve arayüz iki ayrı süreç olarak çalışır; ikisi de aynı token'ı görmek zorunda.
Vite, `/api` isteklerini (WebSocket dahil) arka uca yönlendirir, yani tarayıcı
tarafında her şey tek origin'dedir.

```bash
uv sync --extra gui
cp ui/.env.local.example ui/.env.local     # VITE_AUTH_TOKEN
PARFUM_FINDER_TOKEN=dev-token uv run uvicorn parfum_finder.api:app --port 8000

cd ui && npm install && npm run dev        # http://localhost:5173
```

Token verilmezse süreç başına rastgele bir tane üretilir — paketlenmiş uygulamanın
davranışı budur, orada token pencereye enjekte edilir.

## Windows masaüstü kurulumu

`.github/workflows/build-windows.yml` her `main` push'unda ve `v*` etiketinde
`windows-latest` üzerinde bir kurulum sihirbazı (`parfum-finder-setup.exe`)
üretir; iş akışının "Upload artifact" adımından indirilebilir, etiketli
sürümlerde ayrıca GitHub Release'e eklenir.

Kurulum admin istemez, `%LOCALAPPDATA%\Programs\parfum-finder` altına kurar.
Bilinmesi gereken iki şey:

- **SmartScreen uyarısı.** Exe imzasız, ilk açılışta Windows "Bilinmeyen
  yayımcı" uyarısı gösterir. "Daha fazla bilgi" → "Yine de çalıştır" ile
  geçilir. v1 için bilinçli olarak kabul edildi, bkz. `build-windows-app.md` §4.6.
- **WebView2 Runtime.** Windows 11'de kurulu gelir; eski Windows 10
  sürümlerinde olmayabilir. Uygulama WebView2 bulamazsa Microsoft'un
  Evergreen Bootstrapper'ına yönlendiren bir mesaj kutusu gösterir, beyaz
  ekran vermez.

### Yeni sürüm yayınlama ve otomatik güncelleme

Uygulama her açılışta GitHub'ın `releases/latest` uç noktasını sorar ve daha
yeni bir sürüm varsa release notlarıyla birlikte bir pencere açar. Kullanıcı
"Güncelle" derse kurulum dosyası indirilir, sessiz kurulum başlar ve uygulama
yeni sürümle yeniden açılır; "Şimdi değil" derse pencere kapanır ve o oturumda
bir daha sorulmaz. Kontrol yalnızca paketlenmiş build'de çalışır.

Yayın adımları:

1. `src/parfum_finder/__init__.py` içindeki `__version__`'ı yükselt (tek doğru
   kaynak; `pyproject.toml` sürümünü de aynı tut).
2. `git tag v<sürüm>` ve `git push --tags`. CI, etiketle `__version__`
   uyuşmuyorsa build'i düşürür.
3. GitHub'da release'i yayınla ve açıklamasına değişiklikleri yaz: kullanıcının
   pencerede okuyacağı metin birebir bu.

CI, kurulum dosyasını release'e `parfum-finder-setup.exe` olarak ekler.
Güncelleme kontrolü release'e eklenmiş ilk `.exe` dosyasını indirir.

Kaynaktan Windows exe üretmek için (CI'ın yaptığının aynısı):

```powershell
cd ui; npm ci; npm run build; cd ..
uv sync --locked --extra gui
cl /nologo /std:c11 /W4 /WX /O2 /MT /DUNICODE /D_UNICODE /Fe:packaging\updater-bootstrapper.exe packaging\updater-bootstrapper.c /link /SUBSYSTEM:WINDOWS shell32.lib
uv run pyinstaller packaging/parfum-finder.spec
.\dist\parfum-finder\parfum-finder.exe --selftest   # pencere açmadan arka ucu dener
```

`cl` komutunu Visual Studio Developer PowerShell içinde çalıştırın. `/MT`,
güncelleme yardımcısının Visual C++ runtime DLL'ine ihtiyaç duymamasını sağlar.

## Geliştirme ortamı

Python tarafı:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy .
uv run pytest
```

Arayüz tarafı (`ui/` içinden):

```bash
npm run typecheck          # src, tests ve e2e, hepsi tek tsconfig'te
npm run test               # vitest + jsdom: birim ve bileşen testleri
npm run test:watch         # geliştirirken
npm run test:coverage
npm run test:e2e           # playwright: gerçek tarayıcı, gerçek arka uç
```

`npm run test:e2e` ilk çalıştırmada bir tarayıcı ister:

```bash
npx playwright install chromium
```

Arka ucu kendisi ayağa kaldırır (`ui/e2e/backend.py`): gerçek FastAPI
uygulaması, gerçek sqlite dosyası, uydurma mağazalar. Ağa çıkmaz, gerçek
sitelere dokunmaz. Ayrıntı: [`ui/TESTING.md`](ui/TESTING.md).

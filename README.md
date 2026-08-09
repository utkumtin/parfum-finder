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
- Fiyatlar append-only saklanır: her tarama yeni bir `price_snapshots` satırı
  ekler, var olan bir kaydın üzerine yazılmaz — bu yüzden bir sitenin fiyat
  geçmişi hiç kaybolmaz.
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

## Geliştirme ortamı

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy .
uv run pytest
```

# parfum-finder

Dekant parfüm alışverişi için çoklu-site fiyat/stok karşılaştırma ve sepet optimizasyon
aracı. Tek kullanıcılı, terminal üzerinde çalışan bir TUI.

Tasarım dokümanları (kod öncesi karar kayıtları — önce bunlar okunur):

| Doküman | İçerik |
|---|---|
| [`PRD.md`](PRD.md) | Problem, kapsam, kabul kriterleri |
| [`TECH_STACK.md`](TECH_STACK.md) | Kütüphane seçimleri ve gerekçeleri |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Modüller, keşif akışı, algoritmalar |
| [`APP_FLOW.md`](APP_FLOW.md) | CLI komutları, ekranlar |
| [`SCHEMA.md`](SCHEMA.md) | Site profil JSON şeması + SQLite şeması |
| [`ROADMAP.md`](ROADMAP.md) | Milestone'lar (M0–M10) ve bağımlılıkları |

## Geliştirme ortamı

```bash
uv sync                     # temel bağımlılıklar + dev grubu (ruff, mypy, pytest, pytest-cov)
uv sync --extra browser     # + playwright (opsiyonel, JS-render eden siteler için)

uv run ruff check .
uv run ruff format .
uv run mypy src
uv run pytest
```

## Durum

Şu an **M0 — İskelet** aşamasındayız (bkz. `ROADMAP.md`). `M2`'den itibaren gerçek site
URL'leri gerekiyor; o eşiğe kadar tamamen offline geliştirilebilir.

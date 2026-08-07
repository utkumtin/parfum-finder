# parfum-finder

Dekant parfüm alışverişi için çoklu-site fiyat/stok karşılaştırma ve sepet optimizasyon
aracı. Tek kullanıcılı, terminal üzerinde çalışan bir TUI.

Kod, [`ARCHITECTURE.md`](ARCHITECTURE.md)'deki modül/akış kararlarını takip eder.

## Geliştirme ortamı

```bash
uv sync                     # temel bağımlılıklar + dev grubu (ruff, mypy, pytest, pytest-cov)
uv sync --extra browser     # + playwright (opsiyonel, JS-render eden siteler için)

uv run ruff check .
uv run ruff format .
uv run mypy src
uv run pytest
```

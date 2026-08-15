# hooks/

Profil şemasının yetmediği tuhaf siteler için opsiyonel Python kaçış kapısı: `<id>.py`.
Üç kanca tanımlanabilir: `before_search` (arama sorgusunu göndermeden önce dönüştürür),
`after_search` (arama sonuçlarını filtreler/düzeltir), `parse_variants` (varyant
çıkarımını tamamen devralır). Kanca eklemek kolay olmamalı. Her yeni ihtiyaç önce
profil şemasının genişletilip genişletilemeyeceği sorusunu doğurmalı.

Şu an boş: `sites/` altındaki altı profilin hiçbiri kanca gerektirmedi, hepsi şema ile
sürülüyor.

## Windows masaüstü uygulamasında bir kısıt

Paketlenmiş (PyInstaller) uygulamada bir kanca `profiles.load_site_hooks()`
üzerinden çalışma anında `importlib` ile yüklenir. PyInstaller paketi statik
analizle çıkarır; bir kancanın çalışma anında import edeceği stdlib modülü bu
analizde görünmüyorsa pakete girmez ve kanca donmuş build'de `ImportError`
verir. Kaynaktan çalıştırmada (`uv run parfum-finder ...`) bu kısıt yok,
sorun sadece kurulan .exe için geçerli. Bir kanca yazacaksan sadece `httpx`,
`selectolax`, `rapidfuzz` gibi projenin zaten paketlediği bağımlılıkları
veya `re`, `json`, `datetime` gibi sık kullanılan stdlib modüllerini import
et; daha egzotik bir modül gerekiyorsa önce bunu bildir.

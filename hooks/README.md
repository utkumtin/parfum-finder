# hooks/

Profil şemasının yetmediği tuhaf siteler için opsiyonel Python kaçış kapısı: `<id>.py`.
Üç kanca tanımlanabilir: `before_search` (arama sorgusunu göndermeden önce dönüştürür),
`after_search` (arama sonuçlarını filtreler/düzeltir), `parse_variants` (varyant
çıkarımını tamamen devralır). Kanca eklemek kolay olmamalı. Her yeni ihtiyaç önce
profil şemasının genişletilip genişletilemeyeceği sorusunu doğurmalı.

Şu an boş: `sites/` altındaki altı profilin hiçbiri kanca gerektirmedi, hepsi şema ile
sürülüyor.

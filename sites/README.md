# sites/

Her dosya bir site profili: `<id>.json`. Keşif script'i tarafından üretilir, sonra elle
gözden geçirilir. Özellikle düşük güvenli alanlar ve her zaman elle girilen kargo
bilgisi (ücretsiz kargo eşiği, kargo ücreti, notlar) kontrol edilmeli.

Bu klasör Python paketinin dışındadır (`src/parfum_finder/` değil), çünkü kullanıcı
tarafından düzenlenen veridir, dağıtılan kodun parçası değil.

`splitcim` dışındaki altı profilin `shipping` alanı şu an gerçek veri taşımıyor: kargo bilgisi hiç
toplanmadı (tasarım gereği, bkz. `docs/discovery-report.md`), `shipping_cost_kurus: 0`
gerçek bir ölçüm değil, sadece şemanın istediği bir sayı. Her profilin `needs_review[]`
dizisi bunu tek tek işaretliyor; M8'in kargo hesapları güvenilir olmadan önce hepsi elle
doldurulmalı.

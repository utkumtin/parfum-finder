# Arayüz testleri

İki katman var ve ikisinin işi ayrı.

| Katman | Nerede | Ne ile | Ne kadar sürer |
|---|---|---|---|
| Birim + bileşen | `tests/` | vitest + jsdom + Testing Library | ~2 sn |
| Uçtan uca | `e2e/` | playwright + chromium + gerçek arka uç | ~10 sn |

```bash
npm run test          # jsdom katmanı
npm run test:watch
npm run test:coverage
npm run test:e2e      # tarayıcı katmanı
```

`test:e2e` ilk kez çalıştırılmadan önce bir kere: `npx playwright install chromium`.

---

## jsdom katmanı (`tests/`)

`src/` ağacını aynalar: `tests/lib/format.test.ts`, `tests/screens/ResultsScreen.test.tsx`.
Bileşenler gerçek React ağacında render edilir, gerçek olmayan tek şey ağ.

**Arka uç `tests/helpers/server.ts` ile taklit edilir.** Uygulamanın ağ yüzeyi
tam olarak iki yerden geçiyor — `api/client.ts` içindeki global `fetch` ve
`api/ws.ts` içindeki global `WebSocket` — ve ikisi de burada değiştirilir. Bunun
için bir istek yakalama kütüphanesi kullanılmadı: bir teste kalıplı yanıttan
fazlası gerekiyor, olayın **ne zaman** geldiğine karar etmesi gerekiyor. Tablo
okunmadan bitmiş bir tarama, bug'ların yaşadığı sıra değil.

```ts
const server = installFakeServer();          // mount'ta okunan uçların hepsi cevaplı
server.reply("POST /api/basket/items", { detail: "confirm" }, 409);
const socket = await server.socket("/api/search/search-1");
act(() => socket.emit({ type: "scan_finished", error_count: 0 }));
act(() => socket.refuse(4409));              // arka ucun soketi reddetmesi
```

Tanımlanmamış bir uca istek gidince helper **hata atar**, 404 dönmez: ekranların
hata yollarındaki `catch` blokları sessiz kalmak üzere yazılmış, sessiz bir 404
tam da bu testlerin yakalaması gereken uyuşmazlığı yutardı.

Tel üzerindeki şekiller `tests/helpers/fixtures.ts` içindeki üreticilerden
gelir; bir test yalnızca kendi konusu olan alanları yazar.

## Tarayıcı katmanı (`e2e/`)

`ui/dist` build edilir, `ui/e2e/backend.py` onu **kendisi servis eder** —
paketlenmiş Windows uygulamasının yaptığının aynısı: tek origin, dev-server
proxy'si yok, token sayfaya arka uç tarafından enjekte edilmiş. Vite dev
server'ını sürmek, hiç dağıtılmayan bir kurulumu test etmek olurdu.

Ağın üstündeki her şey gerçek: FastAPI route'ları, tarama servisi, matcher,
ranking, sepet optimizasyonu ve gerçek bir sqlite dosyası. Yalnızca `SiteRunner`
değiştirilir — gerçek mağazalara giden bir tarayıcı testi yavaş olur, çevrimdışı
çalışmaz ve bir fiyat her değiştiğinde cevabını değiştirir.

İki uydurma mağaza (`Alfa Dekant`, `Beta Dekant`) bilerek farklı kargo
politikalarıyla tanımlı: Alfa dekant başına daha ucuz ama kargosu pahalı, yani
hangi planın kazandığı sepete göre değişiyor, sabite göre değil. Kataloğu
değiştirmek e2e beklentilerini değiştirir, ikisi aynı dosyanın iki ucu değil —
`backend.py` içindeki `_CATALOGUE` ile `e2e/*.spec.ts` içindeki sayılar elle
eşleşir.

Testler **seri** koşar (`workers: 1`): hepsi tek arka uç sürecini ve içindeki tek
sepeti paylaşıyor. `basket.spec.ts` her testten önce sepeti API üzerinden
boşaltır. Veritabanı her koşuda yeni bir geçici dosyadır.

## Ne test edilmiyor

- **CSS ve görsel bozulma.** jsdom düzen hesaplamaz; playwright hesaplar ama
  ekran görüntüsü karşılaştırması kurulmadı.
- **WebView2'ye özgü davranış.** Chromium, Edge'in motoru ama aynı build değil.
  Windows'a özgü bir render sorunu buradan geçer.
- **Gerçek site profilleri.** Adapter tarafının testi Python'da, `fixtures/`
  altındaki golden HTML dosyalarıyla; bkz. `uv run parfum-finder validate`.

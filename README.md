# Pixabay API ile Streamlit Gorsel Arama ve Indirme

Pixabay API kullanarak gorsel arama, filtreleme, sayfalama ve indirme yapan Streamlit uygulamasi.
Arayuz Turkce/English dil secimi, acik/koyu tema ve gelistirilmis kart yapisi ile calisir.

## Ozellikler
- Pixabay API entegrasyonu (arama + filtreler)
- Turkce / English arayuz (menu ve filtre etiketleri dile gore degisir)
- Acik / Koyu tema (varsayilan: koyu tema)
- Grid gorunum + alt sayfalama
- Cihaza indirme (`Cihaza Kaydet` butonu)
- Tek tik indirme: `Cihaza Kaydet` butonu `download_button` ile dogrudan indirme sunar
- API cagri cache (`st.cache_data`)
- Demo fallback API key destegi (uyari ile)
- API hata UX: `st.error` + cozum onerileri
- Enter ile arama + buton ile arama

## Kurulum
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## PIXABAY_KEY Ayari (Onerilen)
### 1) Streamlit secrets (onerilen)
Proje klasorunde `.streamlit/secrets.toml` olusturun:

```toml
PIXABAY_KEY = "YOUR_PIXABAY_API_KEY"
```

### 2) Environment variable
```bash
export PIXABAY_KEY="YOUR_PIXABAY_API_KEY"
```

## Streamlit Cloud Deployment Notu
- Streamlit Cloud'da API key eklemek icin: `App > Settings > Secrets`
- `PIXABAY_KEY = "YOUR_PIXABAY_API_KEY"` degerini Secrets alanina ekleyin (demo key ile rate limit riski vardir)

## Demo Key (Fallback) Notu
Uygulama, `PIXABAY_KEY` bulunamazsa demo fallback key ile calisabilir. Bu key paylasimli oldugu icin **rate limit** nedeniyle aramalar zaman zaman yavaslayabilir veya `HTTP 429` hatasi alinabilir. Uygulama bu durumda ekranda `st.warning` ile demo key uyarisi gosterir.

## Calistirma
```bash
streamlit run app.py
```

Uygulama acildiginda:
- Varsayilan tema `Koyu Tema` olarak gelir
- Dil secimi `Turkce` olarak baslar
- Arama yapilmadan once ornek gorseller gosterilir

### Ornek komutlar
```bash
# Virtualenv aktifken
streamlit run app.py

# Farkli portta calistirma
streamlit run app.py --server.port 8502

# Environment variable ile tek satir calistirma
PIXABAY_KEY="YOUR_PIXABAY_API_KEY" streamlit run app.py
```

## Ekran Goruntusu
README icin kendi ekran goruntunuzu ekleyebilirsiniz.

Ornek markdown:
```md
![Uygulama Ekran Goruntusu](docs/app-screenshot.png)
```

## Hata Yonetimi (UX)
API hatalarinda uygulama `st.error` ile hata mesaji ve ek olarak **Cozum onerisi** gosterir:
- API key dogru mu?
- Rate limit dolmus olabilir mi?
- Filtreler cok kisitlayici mi?
- Baglanti/Cloud log kontrolu

## Performans Notu (Indirme)
Bu surumde tek tik indirme icin `download_button` kullanilir. `download_button` veriyi render sirasinda istedigi icin sayfadaki kartlar icin gorsel bytes fetch islemleri yapilabilir. Buna ragmen akisin stabil ve kullanici dostu olmasi icin bu tercih edilmistir. Tekrar renderlarda `st.cache_data` yardimci olur.

## Guvenlik Notu
Gercek bir projede API key dosya/repo icine konmaz. `st.secrets` veya environment variable (`PIXABAY_KEY`) kullanilmalidir. Kod icindeki fallback key sadece demo/odev kolayligi icin dusunulmelidir; paylasimli key oldugu icin kotaya takilma riski vardir.

## Pagination / Limit Notu
Pixabay tarafinda derin sayfalama pratikte sinirlidir. Bu nedenle UI'da toplam sayfa sayisi **500** ile sinirlanir.

UI seviyesinde sinirlar:
- `per_page` secimi sadece desteklenen degerlerden yapilir (`20`, `30`, `50`)
- Sayfa gecisleri `Onceki / Sonraki` butonlari ve ortadaki sayfa inputu ile yapilabilir
- Sayfa inputunda min/max degeri mevcut toplam sayfaya gore sinirlanir

## UI Notlari (Son Hali)
- Ustte sticky header + tema/dil kontrolleri
- Arama kutusu + filtre paneli (Pixabay tarzinda)
- Sonuc akisi (tek dogru siralama): once gorsel grid, sonra `Summary + Pagination`
- En altta `Basa Don` linki
- Header basligi dil secimine gore degisir:
  - TR: `Pixabay Gorsel Arama`
  - EN: `Pixabay Visual Search`

## Manual Test Ornekleri
Asagidaki mini testleri `python3` REPL veya gecici script ile deneyebilirsiniz.

### `slugify_tags()`
```python
from app import slugify_tags

print(slugify_tags("car, volkswagen, old"))  # car
print(slugify_tags("Istanbul Night View"))   # istanbul-night-view
print(slugify_tags(""))                      # image
```

### `build_params()`
```python
from app import build_params

params = build_params(
    query="istanbul",
    lang="tr",
    image_type="photo",
    category="travel",
    orientation="horizontal",
    color="blue",
    safesearch=True,
    page=2,
    per_page=20,
)
print(params["page"], params["per_page"], params["category"], params["colors"])
# Beklenen: 2 20 travel blue
```

## Kod Kalitesi / Format
Kod `black` ile format kontrolunden gecirildi (`python3 -m black app.py`).

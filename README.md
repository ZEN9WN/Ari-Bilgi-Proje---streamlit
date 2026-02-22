# Pixabay API ile Streamlit Gorsel Arama ve Indirme

Pixabay API kullanarak gorsel arama, filtreleme, sayfalama ve indirme yapan Streamlit uygulamasi.

## Ozellikler
- Pixabay API entegrasyonu (arama + filtreler)
- Turkce / English arayuz
- Acik / Koyu tema
- Grid gorunum ve sayfalama
- Cihaza indirme (`download_button`)
- API cagri cache (`st.cache_data`)
- Demo fallback API key destegi (uyari ile)

## Kurulum
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## PIXABAY_KEY Ayari (Onerilen)
### 1) Streamlit secrets (onerilen)
Proje klasorunde `/Users/emirzengin/Documents/New project/.streamlit/secrets.toml` olusturun:

```toml
PIXABAY_KEY = "YOUR_PIXABAY_API_KEY"
```

### 2) Environment variable
```bash
export PIXABAY_KEY="YOUR_PIXABAY_API_KEY"
```

## Demo Key (Fallback) Notu
Uygulama, `PIXABAY_KEY` bulunamazsa demo fallback key ile calisabilir. Bu key paylasimli oldugu icin **rate limit** nedeniyle aramalar zaman zaman yavaslayabilir veya `HTTP 429` hatasi alinabilir.

## Calistirma
```bash
streamlit run app.py
```

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

## Guvenlik Notu
Gercek bir projede API key dosya/repo icine konmaz. `st.secrets` veya environment variable (`PIXABAY_KEY`) kullanilmalidir. Kod icindeki fallback key sadece demo/odev kolayligi icin dusunulmelidir; paylasimli key oldugu icin kotaya takilma riski vardir.

## Pagination / Limit Notu
Pixabay tarafinda derin sayfalama pratikte sinirlidir. Bu nedenle uygulamada `page` degeri `1..500` araligina clamp edilir ve UI'da da toplam sayfa sayisi **500** ile sinirlanir.

Ek validasyonlar:
- `per_page` sadece desteklenen degerlerden biri olur (`20`, `30`, `50`)
- `page` negatif/0 girilirse `1` olarak duzeltilir

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
    page=999,   # clamp -> 500
    per_page=999,  # fallback -> 20
)
print(params["page"], params["per_page"], params["category"], params["colors"])
# Beklenen: 500 20 travel blue
```

## Kod Kalitesi / Format
Kod `black` ile format kontrolunden gecirildi (`python3 -m black app.py`).


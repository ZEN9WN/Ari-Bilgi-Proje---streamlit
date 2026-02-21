<<<<<<< ours
from __future__ import annotations

import math
import os
=======
>>>>>>> theirs
import re
from pathlib import Path
from typing import Any, Dict, List

import requests
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

API_URL = "https://pixabay.com/api/"
DEFAULT_API_KEY = "49738243-e25f3b714305e2a1c2cd97721"
CATEGORIES = [
    "all",
    "backgrounds",
    "fashion",
    "nature",
    "science",
    "education",
    "feelings",
    "health",
    "people",
    "religion",
    "places",
    "animals",
    "industry",
    "computer",
    "food",
    "sports",
    "transportation",
    "travel",
    "buildings",
    "business",
    "music",
]
COLORS = [
    "all",
    "grayscale",
    "transparent",
    "red",
    "orange",
    "yellow",
    "green",
    "turquoise",
    "blue",
    "lilac",
    "pink",
    "white",
    "gray",
    "black",
    "brown",
]
IMAGE_TYPES = ["photo", "illustration", "vector"]
PER_PAGE_OPTIONS = [20, 30, 50]
QUICK_SEARCHES = ["istanbul", "cat", "nature", "pubg", "sports", "business"]


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');

        * {
          font-family: 'Manrope', sans-serif;
        }

        .stApp {
          background:
            radial-gradient(1100px 420px at 10% 0%, #d9fff2 0%, rgba(217,255,242,0) 48%),
            radial-gradient(900px 360px at 100% 0%, #ddebff 0%, rgba(221,235,255,0) 46%),
            #f6f8fb;
        }

        [data-testid="stSidebar"] {
          display: none;
        }

        .top-hero {
          background: linear-gradient(120deg, #0f766e 0%, #155e75 52%, #1d4d8f 100%);
          color: white;
          border-radius: 18px;
          padding: 18px 22px;
          margin-bottom: 14px;
          box-shadow: 0 14px 30px rgba(15, 23, 42, 0.16);
        }

        .top-hero h1 {
          margin: 0;
          font-size: 1.9rem;
          font-weight: 800;
          letter-spacing: 0.2px;
        }

        .top-hero p {
          margin: 7px 0 0;
          opacity: 0.92;
        }

        .glass-card {
          background: rgba(255, 255, 255, 0.9);
          border: 1px solid #e0e7ef;
          border-radius: 16px;
          padding: 14px;
          box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
        }

        .quick-title {
          font-size: 0.95rem;
          color: #445066;
          margin: 8px 0 10px;
          font-weight: 700;
        }

        .result-head {
          margin-top: 10px;
          margin-bottom: 8px;
        }

        .kpi-note {
          color: #5b6775;
          font-size: 0.85rem;
          margin-top: 6px;
        }

        .stButton > button, .stDownloadButton > button, .stLinkButton > a {
          border-radius: 10px;
          font-weight: 650;
          min-height: 2.7rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def safe_rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def get_pixabay_api_key() -> str:
    try:
<<<<<<< ours
        secret_key = str(st.secrets["PIXABAY_KEY"]).strip()
        if secret_key:
            return secret_key
    except Exception:
        pass

    return DEFAULT_API_KEY


def get_download_dir() -> Path:
    for candidate in [Path("downloads"), Path("/tmp/downloads")]:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except OSError:
            continue
    raise RuntimeError("İndirme klasörü oluşturulamadı. Yazma izinlerini kontrol edin.")


def slugify_tags(tags: str) -> str:
    raw = tags.split(",")[0].strip().lower() if tags else "image"
    slug = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return slug or "image"
=======
        return st.secrets["PIXABAY_KEY"]
    except (StreamlitSecretNotFoundError, KeyError):
        return DEFAULT_API_KEY
>>>>>>> theirs


def filename_for_item(image_id: int, tags: str) -> str:
    return f"pixabay_{image_id}_{slugify_tags(tags)}.jpg"


def build_params(
    query: str,
    category: str,
    color: str,
    safesearch: bool,
    page: int,
    per_page: int,
    image_type: str,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "key": get_pixabay_api_key(),
        "q": query,
        "image_type": image_type,
        "per_page": per_page,
        "page": page,
        "safesearch": str(safesearch).lower(),
    }
    if category != "all":
        params["category"] = category
    if color != "all":
        params["colors"] = color
    return params


@st.cache_data(show_spinner=False, ttl=300)
def search_pixabay(
    query: str,
    category: str,
    color: str,
    safesearch: bool,
    page: int,
    per_page: int,
    image_type: str = "photo",
) -> Dict[str, Any]:
    params = build_params(
        query=query,
        category=category,
        color=color,
        safesearch=safesearch,
        page=page,
        per_page=per_page,
        image_type=image_type,
    )

    try:
        response = requests.get(API_URL, params=params, timeout=18)
    except requests.RequestException as exc:
        raise RuntimeError(f"API bağlantı hatası: {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(f"Pixabay API HTTP hatası: {response.status_code}")

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError("API yanıtı JSON formatında değil.") from exc

    if "hits" not in payload:
        raise RuntimeError("API yanıtında 'hits' alanı yok.")

    return payload


@st.cache_data(show_spinner=False, ttl=1800)
def get_showcase_images() -> List[Dict[str, Any]]:
    all_hits: List[Dict[str, Any]] = []
    seen_ids = set()
    for q in ["nature", "travel", "technology", "animals"]:
        try:
            data = search_pixabay(
                query=q,
                category="all",
                color="all",
                safesearch=True,
                page=1,
                per_page=12,
                image_type="photo",
            )
        except RuntimeError:
            continue

        for hit in data.get("hits", []):
            image_id = hit.get("id")
            if image_id in seen_ids:
                continue
            seen_ids.add(image_id)
            all_hits.append(hit)
            if len(all_hits) >= 12:
                return all_hits

    return all_hits


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_image_bytes(image_url: str) -> bytes:
    try:
        response = requests.get(image_url, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Görsel indirilemedi: {exc}") from exc
    return response.content

<<<<<<< ours

def save_image_locally(image_url: str, image_id: int, tags: str) -> Path:
    data = fetch_image_bytes(image_url)
    download_dir = get_download_dir()
=======
    download_dir = Path("downloads")
    download_dir.mkdir(exist_ok=True)
>>>>>>> theirs

    file_path = download_dir / filename_for_item(image_id=image_id, tags=tags)
    counter = 1
    while file_path.exists():
        file_path = download_dir / f"pixabay_{image_id}_{slugify_tags(tags)}_{counter}.jpg"
        counter += 1

    file_path.write_bytes(data)
    return file_path


def init_state() -> None:
    defaults = {
        "search_active": False,
        "search_query": "",
        "category": "all",
        "color": "all",
        "image_type": "photo",
        "show_adult": False,
        "per_page": 20,
        "page": 1,
        "columns": 3,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_state() -> None:
    for key in [
        "search_active",
        "search_query",
        "category",
        "color",
        "image_type",
        "show_adult",
        "per_page",
        "page",
        "columns",
    ]:
        if key in st.session_state:
            del st.session_state[key]
    init_state()


def apply_quick_search(query: str) -> None:
    st.session_state.search_query = query
    st.session_state.page = 1
    st.session_state.search_active = True
    safe_rerun()


def render_top_hero() -> None:
    st.markdown(
        """
        <div class="top-hero">
            <h1>Pixabay Visual Search</h1>
            <p>Google tarzı hızlı arama + Pixabay filtreleri + tek tık indirme.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_search_panel() -> None:
    with st.container(border=True):
        st.markdown("#### Arama")
        q_col, b_col = st.columns([7, 1.6])
        with q_col:
            st.text_input(
                "Görsel arama",
                key="search_query",
                placeholder="Pixabay'da görsel ara (ör: istanbul, cat, pubg)",
                label_visibility="collapsed",
            )
        with b_col:
            search_clicked = st.button("Ara", type="primary", use_container_width=True)

        with st.expander("Filtreler", expanded=True):
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                st.selectbox("Görsel tipi", IMAGE_TYPES, key="image_type")
            with f2:
                st.selectbox(
                    "Kategori",
                    options=CATEGORIES,
                    key="category",
                    format_func=lambda x: "Hepsi" if x == "all" else x,
                )
            with f3:
                st.selectbox(
                    "Renk",
                    options=COLORS,
                    key="color",
                    format_func=lambda x: "Hepsi" if x == "all" else x,
                )
            with f4:
                st.selectbox("Sayfa başına sonuç", PER_PAGE_OPTIONS, key="per_page")

            opt1, opt2 = st.columns(2)
            with opt1:
                st.slider("Grid kolon", min_value=2, max_value=4, step=1, key="columns")
            with opt2:
                st.toggle("Adult içerikleri göster", key="show_adult")

            a1, a2, a3 = st.columns([1, 1, 1])
            with a1:
                apply_filter_clicked = st.button("Filtreyi Uygula", use_container_width=True)
            with a2:
                reset_clicked = st.button("Sıfırla", use_container_width=True)
            with a3:
                refresh_clicked = st.button("Yenile", use_container_width=True)

    if reset_clicked:
        reset_state()
        st.rerun()

    if search_clicked or apply_filter_clicked or refresh_clicked:
        cleaned = st.session_state.search_query.strip()
        if not cleaned:
            st.warning("Lütfen arama kelimesi girin.")
            st.session_state.search_active = False
            return

        st.session_state.search_query = cleaned
        st.session_state.page = 1
        st.session_state.search_active = True


def render_quick_searches() -> None:
    st.markdown("<div class='quick-title'>Hızlı Aramalar</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, term in enumerate(QUICK_SEARCHES):
        with cols[i % 3]:
            if st.button(term.title(), key=f"quick_search_{term}", use_container_width=True):
                apply_quick_search(term)


<<<<<<< ours
def render_showcase() -> None:
    st.markdown("### Örnek Görseller")
    st.caption("Arama yapmadan önce ilham almak için örnek galeriyi görebilirsin.")
=======
            st.session_state.search_query = cleaned
            st.session_state.category = category
            st.session_state.color = color
            st.session_state.image_type = image_type
            st.session_state.safesearch = not show_adult
            st.session_state.per_page = per_page
            st.session_state.columns = columns
            st.session_state.page = 1
            st.session_state.search_active = True
>>>>>>> theirs

    images = get_showcase_images()
    if not images:
        st.info("Örnek görseller yüklenemedi. İnternet bağlantısı veya API limiti kontrol edilmeli.")
        return

    cols = st.columns(4)
    for i, item in enumerate(images[:12]):
        with cols[i % 4]:
            preview_url = item.get("webformatURL") or item.get("previewURL")
            if preview_url:
                st.image(preview_url, use_container_width=True)
            st.caption(f"{item.get('tags', '-')}")


def render_summary(total_hits: int, hits: List[Dict[str, Any]]) -> None:
    likes_total = sum(int(item.get("likes", 0)) for item in hits)
    views_total = sum(int(item.get("views", 0)) for item in hits)
    downloads_total = sum(int(item.get("downloads", 0)) for item in hits)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Toplam Sonuç", total_hits)
    m2.metric("Bu Sayfada Beğeni", likes_total)
    m3.metric("Bu Sayfada Görüntülenme", views_total)
    m4.metric("Bu Sayfada İndirme", downloads_total)


def render_pagination(total_hits: int) -> None:
    total_pages = max(1, min(math.ceil(total_hits / st.session_state.per_page), 500))

    c1, c2, c3, c4 = st.columns([1, 1.4, 1.4, 1])
    with c1:
<<<<<<< ours
        if st.button("◀ Önceki", key=f"{key_prefix}_prev", disabled=st.session_state.page <= 1, use_container_width=True):
=======
        if st.button("◀ Önceki", disabled=st.session_state.page <= 1, use_container_width=True):
>>>>>>> theirs
            st.session_state.page -= 1
<<<<<<< ours
            safe_rerun()
    with c2:
=======
            st.rerun()
    with pager_col2:
>>>>>>> theirs
        selected_page = st.number_input(
            "Sayfa",
            min_value=1,
            max_value=total_pages,
            value=st.session_state.page,
            step=1,
        )
        if int(selected_page) != st.session_state.page:
            st.session_state.page = int(selected_page)
<<<<<<< ours
            safe_rerun()
    with c3:
        st.markdown(f"<div class='kpi-note'>Toplam sayfa: <b>{total_pages}</b></div>", unsafe_allow_html=True)
    with c4:
<<<<<<< ours
        if st.button("Sonraki ▶", key=f"{key_prefix}_next", disabled=st.session_state.page >= total_pages, use_container_width=True):
=======
        if st.button("Sonraki ▶", disabled=st.session_state.page >= total_pages, use_container_width=True):
>>>>>>> theirs
=======
            st.rerun()
    with pager_col3:
        if st.button("Sonraki", disabled=st.session_state.page >= total_pages):
>>>>>>> theirs
            st.session_state.page += 1
            st.rerun()


def render_card(item: Dict[str, Any], key_prefix: str) -> None:
    image_id = int(item.get("id", 0))
    tags = str(item.get("tags", "image"))
    user = str(item.get("user", "-"))
    likes = int(item.get("likes", 0))
    views = int(item.get("views", 0))
    downloads = int(item.get("downloads", 0))
    width = item.get("imageWidth", "?")
    height = item.get("imageHeight", "?")

    preview_url = item.get("webformatURL") or item.get("previewURL") or item.get("largeImageURL")
    image_url = item.get("largeImageURL") or item.get("webformatURL")

    with st.container(border=True):
        if preview_url:
            st.image(preview_url, use_container_width=True)
        else:
            st.info("Önizleme görseli yok.")

        st.markdown(f"**Etiketler:** {tags}")
        st.markdown(f"**Yükleyen:** {user}")
        m1, m2, m3 = st.columns(3)
        m1.metric("Beğeni", likes)
        m2.metric("Görüntülenme", views)
        m3.metric("İndirme", downloads)
        st.caption(f"Çözünürlük: {width} x {height}")

<<<<<<< ours
        d1, d2 = st.columns(2)
        with d1:
            if image_url:
                if hasattr(st, "link_button"):
                    st.link_button("Görseli aç", url=image_url, use_container_width=True)
                else:
                    st.markdown(f"[Görseli aç]({image_url})")
            else:
                st.button("Görseli aç", disabled=True, use_container_width=True)
=======
        file_name = filename_for_item(image_id=image_id, tags=tags)
        dl1, dl2 = st.columns(2)

        with dl1:
            if image_url:
                try:
                    image_bytes = fetch_image_bytes(image_url)
                    st.download_button(
                        "Dosyayı indir",
                        data=image_bytes,
                        file_name=file_name,
                        mime="image/jpeg",
                        key=f"{key_prefix}_download_btn_{image_id}",
                        use_container_width=True,
                    )
                except RuntimeError:
                    st.button("Dosyayı indir", disabled=True, use_container_width=True)
            else:
                st.button("Dosyayı indir", disabled=True, use_container_width=True)
>>>>>>> theirs

        with d2:
            if st.button("Cihaza kaydet", key=f"{key_prefix}_save_{image_id}", use_container_width=True):
                if not image_url:
                    st.error("Bu görsel için indirilebilir URL bulunamadı.")
                else:
                    try:
                        saved = save_image_locally(image_url=image_url, image_id=image_id, tags=tags)
                        st.success(f"Kaydedildi: {saved}")
                    except RuntimeError as exc:
                        st.error(str(exc))


def render_results_grid(hits: List[Dict[str, Any]]) -> None:
    cols = st.columns(st.session_state.columns)
    for i, item in enumerate(hits):
        with cols[i % st.session_state.columns]:
            render_card(item=item, key_prefix=f"card_{i}")


def main() -> None:
    st.set_page_config(
        page_title="Pixabay Görsel Arama",
        page_icon="🖼️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    init_state()
    inject_custom_css()
    render_top_hero()
    render_search_panel()
    render_quick_searches()

    if not st.session_state.search_active:
        render_showcase()
        return

    with st.spinner("Pixabay'dan sonuçlar getiriliyor..."):
        try:
            data = search_pixabay(
                query=st.session_state.search_query,
                category=st.session_state.category,
                color=st.session_state.color,
                safesearch=not st.session_state.show_adult,
                page=st.session_state.page,
                per_page=st.session_state.per_page,
                image_type=st.session_state.image_type,
            )
        except RuntimeError as exc:
            st.error(str(exc))
            return

    hits: List[Dict[str, Any]] = data.get("hits", [])
    total_hits = int(data.get("totalHits", 0))

    if total_hits == 0 or not hits:
        st.warning("Sonuç bulunamadı. Farklı bir kelime veya filtre deneyin.")
        render_showcase()
        return

    render_summary(total_hits=total_hits, hits=hits)
    st.markdown("### Sonuçlar")
    render_pagination(total_hits=total_hits)
    render_results_grid(hits=hits)
    render_pagination(total_hits=total_hits)


if __name__ == "__main__":
    main()

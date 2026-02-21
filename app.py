from __future__ import annotations

import math
import os
import re
from pathlib import Path
from typing import Any, Dict, List

import requests
import streamlit as st

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


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        :root {
          --bg-soft: #f7f6f2;
          --card: #ffffff;
          --ink: #112233;
          --muted: #5b6775;
          --primary: #0f766e;
          --accent: #f59e0b;
          --line: #d9dee7;
        }

        .stApp {
          background:
            radial-gradient(1200px 500px at 0% 0%, #d9f7ef 0%, transparent 45%),
            radial-gradient(800px 400px at 100% 0%, #fdecc8 0%, transparent 45%),
            var(--bg-soft);
        }

        .hero {
          background: linear-gradient(120deg, #0f766e 0%, #155e75 52%, #1d4d8f 100%);
          color: white;
          border-radius: 16px;
          padding: 20px 22px;
          margin-bottom: 16px;
          box-shadow: 0 10px 28px rgba(16, 42, 67, 0.18);
        }

        .hero h2 {
          margin: 0 0 6px 0;
          font-size: 1.6rem;
          letter-spacing: 0.2px;
        }

        .hero p {
          margin: 0;
          opacity: 0.92;
          font-size: 0.95rem;
        }

        .meta-chip {
          display: inline-block;
          margin-top: 10px;
          margin-right: 8px;
          padding: 4px 10px;
          border-radius: 999px;
          background: rgba(255, 255, 255, 0.16);
          font-size: 0.8rem;
        }

        .result-card {
          background: var(--card);
          border: 1px solid var(--line);
          border-radius: 14px;
          padding: 12px;
          box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
        }

        .kpi {
          font-size: 0.82rem;
          color: var(--muted);
          margin-top: 6px;
        }

        .stButton > button, .stDownloadButton > button {
          border-radius: 10px;
          border: 1px solid #c8d0db;
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
    env_key = os.getenv("PIXABAY_KEY", "").strip()
    if env_key:
        return env_key

    try:
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

    raise RuntimeError("İndirme klasörü oluşturulamadı. Yazma izinleri kontrol edilmeli.")


def slugify_tags(tags: str) -> str:
    raw = tags.split(",")[0].strip().lower() if tags else "image"
    slug = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return slug or "image"


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


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_image_bytes(image_url: str) -> bytes:
    try:
        response = requests.get(image_url, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Görsel indirilemedi: {exc}") from exc
    return response.content


def save_image_locally(image_url: str, image_id: int, tags: str) -> Path:
    data = fetch_image_bytes(image_url)
    download_dir = get_download_dir()

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
        "safesearch": True,
        "per_page": 20,
        "page": 1,
        "columns": 3,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def clear_prepared_downloads() -> None:
    for key in list(st.session_state.keys()):
        if "_prepared_" in key:
            del st.session_state[key]


def reset_state() -> None:
    clear_prepared_downloads()
    for key in [
        "search_active",
        "search_query",
        "category",
        "color",
        "image_type",
        "safesearch",
        "per_page",
        "page",
        "columns",
    ]:
        if key in st.session_state:
            del st.session_state[key]
    init_state()


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <h2>Pixabay Görsel Arama</h2>
            <p>Arama yap, filtrele, kartları incele ve tek tıkla indir.</p>
            <span class="meta-chip">Cache aktif</span>
            <span class="meta-chip">Cloud uyumlu</span>
            <span class="meta-chip">Sayfalama destekli</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.subheader("Arama ve Filtreler")
        with st.form("search_form", clear_on_submit=False):
            query = st.text_input(
                "Görsel arama",
                value=st.session_state.search_query,
                placeholder="cat, istanbul, pubg...",
            )
            image_type = st.selectbox("Görsel tipi", IMAGE_TYPES, index=IMAGE_TYPES.index(st.session_state.image_type))
            category = st.selectbox(
                "Kategori",
                options=CATEGORIES,
                index=CATEGORIES.index(st.session_state.category),
                format_func=lambda x: "Hepsi" if x == "all" else x,
            )
            color = st.selectbox(
                "Renk",
                options=COLORS,
                index=COLORS.index(st.session_state.color),
                format_func=lambda x: "Hepsi" if x == "all" else x,
            )
            per_page = st.selectbox(
                "Sayfa başına sonuç",
                PER_PAGE_OPTIONS,
                index=PER_PAGE_OPTIONS.index(st.session_state.per_page),
            )
            columns = st.slider("Grid kolon", min_value=2, max_value=4, value=st.session_state.columns, step=1)
            show_adult = st.toggle("Adult içerikleri göster", value=not st.session_state.safesearch)

            left, right = st.columns(2)
            with left:
                search_clicked = st.form_submit_button("Ara", use_container_width=True)
            with right:
                reset_clicked = st.form_submit_button("Sıfırla", use_container_width=True)

        if reset_clicked:
            reset_state()
            safe_rerun()

        if search_clicked:
            cleaned = query.strip()
            if not cleaned:
                st.warning("Lütfen arama kelimesi girin.")
                st.session_state.search_active = False
                return

            st.session_state.search_query = cleaned
            st.session_state.category = category
            st.session_state.color = color
            st.session_state.image_type = image_type
            st.session_state.safesearch = not show_adult
            st.session_state.per_page = per_page
            st.session_state.columns = columns
            st.session_state.page = 1
            st.session_state.search_active = True
            clear_prepared_downloads()

        st.caption("İpucu: Streamlit Cloud'da API key için Settings > Secrets kısmına PIXABAY_KEY ekleyin.")


def render_summary(total_hits: int, hits: List[Dict[str, Any]]) -> None:
    likes_total = sum(int(item.get("likes", 0)) for item in hits)
    views_total = sum(int(item.get("views", 0)) for item in hits)
    downloads_total = sum(int(item.get("downloads", 0)) for item in hits)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Toplam Sonuç", total_hits)
    m2.metric("Bu Sayfada Beğeni", likes_total)
    m3.metric("Bu Sayfada Görüntülenme", views_total)
    m4.metric("Bu Sayfada İndirme", downloads_total)


def render_pagination(total_hits: int, key_prefix: str) -> None:
    total_pages = max(1, min(math.ceil(total_hits / st.session_state.per_page), 500))

    c1, c2, c3, c4 = st.columns([1, 1.4, 1.4, 1])
    with c1:
        if st.button(
            "◀ Önceki",
            key=f"{key_prefix}_prev",
            disabled=st.session_state.page <= 1,
            use_container_width=True,
        ):
            st.session_state.page -= 1
            safe_rerun()
    with c2:
        selected_page = st.number_input(
            "Sayfa",
            key=f"{key_prefix}_page_input",
            min_value=1,
            max_value=total_pages,
            value=st.session_state.page,
            step=1,
        )
        if int(selected_page) != st.session_state.page:
            st.session_state.page = int(selected_page)
            safe_rerun()
    with c3:
        st.markdown(f"<div class='kpi'>Toplam sayfa: <b>{total_pages}</b></div>", unsafe_allow_html=True)
    with c4:
        if st.button(
            "Sonraki ▶",
            key=f"{key_prefix}_next",
            disabled=st.session_state.page >= total_pages,
            use_container_width=True,
        ):
            st.session_state.page += 1
            safe_rerun()


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
            st.info("Önizleme görseli bulunamadı.")

        st.markdown(f"**Etiketler:** {tags}")
        st.markdown(f"**Yükleyen:** {user}")

        k1, k2, k3 = st.columns(3)
        k1.metric("Beğeni", likes)
        k2.metric("Görüntülenme", views)
        k3.metric("İndirme", downloads)
        st.caption(f"Çözünürlük: {width} x {height}")

        file_name = filename_for_item(image_id=image_id, tags=tags)
        prepare_key = f"{key_prefix}_prepared_{image_id}"
        dl1, dl2 = st.columns(2)

        with dl1:
            if image_url:
                if st.button("İndirmeyi hazırla", key=f"{key_prefix}_prepare_btn_{image_id}", use_container_width=True):
                    try:
                        st.session_state[prepare_key] = fetch_image_bytes(image_url)
                    except RuntimeError as exc:
                        st.error(str(exc))

                if prepare_key in st.session_state:
                    st.download_button(
                        "Dosyayı indir",
                        data=st.session_state[prepare_key],
                        file_name=file_name,
                        mime="image/jpeg",
                        key=f"{key_prefix}_download_btn_{image_id}",
                        use_container_width=True,
                    )
            else:
                st.button("İndirmeyi hazırla", disabled=True, use_container_width=True)

        with dl2:
            if st.button("Sunucuya kaydet", key=f"{key_prefix}_save_btn_{image_id}", use_container_width=True):
                if not image_url:
                    st.error("Bu görsel için indirilebilir URL yok.")
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
        initial_sidebar_state="expanded",
    )

    init_state()
    inject_custom_css()
    render_hero()
    render_sidebar()

    if not st.session_state.search_active:
        st.info("Arama başlatmak için sol panelden bir kelime girip 'Ara' butonuna basın.")
        return

    with st.spinner("Pixabay'dan sonuçlar getiriliyor..."):
        try:
            data = search_pixabay(
                query=st.session_state.search_query,
                category=st.session_state.category,
                color=st.session_state.color,
                safesearch=st.session_state.safesearch,
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
        return

    render_summary(total_hits=total_hits, hits=hits)
    st.markdown("### Sonuçlar")
    render_pagination(total_hits=total_hits, key_prefix="top")
    render_results_grid(hits=hits)
    render_pagination(total_hits=total_hits, key_prefix="bottom")


if __name__ == "__main__":
    main()

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
ORIENTATIONS = ["all", "horizontal", "vertical"]
PER_PAGE_OPTIONS = [20, 30, 50]
LANG_OPTIONS = ["tr", "en"]

SHOWCASE_IMAGES = [
    {"title": "Nature", "url": "https://picsum.photos/id/1018/900/560"},
    {"title": "Travel", "url": "https://picsum.photos/id/1015/900/560"},
    {"title": "City", "url": "https://picsum.photos/id/1043/900/560"},
    {"title": "People", "url": "https://picsum.photos/id/1005/900/560"},
    {"title": "Animals", "url": "https://picsum.photos/id/1024/900/560"},
    {"title": "Technology", "url": "https://picsum.photos/id/180/900/560"},
    {"title": "Food", "url": "https://picsum.photos/id/292/900/560"},
    {"title": "Sports", "url": "https://picsum.photos/id/1059/900/560"},
]

I18N: Dict[str, Dict[str, str]] = {
    "tr": {
        "hero_title": "Pixabay Görsel Arama",
        "hero_subtitle": "Google tarzı hızlı arama + Pixabay filtreleri + tek tık indirme.",
        "language": "Dil",
        "theme": "Tema",
        "theme_dark": "🌙 Koyu Tema",
        "theme_light": "☀️ Açık Tema",
        "search_header": "Arama",
        "search_input": "Görsel arama",
        "search_placeholder": "Pixabay'da görsel ara (ör: istanbul, kedi, pubg)",
        "search_btn": "Ara",
        "filters": "Filtreler",
        "image_type": "Görsel Türü",
        "category": "Kategori",
        "orientation": "Yatay/Dikey",
        "per_page": "Sonuç Sayısı",
        "color": "Renk",
        "columns": "Grid Kolon",
        "adult": "Adult içerikleri göster",
        "apply": "Filtreyi Uygula",
        "reset": "Sıfırla",
        "refresh": "Yenile",
        "showcase_title": "Örnek Görseller",
        "showcase_caption": "Arama yapmadan önce örnek kartları görüntüleyebilirsin.",
        "total_results": "Toplam Sonuç",
        "page_likes": "Bu Sayfada Beğeni",
        "page_views": "Bu Sayfada Görüntülenme",
        "page_downloads": "Bu Sayfada İndirme",
        "prev": "◀ Önceki",
        "next": "Sonraki ▶",
        "page": "Sayfa",
        "total_pages": "Toplam sayfa",
        "preview_missing": "Önizleme görseli yok.",
        "tags": "Etiketler",
        "user": "Kullanıcı",
        "likes": "Beğeni",
        "views": "Görüntülenme",
        "downloads": "İndirme",
        "resolution": "Çözünürlük",
        "fullscreen_open": "Tam Ekran Aç",
        "save_device": "Cihaza Kaydet",
        "search_empty": "Lütfen arama kelimesi girin.",
        "loading": "Pixabay sonuçları getiriliyor...",
        "no_results": "Sonuç bulunamadı. Farklı kelime veya filtre deneyin.",
        "results_title": "Sonuçlar",
        "saved_prefix": "Kaydedildi",
        "back_top": "⬆ Üste Dön",
    },
    "en": {
        "hero_title": "Pixabay Visual Search",
        "hero_subtitle": "Google-style quick search + Pixabay filters + one-click download.",
        "language": "Language",
        "theme": "Theme",
        "theme_dark": "🌙 Dark Theme",
        "theme_light": "☀️ Light Theme",
        "search_header": "Search",
        "search_input": "Image search",
        "search_placeholder": "Search on Pixabay (e.g. istanbul, cat, pubg)",
        "search_btn": "Search",
        "filters": "Filters",
        "image_type": "Image Type",
        "category": "Category",
        "orientation": "Orientation",
        "per_page": "Results Per Page",
        "color": "Color",
        "columns": "Grid Columns",
        "adult": "Show adult content",
        "apply": "Apply Filters",
        "reset": "Reset",
        "refresh": "Refresh",
        "showcase_title": "Sample Images",
        "showcase_caption": "Preview sample cards before searching.",
        "total_results": "Total Results",
        "page_likes": "Likes on This Page",
        "page_views": "Views on This Page",
        "page_downloads": "Downloads on This Page",
        "prev": "◀ Previous",
        "next": "Next ▶",
        "page": "Page",
        "total_pages": "Total pages",
        "preview_missing": "No preview image.",
        "tags": "Tags",
        "user": "User",
        "likes": "Likes",
        "views": "Views",
        "downloads": "Downloads",
        "resolution": "Resolution",
        "fullscreen_open": "Open Fullscreen",
        "save_device": "Save to Device",
        "search_empty": "Please enter a search term.",
        "loading": "Fetching results from Pixabay...",
        "no_results": "No results found. Try another keyword or filter.",
        "results_title": "Results",
        "saved_prefix": "Saved",
        "back_top": "⬆ Back to Top",
    },
}

OPTION_LABELS_TR: Dict[str, str] = {
    "all": "Hepsi",
    "photo": "Fotoğraf",
    "illustration": "İllüstrasyon",
    "vector": "Vektör",
    "horizontal": "Yatay",
    "vertical": "Dikey",
    "backgrounds": "Arkaplanlar",
    "fashion": "Moda",
    "nature": "Doğa",
    "science": "Bilim",
    "education": "Eğitim",
    "feelings": "Duygular",
    "health": "Sağlık",
    "people": "İnsanlar",
    "religion": "Din",
    "places": "Mekanlar",
    "animals": "Hayvanlar",
    "industry": "Endüstri",
    "computer": "Bilgisayar",
    "food": "Yemek",
    "sports": "Spor",
    "transportation": "Ulaşım",
    "travel": "Seyahat",
    "buildings": "Binalar",
    "business": "İş",
    "music": "Müzik",
    "grayscale": "Gri Tonlama",
    "transparent": "Şeffaf",
    "red": "Kırmızı",
    "orange": "Turuncu",
    "yellow": "Sarı",
    "green": "Yeşil",
    "turquoise": "Turkuaz",
    "blue": "Mavi",
    "lilac": "Lila",
    "pink": "Pembe",
    "white": "Beyaz",
    "gray": "Gri",
    "black": "Siyah",
    "brown": "Kahverengi",
}

OPTION_LABELS_EN: Dict[str, str] = {
    "all": "All",
    "photo": "Photo",
    "illustration": "Illustration",
    "vector": "Vector",
    "horizontal": "Horizontal",
    "vertical": "Vertical",
    "grayscale": "Grayscale",
}


def current_lang() -> str:
    return st.session_state.get("search_lang", "tr")


def t(key: str) -> str:
    lang = current_lang()
    return I18N.get(lang, I18N["tr"]).get(key, key)


def option_label(value: str) -> str:
    lang = current_lang()
    if lang == "tr":
        return OPTION_LABELS_TR.get(value, value.replace("_", " ").title())
    return OPTION_LABELS_EN.get(value, value.replace("_", " ").title())


def inject_custom_css(theme_mode: str) -> None:
    is_dark = theme_mode == "dark"
    bg_primary = "#0b1220" if is_dark else "#f3f6fb"
    text_primary = "#e8eefc" if is_dark else "#15253f"
    text_muted = "#c5d3ea" if is_dark else "#5a6881"
    card_bg = "#111c33" if is_dark else "#ffffff"
    card_border = "#23304e" if is_dark else "#7f8ca1"
    input_bg = "#0b1a33" if is_dark else "#102f5d"
    card_stat_bg = "#0d172b" if is_dark else "#f6f9ff"
    btn_bg = "#1b315a" if is_dark else "#132f57"
    btn_border = "#2a4b88" if is_dark else "#1c4c90"
    btn_text = "#f4f8ff"

    css = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');

        * { font-family: 'Manrope', sans-serif; }

        .stApp {
          background:
            radial-gradient(1100px 420px at 10% 0%, #d9fff2 0%, rgba(217,255,242,0) 48%),
            radial-gradient(900px 360px at 100% 0%, rgba(221,235,255,0.35) 0%, rgba(221,235,255,0) 46%),
            __BG_PRIMARY__;
          color: __TEXT_PRIMARY__;
        }

        [data-testid="stSidebar"] { display: none; }
        [data-testid="stHeadingWithActionElements"] button,
        [data-testid="stHeadingWithActionElements"] a {
          display: none !important;
        }
        [data-testid="StyledFullScreenButton"],
        button[title="View fullscreen"],
        button[title="Tam ekran görüntüle"] {
          display: none !important;
        }

        .hero {
          background: linear-gradient(120deg, #0f766e 0%, #155e75 52%, #1d4d8f 100%);
          color: white;
          border-radius: 18px;
          padding: 12px 20px;
          margin-bottom: 10px;
          box-shadow: 0 12px 30px rgba(15, 23, 42, 0.16);
          cursor: pointer;
        }

        .hero h1 {
          margin: 0;
          font-size: 2rem;
          font-weight: 800;
        }

        .hero p {
          margin: 2px 0 0;
          color: #e8f2ff !important;
          font-size: 0.92rem;
        }
        .hero-link {
          text-decoration: none !important;
          display: block;
        }

        .filter-wrap {
          background: #0f2450;
          border: 1px solid #1f3d7a;
          border-radius: 14px;
          padding: 12px;
          margin-top: 8px;
          margin-bottom: 8px;
          box-shadow: 0 8px 20px rgba(8, 18, 38, 0.28);
        }

        .section-title {
          margin: 6px 0 10px;
          font-weight: 800;
          color: __TEXT_PRIMARY__;
          font-size: 0.95rem;
          letter-spacing: 0.2px;
        }
        .top-control-label {
          color: __TEXT_PRIMARY__;
          font-size: 0.86rem;
          font-weight: 700;
          margin-bottom: 4px;
          line-height: 1.1;
        }
        .scroll-top-link {
          display: inline-block;
          margin-top: 12px;
          padding: 8px 14px;
          border-radius: 10px;
          border: 1px solid __CARD_BORDER__;
          color: __TEXT_PRIMARY__ !important;
          background: __CARD_BG__;
          text-decoration: none;
          font-weight: 700;
        }

        [data-testid="stCaptionContainer"] p,
        .stCaption,
        .stMarkdown p,
        .stMarkdown label,
        [data-testid="stMetricLabel"] p,
        [data-testid="stMetricValue"] {
          color: __TEXT_PRIMARY__ !important;
        }

        [data-testid="stTextInput"] input,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        [data-testid="stNumberInput"] input {
          background: __INPUT_BG__ !important;
          color: #f6f9ff !important;
          border: 1px solid #1f4f8f !important;
          border-radius: 10px !important;
          min-height: 2.85rem !important;
        }
        [data-testid="stNumberInput"] button {
          display: none !important;
        }
        [data-testid="stNumberInput"] input {
          text-align: center !important;
          font-weight: 700 !important;
        }
        .page-center {
          text-align: center;
          color: __TEXT_PRIMARY__;
          font-weight: 700;
        }

        [data-testid="stExpander"] [data-baseweb="select"] span,
        [data-testid="stExpander"] [data-baseweb="select"] div,
        [data-testid="stExpander"] label {
          color: #e6eeff !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
          background: __CARD_BG__;
          border-color: __CARD_BORDER__ !important;
          border-width: 1.5px !important;
        }

        .card-label {
          color: __TEXT_PRIMARY__;
          font-size: 1rem;
          font-weight: 700;
          margin-top: 8px;
        }
        .card-value {
          color: __TEXT_MUTED__;
          font-size: 0.98rem;
          margin-bottom: 4px;
        }
        .card-stats {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 8px;
          margin-top: 10px;
          margin-bottom: 8px;
        }
        .card-stat-box {
          border: 1px solid __CARD_BORDER__;
          border-radius: 10px;
          padding: 8px;
          background: __CARD_STAT_BG__;
        }
        .card-stat-title {
          color: __TEXT_MUTED__;
          font-size: 0.8rem;
        }
        .card-stat-value {
          color: __TEXT_PRIMARY__;
          font-size: 1.2rem;
          font-weight: 800;
        }

        .stButton > button,
        .stDownloadButton > button,
        .stLinkButton > a {
          border-radius: 10px;
          min-height: 2.85rem;
          font-weight: 700;
          background: __BTN_BG__ !important;
          border: 1px solid __BTN_BORDER__ !important;
          color: __BTN_TEXT__ !important;
          width: 100% !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stLinkButton > a:hover {
          filter: brightness(1.08);
        }

        button[kind="primary"] {
          background: #ff4d5a !important;
          border: 1px solid #ff4d5a !important;
          color: #ffffff !important;
        }
        button[kind="primary"]:hover {
          background: #e63f4c !important;
          border: 1px solid #e63f4c !important;
        }

        div[data-testid="stExpander"] {
          background: #0f2450;
          border: 1px solid #1f3d7a;
          border-radius: 12px;
        }
        div[data-testid="stExpander"] details {
          background: #0f2450;
          border-radius: 12px;
        }
        div[data-testid="stExpander"] summary p {
          color: #dce7ff;
          font-weight: 700;
        }
        div[data-testid="stExpander"] label,
        div[data-testid="stExpander"] p {
          color: #dce7ff;
        }
        </style>
    """

    css = (
        css.replace("__BG_PRIMARY__", bg_primary)
        .replace("__TEXT_PRIMARY__", text_primary)
        .replace("__TEXT_MUTED__", text_muted)
        .replace("__CARD_BG__", card_bg)
        .replace("__CARD_BORDER__", card_border)
        .replace("__INPUT_BG__", input_bg)
        .replace("__CARD_STAT_BG__", card_stat_bg)
        .replace("__BTN_BG__", btn_bg)
        .replace("__BTN_BORDER__", btn_border)
        .replace("__BTN_TEXT__", btn_text)
    )

    st.markdown(css, unsafe_allow_html=True)


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


def init_state() -> None:
    defaults = {
        "search_active": False,
        "search_query": "",
        "search_query_input": "",
        "search_lang": "tr",
        "search_lang_select": "tr",
        "theme_mode": "dark",
        "image_type": "photo",
        "category": "all",
        "orientation": "all",
        "color": "all",
        "per_page": 20,
        "columns": 3,
        "show_adult": False,
        "page": 1,
        "_clear_search_input": False,
        "_request_reset": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_filters() -> None:
    st.session_state.image_type = "photo"
    st.session_state.category = "all"
    st.session_state.orientation = "all"
    st.session_state.color = "all"
    st.session_state.per_page = 20
    st.session_state.columns = 3
    st.session_state.show_adult = False


def reset_all() -> None:
    st.session_state.search_query = ""
    st.session_state.page = 1
    st.session_state.search_active = False
    st.session_state._clear_search_input = True
    reset_filters()


def toggle_theme() -> None:
    st.session_state.theme_mode = "dark" if st.session_state.theme_mode == "light" else "light"


def slugify_tags(tags: str) -> str:
    raw = tags.split(",")[0].strip().lower() if tags else "image"
    slug = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return slug or "image"


def filename_for_item(image_id: int, tags: str) -> str:
    return f"pixabay_{image_id}_{slugify_tags(tags)}.jpg"


def get_download_dir() -> Path:
    for candidate in [Path("downloads"), Path("/tmp/downloads")]:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except OSError:
            continue
    raise RuntimeError("İndirme klasörü oluşturulamadı. Yazma izinlerini kontrol edin.")


def build_params(
    query: str,
    lang: str,
    image_type: str,
    category: str,
    orientation: str,
    color: str,
    safesearch: bool,
    page: int,
    per_page: int,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "key": get_pixabay_api_key(),
        "q": query,
        "lang": lang,
        "image_type": image_type,
        "safesearch": str(safesearch).lower(),
        "page": page,
        "per_page": per_page,
    }

    if category != "all":
        params["category"] = category
    if orientation != "all":
        params["orientation"] = orientation
    if color != "all":
        params["colors"] = color

    return params


@st.cache_data(show_spinner=False, ttl=300)
def search_pixabay(
    query: str,
    lang: str,
    image_type: str,
    category: str,
    orientation: str,
    color: str,
    safesearch: bool,
    page: int,
    per_page: int,
) -> Dict[str, Any]:
    params = build_params(
        query=query,
        lang=lang,
        image_type=image_type,
        category=category,
        orientation=orientation,
        color=color,
        safesearch=safesearch,
        page=page,
        per_page=per_page,
    )

    try:
        response = requests.get(API_URL, params=params, timeout=18)
    except requests.RequestException as exc:
        raise RuntimeError(f"API bağlantı hatası: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError("API yanıtı JSON formatında değil.") from exc

    if response.status_code != 200:
        api_error = payload.get("error", "") if isinstance(payload, dict) else ""
        if response.status_code == 429:
            raise RuntimeError("Pixabay API limitine ulaşıldı (HTTP 429). Birkaç dakika sonra tekrar deneyin.")
        if response.status_code == 400 and api_error:
            raise RuntimeError(f"Pixabay API hatası (HTTP 400): {api_error}")
        raise RuntimeError(f"Pixabay API HTTP hatası: {response.status_code}")

    if "hits" not in payload:
        raise RuntimeError("API yanıtında 'hits' alanı bulunamadı.")

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


def render_hero() -> None:
    st.markdown(
        f"""
        <a class="hero-link" href="#top">
          <div class="hero">
              <h1>{t("hero_title")}</h1>
              <p>{t("hero_subtitle")}</p>
          </div>
        </a>
        """,
        unsafe_allow_html=True,
    )


def render_top_controls() -> None:
    c1, c2, c3 = st.columns([6, 2, 2])
    with c2:
        st.markdown(f"<div class='top-control-label'>{t('language')}</div>", unsafe_allow_html=True)
        selected_lang = st.selectbox(
            "Language",
            options=LANG_OPTIONS,
            key="search_lang_select",
            format_func=lambda x: "Türkçe" if x == "tr" else "English",
            label_visibility="collapsed",
        )
        if selected_lang != st.session_state.search_lang:
            st.session_state.search_lang = selected_lang
            safe_rerun()
    with c3:
        st.markdown(f"<div class='top-control-label'>{t('theme')}</div>", unsafe_allow_html=True)
        label = t("theme_dark") if st.session_state.theme_mode == "light" else t("theme_light")
        if st.button(label, key="theme_toggle_btn", use_container_width=True):
            toggle_theme()
            safe_rerun()


def run_search(reset_page: bool) -> None:
    query = st.session_state.search_query_input.strip()
    if not query:
        st.warning(t("search_empty"))
        st.session_state.search_active = False
        return

    st.session_state.search_query = query
    st.session_state.search_active = True
    if reset_page:
        st.session_state.page = 1


def render_search_section() -> None:
    st.markdown(f"<div class='section-title'>{t('search_header')}</div>", unsafe_allow_html=True)

    if st.session_state._request_reset:
        reset_all()
        st.session_state._request_reset = False

    if st.session_state._clear_search_input:
        st.session_state.search_query_input = ""
        st.session_state._clear_search_input = False

    with st.form("search_form_main", clear_on_submit=False):
        q_col, b_col = st.columns([7, 1.6])
        with q_col:
            st.text_input(
                t("search_input"),
                key="search_query_input",
                placeholder=t("search_placeholder"),
                label_visibility="collapsed",
            )
        with b_col:
            submitted = st.form_submit_button(t("search_btn"), type="primary", use_container_width=True)
        if submitted:
            run_search(reset_page=True)

    st.markdown("<div class='filter-wrap'>", unsafe_allow_html=True)
    with st.expander(t("filters"), expanded=True):
        row1 = st.columns(4)
        with row1[0]:
            st.selectbox(t("image_type"), IMAGE_TYPES, key="image_type", format_func=option_label)
        with row1[1]:
            st.selectbox(
                t("category"),
                CATEGORIES,
                key="category",
                format_func=option_label,
            )
        with row1[2]:
            st.selectbox(
                t("orientation"),
                ORIENTATIONS,
                key="orientation",
                format_func=option_label,
            )
        with row1[3]:
            st.selectbox(t("per_page"), PER_PAGE_OPTIONS, key="per_page")

        row2 = st.columns(3)
        with row2[0]:
            st.selectbox(
                t("color"),
                COLORS,
                key="color",
                format_func=option_label,
            )
        with row2[1]:
            st.slider(t("columns"), min_value=2, max_value=4, step=1, key="columns")
        with row2[2]:
            st.toggle(t("adult"), key="show_adult")

        action_cols = st.columns(3)
        with action_cols[0]:
            if st.button(t("apply"), use_container_width=True):
                run_search(reset_page=True)
        with action_cols[1]:
            if st.button(t("reset"), use_container_width=True):
                st.session_state._request_reset = True
                safe_rerun()
        with action_cols[2]:
            if st.button(t("refresh"), use_container_width=True):
                run_search(reset_page=False)

    st.markdown("</div>", unsafe_allow_html=True)


def render_showcase() -> None:
    st.markdown(f"<div class='section-title'>{t('showcase_title')}</div>", unsafe_allow_html=True)
    st.caption(t("showcase_caption"))

    cols = st.columns(4)
    for i, item in enumerate(SHOWCASE_IMAGES):
        with cols[i % 4]:
            st.image(item["url"], use_container_width=True)
            st.caption(item["title"])


def render_summary(total_hits: int, hits: List[Dict[str, Any]]) -> None:
    likes_total = sum(int(item.get("likes", 0)) for item in hits)
    views_total = sum(int(item.get("views", 0)) for item in hits)
    downloads_total = sum(int(item.get("downloads", 0)) for item in hits)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("total_results"), total_hits)
    c2.metric(t("page_likes"), likes_total)
    c3.metric(t("page_views"), views_total)
    c4.metric(t("page_downloads"), downloads_total)


def render_pagination(total_hits: int, key_prefix: str) -> None:
    total_pages = max(1, min(math.ceil(total_hits / st.session_state.per_page), 500))
    page_key = f"{key_prefix}_page"
    if st.session_state.get(page_key) != st.session_state.page:
        st.session_state[page_key] = st.session_state.page

    p1, p2, p3 = st.columns([1, 1.2, 1])
    with p1:
        if st.button(t("prev"), key=f"{key_prefix}_prev", disabled=st.session_state.page <= 1, use_container_width=True):
            st.session_state.page -= 1
            safe_rerun()
    with p2:
        selected_page = st.number_input(
            t("page"),
            key=page_key,
            min_value=1,
            max_value=total_pages,
            value=st.session_state.page,
            step=1,
            label_visibility="collapsed",
        )
        if int(selected_page) != st.session_state.page:
            st.session_state.page = int(selected_page)
            safe_rerun()
        st.markdown(
            f"<div class='page-center'>{t('page')}: {st.session_state.page} | {t('total_pages')}: {total_pages}</div>",
            unsafe_allow_html=True,
        )
    with p3:
        if st.button(t("next"), key=f"{key_prefix}_next", disabled=st.session_state.page >= total_pages, use_container_width=True):
            st.session_state.page += 1
            safe_rerun()


def render_card(item: Dict[str, Any], key_prefix: str) -> None:
    image_id = int(item.get("id", 0))
    tags = str(item.get("tags", "-"))
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
            st.info(t("preview_missing"))

        st.markdown(f"<div class='card-label'>{t('tags')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card-value'>{tags}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card-label'>{t('user')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card-value'>{user}</div>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="card-stats">
              <div class="card-stat-box"><div class="card-stat-title">{t('likes')}</div><div class="card-stat-value">{likes}</div></div>
              <div class="card-stat-box"><div class="card-stat-title">{t('views')}</div><div class="card-stat-value">{views}</div></div>
              <div class="card-stat-box"><div class="card-stat-title">{t('downloads')}</div><div class="card-stat-value">{downloads}</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(f"{t('resolution')}: {width} x {height}")

        a1, a2 = st.columns(2)
        with a1:
            if image_url:
                if hasattr(st, "link_button"):
                    st.link_button(t("fullscreen_open"), url=image_url, use_container_width=True)
                else:
                    st.markdown(f"[{t('fullscreen_open')}]({image_url})")
            else:
                st.button(t("fullscreen_open"), disabled=True, use_container_width=True)

        with a2:
            if image_url:
                try:
                    image_bytes = fetch_image_bytes(image_url)
                    st.download_button(
                        t("save_device"),
                        data=image_bytes,
                        file_name=filename_for_item(image_id=image_id, tags=tags),
                        mime="image/jpeg",
                        key=f"{key_prefix}_download_{image_id}",
                        use_container_width=True,
                    )
                except RuntimeError as exc:
                    st.button(t("save_device"), disabled=True, use_container_width=True)
                    st.caption(str(exc))
            else:
                st.button(t("save_device"), disabled=True, use_container_width=True)


def render_results(hits: List[Dict[str, Any]]) -> None:
    cols = st.columns(st.session_state.columns)
    for i, item in enumerate(hits):
        with cols[i % st.session_state.columns]:
            render_card(item, key_prefix=f"card_{i}")


def main() -> None:
    st.set_page_config(
        page_title="Pixabay Visual Search",
        page_icon="🖼️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    init_state()
    inject_custom_css(st.session_state.theme_mode)

    st.markdown("<a id='top'></a>", unsafe_allow_html=True)
    render_top_controls()
    render_hero()
    render_search_section()

    if not st.session_state.search_active:
        render_showcase()
        return

    with st.spinner(t("loading")):
        try:
            data = search_pixabay(
                query=st.session_state.search_query,
                lang=st.session_state.search_lang,
                image_type=st.session_state.image_type,
                category=st.session_state.category,
                orientation=st.session_state.orientation,
                color=st.session_state.color,
                safesearch=not st.session_state.show_adult,
                page=st.session_state.page,
                per_page=st.session_state.per_page,
            )
        except RuntimeError as exc:
            st.error(str(exc))
            render_showcase()
            return

    hits: List[Dict[str, Any]] = data.get("hits", [])
    total_hits = int(data.get("totalHits", 0))

    if total_hits == 0 or not hits:
        st.warning(t("no_results"))
        render_showcase()
        return

    render_results(hits)
    st.markdown("---")
    st.markdown(f"<div class='section-title'>{t('results_title')}</div>", unsafe_allow_html=True)
    render_summary(total_hits=total_hits, hits=hits)
    render_pagination(total_hits, key_prefix="bottom")


if __name__ == "__main__":
    main()

from __future__ import annotations

import re
import os
from pathlib import Path
from typing import Any, Dict

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
PER_PAGE_OPTIONS = [20, 30, 50]


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


def safe_rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def get_download_dir() -> Path:
    candidates = [Path("downloads"), Path("/tmp/downloads")]
    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except OSError:
            continue

    raise RuntimeError("İndirme klasörü oluşturulamadı. Yazma izni olan bir klasör bulunamadı.")


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
    """Pixabay API'den görsel sonuçlarını döndürür."""
    api_key = get_pixabay_api_key()
    params: Dict[str, Any] = {
        "key": api_key,
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

    try:
        response = requests.get(API_URL, params=params, timeout=15)
    except requests.RequestException as exc:
        raise RuntimeError(f"API bağlantı hatası: {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(f"Pixabay API hata kodu: HTTP {response.status_code}")

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError("API yanıtı JSON formatında değil.") from exc

    if "hits" not in payload:
        raise RuntimeError("API yanıtında 'hits' alanı bulunamadı.")

    return payload


def slugify_tags(tags: str) -> str:
    raw = tags.split(",")[0].strip().lower() if tags else "image"
    slug = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return slug or "image"


def save_image_locally(image_url: str, image_id: int, tags: str) -> Path:
    try:
        response = requests.get(image_url, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Görsel indirilemedi: {exc}") from exc

    download_dir = get_download_dir()

    slug = slugify_tags(tags)
    base = download_dir / f"pixabay_{image_id}_{slug}.jpg"
    file_path = base
    counter = 1
    while file_path.exists():
        file_path = download_dir / f"pixabay_{image_id}_{slug}_{counter}.jpg"
        counter += 1

    file_path.write_bytes(response.content)
    return file_path


def init_state() -> None:
    st.session_state.setdefault("search_active", False)
    st.session_state.setdefault("search_query", "")
    st.session_state.setdefault("category", "all")
    st.session_state.setdefault("color", "all")
    st.session_state.setdefault("safesearch", True)
    st.session_state.setdefault("per_page", 20)
    st.session_state.setdefault("page", 1)


def reset_state() -> None:
    st.session_state.search_active = False
    st.session_state.search_query = ""
    st.session_state.category = "all"
    st.session_state.color = "all"
    st.session_state.safesearch = True
    st.session_state.per_page = 20
    st.session_state.page = 1


def render_search_form() -> None:
    with st.form("search_form"):
        query = st.text_input("Görsel arama", value=st.session_state.search_query, placeholder="cat, istanbul, pubg...")
        col1, col2, col3 = st.columns(3)

        with col1:
            category = st.selectbox(
                "Kategori",
                options=CATEGORIES,
                format_func=lambda x: "Hepsi" if x == "all" else x,
                index=CATEGORIES.index(st.session_state.category),
            )
        with col2:
            color = st.selectbox(
                "Renk",
                options=COLORS,
                format_func=lambda x: "Hepsi" if x == "all" else x,
                index=COLORS.index(st.session_state.color),
            )
        with col3:
            per_page = st.selectbox("Sayfa başına sonuç", options=PER_PAGE_OPTIONS, index=PER_PAGE_OPTIONS.index(st.session_state.per_page))

        safesearch = st.checkbox("Adult içerikleri göster", value=not st.session_state.safesearch)

        submit_col, reset_col = st.columns([1, 1])
        with submit_col:
            submitted = st.form_submit_button("Ara")
        with reset_col:
            reset_clicked = st.form_submit_button("Arama parametrelerini sıfırla")

    if reset_clicked:
        reset_state()
        safe_rerun()

    if submitted:
        cleaned = query.strip()
        if not cleaned:
            st.warning("Lütfen arama kelimesi girin.")
            st.session_state.search_active = False
            return

        st.session_state.search_query = cleaned
        st.session_state.category = category
        st.session_state.color = color
        st.session_state.safesearch = not safesearch
        st.session_state.per_page = per_page
        st.session_state.page = 1
        st.session_state.search_active = True


def render_pagination(total_hits: int) -> None:
    total_pages = max(1, min((total_hits + st.session_state.per_page - 1) // st.session_state.per_page, 500))

    pager_col1, pager_col2, pager_col3 = st.columns([1, 2, 1])
    with pager_col1:
        if st.button("Önceki", disabled=st.session_state.page <= 1):
            st.session_state.page -= 1
            safe_rerun()
    with pager_col2:
        selected_page = st.number_input(
            "Sayfa",
            min_value=1,
            max_value=total_pages,
            value=st.session_state.page,
            step=1,
        )
        if selected_page != st.session_state.page:
            st.session_state.page = int(selected_page)
            safe_rerun()
    with pager_col3:
        if st.button("Sonraki", disabled=st.session_state.page >= total_pages):
            st.session_state.page += 1
            safe_rerun()

    st.caption(f"Toplam sonuç: {total_hits} | Toplam sayfa: {total_pages}")


def render_results(hits: list[Dict[str, Any]]) -> None:
    cols = st.columns(3)
    for idx, item in enumerate(hits):
        col = cols[idx % 3]
        with col:
            preview_url = item.get("previewURL") or item.get("webformatURL") or item.get("largeImageURL")
            if preview_url:
                st.image(preview_url, use_container_width=True)
            else:
                st.info("Önizleme görseli yok.")
            st.write(f"**Etiketler:** {item.get('tags', '-')}")
            st.write(f"**Kullanıcı:** {item.get('user', '-')}")
            st.write(f"**Beğeni:** {item.get('likes', 0)} | **Görüntülenme:** {item.get('views', 0)}")
            width = item.get("imageWidth", "?")
            height = item.get("imageHeight", "?")
            st.write(f"**Çözünürlük:** {width} x {height}")

            image_url = item.get("largeImageURL") or item.get("webformatURL")
            if st.button("İndir (downloads/)", key=f"download_{item.get('id', idx)}"):
                if not image_url:
                    st.error("Bu görsel için indirilebilir URL bulunamadı.")
                else:
                    try:
                        saved_path = save_image_locally(
                            image_url=image_url,
                            image_id=item.get("id", idx),
                            tags=item.get("tags", "image"),
                        )
                        st.success(f"Kaydedildi: {saved_path}")
                    except RuntimeError as exc:
                        st.error(str(exc))

            st.markdown("---")


def main() -> None:
    st.set_page_config(page_title="Pixabay Görsel Arama", page_icon="🖼️", layout="wide")
    st.title("Pixabay API ile Görsel Arama & İndirme")

    init_state()
    render_search_form()

    if not st.session_state.search_active:
        st.info("Arama yapmak için kelime girip 'Ara' butonuna basın.")
        return

    try:
        data = search_pixabay(
            query=st.session_state.search_query,
            category=st.session_state.category,
            color=st.session_state.color,
            safesearch=st.session_state.safesearch,
            page=st.session_state.page,
            per_page=st.session_state.per_page,
        )
    except RuntimeError as exc:
        st.error(str(exc))
        return

    hits = data.get("hits", [])
    total_hits = int(data.get("totalHits", 0))

    if total_hits == 0 or not hits:
        st.warning("Sonuç bulunamadı.")
        return

    render_pagination(total_hits)
    render_results(hits)


if __name__ == "__main__":
    main()

import streamlit as st
import requests
import random

# -------------------
# CONFIG
# -------------------
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p"

# Movie mood → genres (movie genre IDs)
MOODS_MOVIE = {
    "Anything": {},
    "Cozy": {"with_genres": "18,10749", "without_genres": "27,53"},
    "Feel-Good": {"with_genres": "35,10749", "without_genres": "27,53"},
    "Adrenaline": {"with_genres": "28,53"},
    "Spooky": {"with_genres": "27,53"},
    "Brainy": {"with_genres": "99,36,18"},
    "Silly": {"with_genres": "35"},
    "Rom-Com": {"with_genres": "10749,35", "without_genres": "27,53"},
    "Family Night": {"with_genres": "10751"},
    "Short & Sweet (≤100 min)": {"with_runtime.lte": "100"},  # Movies only
}

# TV mood → genres (TV genre IDs)
MOODS_TV = {
    "Anything": {},
    "Cozy": {"with_genres": "35,18"},
    "Feel-Good": {"with_genres": "35"},
    "Adrenaline": {"with_genres": "10759,9648"},
    "Spooky": {"with_genres": "9648,10765"},   # TV has no 'Horror' id
    "Brainy": {"with_genres": "99,18"},
    "Silly": {"with_genres": "35"},
    "Rom-Com": {"with_genres": "35,18"},       # approx for TV
    "Family Night": {"with_genres": "10762,16"},
    "Short & Sweet (≤100 min)": {},            # ignore for TV
}

INDUSTRIES = {
    "Any": {},
    "Hollywood": {"with_origin_country": "US"},
    "Bollywood": {"with_origin_country": "IN"},
    "Nollywood": {"with_origin_country": "NG"},
    "Korean": {"with_origin_country": "KR"},
    "Japanese": {"with_origin_country": "JP"},
    "French": {"with_origin_country": "FR"},
}

# -------------------
# HELPERS
# -------------------
def poster_url(path, size="w500"):
    return f"{IMAGE_BASE}/{size}{path}" if path else None

def discover_titles(kind: str, mood: str, industry: str):
    # pick endpoint + mood map (✅ this was the bug)
    if kind == "movie":
        endpoint = f"{BASE_URL}/discover/movie"
        filters = dict(MOODS_MOVIE.get(mood, {}))
    else:
        endpoint = f"{BASE_URL}/discover/tv"
        filters = dict(MOODS_TV.get(mood, {}))

    # merge industry filters (⚠️ do not change)
    filters.update(INDUSTRIES.get(industry, {}))

    # Special case: Nollywood + Rom-Com → widen with OR genres
    if industry == "Nollywood" and mood == "Rom-Com":
        filters["with_genres"] = "10749|35" if kind == "movie" else "35|18"

    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "page": random.randint(1, 5),
        **filters,
    }

    # TV shouldn’t get movie runtime filter
    if kind == "tv":
        params.pop("with_runtime.lte", None)

    r = requests.get(endpoint, params=params, timeout=12)
    r.raise_for_status()
    return r.json().get("results", [])

def pick_one(items):
    return random.choice(items) if items else None

def title_year_vote_overview(item, kind):
    if kind == "movie":
        title = item.get("title") or item.get("name") or "Unknown Title"
        year = (item.get("release_date") or "")[:4]
    else:
        title = item.get("name") or item.get("title") or "Unknown Title"
        year = (item.get("first_air_date") or "")[:4]
    vote = item.get("vote_average", None)
    overview = item.get("overview") or "No description available."
    return title, year, vote, overview

# -------------------
# UI (tidy, without touching industry behavior)
# -------------------
st.set_page_config(page_title="Random Movie Night Picker", page_icon="🎬", layout="centered")
st.title("🎬 Random Movie Night Picker 🍿")
st.caption("Pick your vibe + industry, then hit Surprise Me!")

# top row: type + (dynamic) vibe and industry in two neat columns
type_choice = st.radio("Type", ["Movies", "TV Shows"], horizontal=True)
kind_api = "movie" if type_choice == "Movies" else "tv"

# ✅ use the RIGHT mood map for the chosen type, and separate widget state per type
active_moods = MOODS_MOVIE if kind_api == "movie" else MOODS_TV
c1, c2 = st.columns(2)
with c1:
    mood = st.selectbox("Pick your vibe:", list(active_moods.keys()), key=f"mood_{kind_api}")
with c2:
    # leaving industry control exactly as-is in behavior; just placing in column
    industry = st.radio("Pick industry:", list(INDUSTRIES.keys()), horizontal=False, key="industry_radio")

st.write("")
go = st.button("🎲 Surprise Me!", use_container_width=True)

if go:
    try:
        results = discover_titles(kind_api, mood, industry)
    except requests.HTTPError as e:
        st.error(f"TMDB error: {e}")
        results = []

    pick = pick_one(results)
    if not pick:
        st.warning("No titles found for that combo. Try a different vibe or industry.")
    else:
        title, year, vote, overview = title_year_vote_overview(pick, kind_api)
        poster = poster_url(pick.get("poster_path"))

        # nice, centered card-ish look without custom CSS
        st.subheader(f"{'🎥' if kind_api=='movie' else '📺'} Tonight’s pick: **{title}**")
        bits = []
        if year: bits.append(year)
        if vote is not None: bits.append(f"⭐ {vote:.1f}")
        if bits: st.caption(" · ".join(bits))
        if poster: st.image(poster, width=320)
        st.write(overview)

        st.divider()
        st.subheader("Other ideas")
        others = [i for i in results if i.get("id") != pick.get("id")]
        for alt in random.sample(others, k=min(4, len(others))):
            a_title, a_year, a_vote, _ = title_year_vote_overview(alt, kind_api)
            icon = "🎥" if kind_api == "movie" else "📺"
            st.write(f"{icon} **{a_title}** — {a_year} · ⭐ {a_vote if a_vote is not None else 'N/A'}")

st.caption("This product uses the TMDB API but is not endorsed or certified by TMDB.")

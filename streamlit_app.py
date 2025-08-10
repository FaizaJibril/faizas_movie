import streamlit as st
import requests
import random

# -------------------
# CONFIG
# -------------------
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"

# Movie mood → genres (movie genre IDs)
MOODS_MOVIE = {
    "Anything": {},
    "Cozy": {"with_genres": "18,10749", "without_genres": "27,53"},          # Drama+Romance, no Horror/Thriller
    "Feel-Good": {"with_genres": "35,10749", "without_genres": "27,53"},      # Comedy+Romance
    "Adrenaline": {"with_genres": "28,53"},                                   # Action+Thriller
    "Spooky": {"with_genres": "27,53"},                                       # Horror+Thriller
    "Brainy": {"with_genres": "99,36,18"},                                    # Docu+History+Drama
    "Silly": {"with_genres": "35"},                                           # Comedy
    "Rom-Com": {"with_genres": "10749,35", "without_genres": "27,53"},        # Romance+Comedy
    "Family Night": {"with_genres": "10751"},                                 # Family
    "Short & Sweet (≤100 min)": {"with_runtime.lte": "100"},                  # Movies only
}

# TV mood → genres (tv genre IDs are different!)
# TV genre IDs (common): 16 Animation, 35 Comedy, 80 Crime, 99 Documentary, 18 Drama,
# 9648 Mystery, 10759 Action & Adventure, 10762 Kids, 10763 News, 10764 Reality,
# 10765 Sci-Fi & Fantasy, 10766 Soap, 10767 Talk, 10768 War & Politics, 37 Western
MOODS_TV = {
    "Anything": {},
    "Cozy": {"with_genres": "35,18"},                          # Comedy + Drama
    "Feel-Good": {"with_genres": "35"},                        # Comedy
    "Adrenaline": {"with_genres": "10759,9648"},               # Action & Adventure + Mystery
    "Spooky": {"with_genres": "9648,10765"},                   # Mystery + Sci-Fi & Fantasy (TV has no 'Horror' id)
    "Brainy": {"with_genres": "99,18"},                        # Documentary + Drama
    "Silly": {"with_genres": "35"},                            # Comedy
    "Rom-Com": {"with_genres": "35,18"},                       # Approx: Comedy + Drama (TV lacks Romance id)
    "Family Night": {"with_genres": "10762,16"},               # Kids + Animation
    "Short & Sweet (≤100 min)": {},                            # Not applicable to TV; ignore runtime
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

IMAGE_BASE = "https://image.tmdb.org/t/p"

# -------------------
# HELPERS
# -------------------
def discover_titles(kind: str, mood: str, industry: str):
    """
    kind: 'movie' or 'tv'
    mood: key from MOODS_MOVIE/MOODS_TV
    industry: key from INDUSTRIES
    """
    # choose endpoint + mood map
    if kind == "movie":
        endpoint = f"{BASE_URL}/discover/movie"
        mood_filters = dict(MOODS_MOVIE.get(mood, {}))
    else:
        endpoint = f"{BASE_URL}/discover/tv"
        mood_filters = dict(MOODS_TV.get(mood, {}))

    # industry filters
    filters = {}
    filters.update(mood_filters)
    filters.update(INDUSTRIES.get(industry, {}))

    # Special case: Nollywood + Rom-Com → use OR genres to widen set
    # - Movies: Romance OR Comedy
    # - TV: Comedy OR Drama (approx for rom-com vibe)
    if industry == "Nollywood" and mood == "Rom-Com":
        if kind == "movie":
            filters["with_genres"] = "10749|35"
        else:
            filters["with_genres"] = "35|18"

    params = {
        "api_key": TMDB_API_KEY,
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "language": "en-US",
        **filters
    }
    # Randomize page for variety
    params["page"] = random.randint(1, 5)

    # runtime applies to movies only; ensure we don't send it for TV
    if kind == "tv" and "with_runtime.lte" in params:
        params.pop("with_runtime.lte", None)

    resp = requests.get(endpoint, params=params, timeout=12)
    resp.raise_for_status()
    data = resp.json()
    return data.get("results", [])

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

def poster_url(path, size="w500"):
    return f"{IMAGE_BASE}/{size}{path}" if path else None

# -------------------
# UI
# -------------------
st.title("🎬 Random Movie Night Picker 🍿")
st.write("Pick your vibe and I'll fetch you something to watch!")

kind = st.segmented_control("Type", ["Movies", "TV Shows"])
kind_api = "movie" if kind == "Movies" else "tv"

mood = st.radio("Pick your vibe:", list(MOODS_MOVIE.keys()), horizontal=True)
industry = st.radio("Pick industry:", list(INDUSTRIES.keys()), horizontal=True)

if st.button("🎲 Surprise Me!"):
    try:
        results = discover_titles(kind_api, mood, industry)
    except requests.HTTPError as e:
        st.error(f"TMDB error: {e}")
        results = []

    pick = pick_one(results)
    if not pick:
        st.error("No titles found for that combo. Try a different vibe or industry!")
    else:
        title, year, vote, overview = title_year_vote_overview(pick, kind_api)
        poster = poster_url(pick.get("poster_path"))

        if poster:
            st.image(poster, width=300)

        badge = "🎥" if kind_api == "movie" else "📺"
        st.subheader(f"Tonight’s pick: {badge} {title}")
        parts = []
        if year: parts.append(year)
        if vote is not None: parts.append(f"⭐ {vote:.1f}")
        if parts: st.caption(" · ".join(parts))
        st.write(overview)

        # Other ideas
        st.markdown("### Other ideas")
        others = [it for it in results if it.get("id") != pick.get("id")]
        for alt in random.sample(others, k=min(5, len(others))):
            a_title, a_year, a_vote, _ = title_year_vote_overview(alt, kind_api)
            st.write(f"{'🎥' if kind_api=='movie' else '📺'} **{a_title}** — {a_year} · ⭐ {a_vote if a_vote is not None else 'N/A'}")

st.markdown("---")
st.caption("This product uses the TMDB API but is not endorsed or certified by TMDB.")

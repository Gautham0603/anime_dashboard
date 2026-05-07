import streamlit as st
import requests
import pandas as pd

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Anime Dashboard",
    page_icon="🔥",
    layout="wide"
)

st.title("🔥 Dynamic Anime Dashboard")

# ---------------- SIDEBAR ---------------- #

st.sidebar.header("Anime Controls")

page_number = st.sidebar.slider(
    "Select Anime Page",
    min_value=1,
    max_value=200,
    value=1
)

# 200 pages × 50 anime ≈ 10,000 anime
anime_per_page = 50

# ---------------- API ---------------- #

url = "https://graphql.anilist.co"

query = f"""
{{
  Page(page: {page_number}, perPage: {anime_per_page}) {{

    media(type: ANIME, sort: POPULARITY_DESC) {{

      title {{
        romaji
      }}

      averageScore

      episodes

      coverImage {{
        large
      }}
    }}
  }}
}}
"""

# ---------------- REQUEST ---------------- #

try:

    response = requests.post(
        url,
        json={"query": query},
        timeout=15
    )

    data = response.json()

    # Safe extraction
    media = data.get("data", {}).get("Page", {}).get("media", [])

    anime_list = []

    # ---------------- DATA EXTRACTION ---------------- #

    for anime in media:

        score = anime.get("averageScore")

        anime_list.append({

            "Title": anime["title"]["romaji"],

            "Score": round(score / 10, 1) if score else "N/A",

            "Episodes": anime.get("episodes") or "Ongoing",

            "Poster": anime["coverImage"]["large"]
        })

    # ---------------- DATAFRAME ---------------- #

    df = pd.DataFrame(anime_list)

    st.subheader(f"📊 Anime Data — Page {page_number}")

    st.dataframe(
        df[["Title", "Score", "Episodes"]],
        use_container_width=True
    )

    # ---------------- POSTERS ---------------- #

    st.subheader("🔥 Anime Gallery")

    cols = st.columns(5)

    for i, anime in enumerate(anime_list):

        with cols[i % 5]:

            st.image(anime["Poster"])

            st.markdown(f"### {anime['Title']}")

            st.write(f"⭐ Score: {anime['Score']}")

            st.write(f"🎬 Episodes: {anime['Episodes']}")

# ---------------- ERROR HANDLING ---------------- #

except Exception as e:

    st.error("Failed to fetch anime data from AniList API.")

    st.write(e)

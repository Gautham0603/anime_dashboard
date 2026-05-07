import streamlit as st
import requests
import pandas as pd

# Page config
st.set_page_config(
    page_title="Anime Dashboard",
    page_icon="🔥",
    layout="wide"
)

st.title("🔥 Dynamic Anime Dashboard")

# AniList API
url = "https://graphql.anilist.co"

# Query
query = """
{
  Page(page: 1, perPage: 50) {
    media(type: ANIME, sort: POPULARITY_DESC) {
      title {
        romaji
      }
      averageScore
      episodes
      coverImage {
        large
      }
    }
  }
}
"""

# Request
response = requests.post(
    url,
    json={"query": query}
)

# JSON response
data = response.json()

anime_list = []

# Safe API check
if (
    "data" in data and
    data["data"] and
    "Page" in data["data"] and
    "media" in data["data"]["Page"]
):

    for anime in data["data"]["Page"]["media"]:

        score = anime["averageScore"]

        anime_list.append({
            "Title": anime["title"]["romaji"],
            "Score": score / 10 if score else "N/A",
            "Episodes": anime["episodes"] or "Ongoing",
            "Poster": anime["coverImage"]["large"]
        })

    # DataFrame
    df = pd.DataFrame(anime_list)

    # Table
    st.subheader("Anime Data")

    st.dataframe(
        df[["Title", "Score", "Episodes"]],
        use_container_width=True
    )

    # Posters
    st.subheader("🔥 Top Anime")

    cols = st.columns(5)

    for i, anime in enumerate(anime_list):

        with cols[i % 5]:

            st.image(anime["Poster"])

            st.markdown(f"### {anime['Title']}")

            st.write(f"⭐ Score: {anime['Score']}")

            st.write(f"🎬 Episodes: {anime['Episodes']}")

else:

    st.error("Failed to fetch anime data.")
    st.write(data)

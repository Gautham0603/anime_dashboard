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
  Page(page: 30, perPage: 50) {
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

# Convert to JSON
data = response.json()

# Anime list
anime_list = []

# Extract data
for anime in data["data"]["Page"]["media"]:

    anime_list.append({
        "Title": anime["title"]["romaji"],
        "Score": anime["averageScore"]/10,
        "Episodes": anime["episodes"],
        "Poster": anime["coverImage"]["large"]
    })

# DataFrame
df = pd.DataFrame(anime_list)

# Show dataframe
st.subheader("Anime Data")

st.dataframe(
    df[["Title", "Score", "Episodes"]],
    use_container_width=True
)

# Posters section
st.subheader("🔥 Top Anime")

cols = st.columns(5)

for i, anime in enumerate(anime_list):

    with cols[i % 5]:

        st.image(anime["Poster"])

        st.markdown(f"### {anime['Title']}")

        st.write(f"⭐ Score: {anime['Score']/10}")

        st.write(f"🎬 Episodes: {anime['Episodes']}")

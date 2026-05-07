import streamlit as st
import requests
import pandas as pd

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Anime Dashboard",
    page_icon="🔥",
    layout="wide"
)

st.title("🔥 Massive Anime Database")

# ---------------- SETTINGS ---------------- #

TOTAL_PAGES = 200
ANIME_PER_PAGE = 50

url = "https://graphql.anilist.co"

anime_list = []

# ---------------- FETCH MULTIPLE PAGES ---------------- #

with st.spinner("Fetching anime database..."):

    for page in range(1, TOTAL_PAGES + 1):

        query = f"""
        {{
          Page(page: {page}, perPage: {ANIME_PER_PAGE}) {{

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

        try:

            response = requests.post(
                url,
                json={"query": query},
                timeout=10
            )

            data = response.json()

            media = data.get(
                "data", {}
            ).get(
                "Page", {}
            ).get(
                "media", []
            )

            for anime in media:

                score = anime.get("averageScore")

                anime_list.append({

                    "Title": anime["title"]["romaji"],

                    "Score": round(score / 10, 1)
                    if score else "N/A",

                    "Episodes": anime.get("episodes")
                    or "Ongoing",

                    "Poster": anime["coverImage"]["large"]
                })

        except:
            pass

# ---------------- DATAFRAME ---------------- #

df = pd.DataFrame(anime_list)

# Remove duplicates
df = df.drop_duplicates(subset=["Title"])

# Reset index
df.reset_index(drop=True, inplace=True)

# ---------------- TABLE ---------------- #

st.subheader(f"📊 Total Anime Loaded: {len(df)}")

st.dataframe(
    df[["Title", "Score", "Episodes"]],
    use_container_width=True,
    height=700
)

# ---------------- SEARCH ---------------- #

search = st.text_input("🔍 Search Anime")

if search:

    filtered_df = df[
        df["Title"].str.contains(
            search,
            case=False,
            na=False
        )
    ]

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

# ---------------- POSTERS ---------------- #

st.subheader("🔥 Anime Gallery")

cols = st.columns(5)

for i, anime in enumerate(anime_list[:50]):

    with cols[i % 5]:

        st.image(anime["Poster"])

        st.markdown(f"### {anime['Title']}")

        st.write(f"⭐ Score: {anime['Score']}")

        st.write(f"🎬 Episodes: {anime['Episodes']}")

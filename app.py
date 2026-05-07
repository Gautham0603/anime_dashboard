import streamlit as st
import requests
import pandas as pd
import base64

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Anime Dashboard",
    page_icon="🔥",
    layout="wide"
)

# ---------------- BACKGROUND IMAGE ---------------- #

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* Dark transparent overlay */
        .main {{
            background-color: rgba(0, 0, 0, 0.7);
            padding: 20px;
            border-radius: 15px;
        }}

        /* Make dataframe readable */
        section[data-testid="stSidebar"] {{
            background-color: rgba(0,0,0,0.8);
        }}

        div[data-testid="stDataFrame"] {{
            background-color: rgba(255,255,255,0.9);
            border-radius: 10px;
        }}

        h1, h2, h3, h4, h5, h6, p, label, div {{
            color: white;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Add background image
add_bg_from_local("background.jpg")

# ---------------- TITLE ---------------- #

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

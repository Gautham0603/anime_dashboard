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

# ---------------- BACKGROUND ---------------- #

def add_bg_from_local(image_file):

    with open(image_file, "rb") as image:

        encoded = base64.b64encode(
            image.read()
        ).decode()

    st.markdown(
        f"""
        <style>

        .stApp {{
            background-image:
            linear-gradient(
                rgba(0,0,0,0.78),
                rgba(0,0,0,0.78)
            ),
            url("data:image/jpg;base64,{encoded}");

            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        section[data-testid="stSidebar"] {{
            background-color: rgba(0,0,0,0.85);
        }}

        div[data-testid="stDataFrame"] {{
            background-color: rgba(255,255,255,0.08);
            backdrop-filter: blur(10px);
            border-radius: 15px;
        }}

        h1, h2, h3, h4, h5, h6,
        p, label, div {{
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

TOTAL_PAGES = 50
ANIME_PER_PAGE = 50

url = "https://graphql.anilist.co"

# ---------------- CACHE ---------------- #

@st.cache_data(show_spinner=False)

def fetch_anime_data():

    anime_list = []

    for page in range(1, TOTAL_PAGES + 1):

        query = f"""
        {{
          Page(page: {page}, perPage: {ANIME_PER_PAGE}) {{

            media(type: ANIME, sort: ID) {{

              id

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

                if not anime:
                    continue

                title_data = anime.get("title")

                if not title_data:
                    continue

                title = title_data.get("romaji")

                if not title:
                    continue

                score = anime.get("averageScore")

                anime_list.append({

                    "ID": anime.get("id"),

                    "Title": title,

                    "Score": round(score / 10, 1)
                    if score else "N/A",

                    "Episodes": anime.get("episodes")
                    or "Ongoing",

                    "Poster": anime.get(
                        "coverImage", {}
                    ).get(
                        "large"
                    )
                })

        except:
            pass

    return anime_list

# ---------------- FETCH DATA ---------------- #

with st.spinner("Fetching anime database..."):

    anime_list = fetch_anime_data()

# ---------------- DATAFRAME ---------------- #

df = pd.DataFrame(anime_list)

# Remove duplicates
if not df.empty:

    df = df.drop_duplicates(
        subset=["ID"]
    )

    df.reset_index(
        drop=True,
        inplace=True
    )

# ---------------- SIDEBAR ---------------- #

st.sidebar.header("🔍 Anime Search")

search = st.sidebar.text_input(
    "Search Anime"
)

# ---------------- FILTER ---------------- #

filtered_df = df.copy()

if search and not filtered_df.empty:

    filtered_df = filtered_df[
        filtered_df["Title"].str.contains(
            search,
            case=False,
            na=False
        )
    ]

# ---------------- TABLE ---------------- #

if not filtered_df.empty:

    st.subheader(
        f"📊 Total Anime Loaded: {len(filtered_df)}"
    )

    st.dataframe(
        filtered_df[
            ["Title", "Score", "Episodes"]
        ],
        use_container_width=True,
        height=700
    )

else:

    st.warning("No anime data loaded.")

# ---------------- GALLERY ---------------- #

if not filtered_df.empty:

    st.subheader("🔥 Anime Gallery")

    cols = st.columns(5)

    gallery_df = filtered_df.head(50)

    for i, (_, anime) in enumerate(
        gallery_df.iterrows()
    ):

        with cols[i % 5]:

            if anime["Poster"]:

                st.image(
                    anime["Poster"]
                )

            st.markdown(
                f"### {anime['Title']}"
            )

            st.write(
                f"⭐ Score: {anime['Score']}"
            )

            st.write(
                f"🎬 Episodes: {anime['Episodes']}"
            )

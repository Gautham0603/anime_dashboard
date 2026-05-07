import streamlit as st
import requests
import pandas as pd
import base64

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Anime Genre Dashboard",
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

# Add background
add_bg_from_local("background.jpg")

# ---------------- TITLE ---------------- #

st.title("🔥 Anime Genre Dashboard")

# ---------------- SIDEBAR ---------------- #

st.sidebar.header("🎴 Anime Filters")

genres = [
    "Action",
    "Adventure",
    "Comedy",
    "Drama",
    "Fantasy",
    "Horror",
    "Romance",
    "Sci-Fi",
    "Sports",
    "Slice of Life",
    "Mystery",
    "Psychological"
]

selected_genre = st.sidebar.selectbox(
    "Select Genre",
    genres
)

search = st.sidebar.text_input(
    "🔍 Search Anime"
)

min_score = st.sidebar.slider(
    "⭐ Minimum Score",
    0.0,
    10.0,
    7.0
)

# ---------------- API ---------------- #

url = "https://graphql.anilist.co"

query = f"""
{{
  Page(page: 1, perPage: 50) {{

    media(
      type: ANIME,
      genre: "{selected_genre}",
      sort: POPULARITY_DESC
    ) {{

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

# ---------------- FETCH DATA ---------------- #

@st.cache_data(show_spinner=False)

def fetch_anime_data(query):

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

    anime_list = []

    for anime in media:

        if not anime:
            continue

        title = anime["title"]["romaji"]

        score = anime.get("averageScore")

        anime_list.append({

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

    return anime_list

# Load anime
anime_list = fetch_anime_data(query)

# ---------------- DATAFRAME ---------------- #

df = pd.DataFrame(anime_list)

# ---------------- FILTERS ---------------- #

if not df.empty:

    # Search filter
    if search:

        df = df[
            df["Title"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    # Score filter
    df = df[
        pd.to_numeric(
            df["Score"],
            errors="coerce"
        ) >= min_score
    ]

# ---------------- TABLE ---------------- #

st.subheader(
    f"📊 {selected_genre} Anime"
)

if not df.empty:

    st.dataframe(
        df[
            ["Title", "Score", "Episodes"]
        ],
        use_container_width=True,
        height=600
    )

else:

    st.warning(
        "No anime found."
    )

# ---------------- GALLERY ---------------- #

st.subheader("🔥 Anime Gallery")

cols = st.columns(5)

for i, (_, anime) in enumerate(
    df.head(25).iterrows()
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

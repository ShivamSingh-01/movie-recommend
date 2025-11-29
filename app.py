import streamlit as st
import pickle
import pandas as pd
import requests
import gdown  # to download similarity.pkl from Google Drive

# -----------------------------
# TMDB API KEY (direct use, no secrets)
# -----------------------------
TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

# -----------------------------
# Download similarity.pkl from Google Drive
# -----------------------------
file_id = "1t2tIMQ36_p4fRrCelW06nVNkge8WNRj4"   # your Google Drive file ID
url = f"https://drive.google.com/uc?id={file_id}"
output_path = "similarity.pkl"

try:
    open(output_path, "rb")
except FileNotFoundError:
    gdown.download(url, output_path, quiet=False)

# -----------------------------
# Fetch movie poster (TMDB API)
# -----------------------------
def fetch_poster(movie_name):
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": movie_name
        }
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data.get("results"):
            poster_path = data["results"][0].get("poster_path")
            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path
    except:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster"

# -----------------------------
# Recommendation logic
# -----------------------------
def rec(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for idx, score in movies_list:
        movie_name = movies.iloc[idx].title
        recommended_movies.append(movie_name)
        recommended_posters.append(fetch_poster(movie_name))

    return recommended_movies, recommended_posters

# -----------------------------
# Load data
# -----------------------------
movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open("similarity.pkl", "rb"))

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 Movie Recommendation System")

selected_movie_name = st.selectbox(
    "Select a movie:",
    movies["title"].values
)

if st.button("Recommend"):
    names, posters = rec(selected_movie_name)

    cols = st.columns(len(names))
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.text(name)
            st.image(poster, use_container_width=True)

import streamlit as st
import random

st.title("🎬 Random Movie Night Picker 🍿")
st.write("Pick your mood, pick your industry, and let us surprise you!")

# Get user's name
name = st.text_input("What is your name?")

# Choose industry
industry = st.selectbox(
    "Choose an industry:",
    ["Hollywood", "Nollywood", "Bollywood", "Korean"]
)

# Choose genre
genre = st.selectbox(
    "Choose a genre:",
    ["Action", "Romance", "Comedy", "Horror"]
)

# Movie lists
hollywood = {
    "Action": ["Mad Max: Fury Road", "John Wick", "Black Panther"],
    "Romance": ["La La Land", "The Notebook", "10 Things I Hate About You"],
    "Comedy": ["Bridesmaids", "Superbad", "Booksmart"],
    "Horror": ["Get Out", "The Conjuring", "Us"]
}
nollywood = {
    "Action": ["King of Boys", "The Figurine"],
    "Romance": ["Fifty", "Isoken","Finally Falling"],
    "Comedy": ["Chief Daddy", "The Wedding Party"],
    "Horror": ["Living in Bondage", "Hex"]
}
bollywood = {
    "Action": ["War", "Dhoom 3"],
    "Romance": ["Yeh Jawaani Hai Deewani", "Dilwale Dulhania Le Jayenge"],
    "Comedy": ["3 Idiots", "Chennai Express"],
    "Horror": ["Stree", "Pari"]
}
korean = {
    "Action": ["Train to Busan", "The Man from Nowhere"],
    "Romance": ["Tune in for Love", "Always"],
    "Comedy": ["Extreme Job", "Sunny"],
    "Horror": ["The Wailing", "Gonjiam: Haunted Asylum"]
}

# Button to generate a pick
if st.button("🍿 Pick my movie!"):
    movies = None
    if industry == "Hollywood":
        movies = hollywood.get(genre)
    elif industry == "Nollywood":
        movies = nollywood.get(genre)
    elif industry == "Bollywood":
        movies = bollywood.get(genre)
    elif industry == "Korean":
        movies = korean.get(genre)
    if movies:
        movie_pick = random.choice(movies)
        st.success(f"{name if name else 'You'}, would love: **{movie_pick}** 💖 ")
    else:
        st.error("Sorry, we don't have movies for that combination. Try again!")


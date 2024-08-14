import requests
from .config import tmdb_auth

def get_top_releases():
    url = "https://api.themoviedb.org/3/movie/top_rated?language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {tmdb_auth}"
    }

    response = requests.get(url, headers=headers)
    return response.json()

def get_releases():
    url = "https://api.themoviedb.org/3/movie/now_playing?language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {tmdb_auth}"
    }

    response = requests.get(url, headers=headers)
    return response.json()

def get_trending():
    url = "https://api.themoviedb.org/3/trending/movie/day?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {tmdb_auth}"
    }

    response = requests.get(url, headers=headers)
    return response.json()

def get_upcoming():
    url = "https://api.themoviedb.org/3/movie/upcoming?language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {tmdb_auth}"
    }

    response = requests.get(url, headers=headers)
    return response.json()

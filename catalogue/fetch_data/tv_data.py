import requests
from .utils import rename_field
from .config import tmdb_auth

def get_tv_trending():
    url = "https://api.themoviedb.org/3/trending/tv/day?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {tmdb_auth}"
    }

    response = requests.get(url, headers=headers)
    data = rename_field(response.json())
    return data

def get_airing_today():
    url = "https://api.themoviedb.org/3/tv/airing_today?language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {tmdb_auth}"
    }

    response = requests.get(url, headers=headers)
    data = rename_field(response.json())
    return data

def get_on_the_air():
    url = "https://api.themoviedb.org/3/tv/on_the_air?language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {tmdb_auth}"
    }

    response = requests.get(url, headers=headers)
    data = rename_field(response.json())
    return data

def get_tv_popular():
    url = "https://api.themoviedb.org/3/tv/popular?language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {tmdb_auth}"
    }

    response = requests.get(url, headers=headers)
    data = rename_field(response.json())
    return data

def get_tv_top_rated():
    url = "https://api.themoviedb.org/3/tv/top_rated?language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {tmdb_auth}"
    }

    response = requests.get(url, headers=headers)
    data = rename_field(response.json())
    return data
# fetch_data/config.py
import os
from dotenv import load_dotenv

load_dotenv()
tmdb_auth = os.getenv("TMDB_AUTH")
watchmode_auth = os.getenv("WATCHMODE_API_KEY")

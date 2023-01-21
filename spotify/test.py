from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from pprint import pprint

from dotenv import load_dotenv
import os

load_dotenv()

client_credentials_manager = SpotifyClientCredentials(client_id=os.getenv('SPOTIFY_CLIENT_ID'), client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

search_str = 'Muse'
result = sp.search(search_str)
pprint(result)
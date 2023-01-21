from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

import spotipy
from pprint import pprint

from dotenv import load_dotenv
import os

load_dotenv()

client_credentials_manager = SpotifyClientCredentials(client_id=os.getenv('SPOTIFY_CLIENT_ID'), client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'))
sp = spotipy.Spotify(
    client_credentials_manager=client_credentials_manager,
    auth_manager=SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
        scope='user-read-recently-played user-library-read playlist-modify-private playlist-modify-public user-library-read user-library-modify user-top-read user-read-currently-playing',
        cache_path=os.getenv('SPOTIFY_CACHE_PATH'))

    )

search_str = 'Muse'
pprint(sp.current_user_recently_played())

pprint(sp.current_user())

username = sp.current_user()["id"]

# # Get the user's top songs
# top_songs = sp.current_user_top_tracks()
# song_uris = [song['uri'] for song in top_songs['items']]

# # Create a new playlist for the user's top songs
# playlist_name = "My Top Songs"
# playlist = sp.user_playlist_create(username, playlist_name)
# playlist_id = playlist['id']

# # Add the songs to the playlist
# sp.user_playlist_add_tracks(username, playlist_id, song_uris)

# print("Successfully created playlist " + playlist_name + " with your top songs.")

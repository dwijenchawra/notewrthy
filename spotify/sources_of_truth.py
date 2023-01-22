from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

import spotipy
from pprint import pprint

from dotenv import load_dotenv
import os

load_dotenv()


# given a spotify playlist url, get the average valence, energy, danceability, tempo, mode, acousticness, instrumentalness, and loudness of the songs in the playlist
def get_playlist_features(playlist_url):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
                redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
                scope='user-read-recently-played user-library-read playlist-modify-private playlist-modify-public user-library-read user-library-modify user-top-read user-read-currently-playing',
                cache_path=os.getenv('SPOTIFY_CACHE_PATH')))
    playlist_id = playlist_url.split("?")[0].split("/")[4]
    results = sp.playlist_items(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    track_ids = []
    for item in tracks:
        track_ids.append(item['track']['id'])
    features = sp.audio_features(track_ids)
    valence = 0
    energy = 0
    danceability = 0
    tempo = 0
    mode = 0
    acousticness = 0
    instrumentalness = 0
    loudness = 0
    for feature in features:
        valence += feature['valence']
        energy += feature['energy']
        danceability += feature['danceability']
        tempo += feature['tempo']
        mode += feature['mode']
        acousticness += feature['acousticness']
        instrumentalness += feature['instrumentalness']
        loudness += feature['loudness']
    valence /= len(features)
    energy /= len(features)
    danceability /= len(features)
    tempo /= len(features)
    mode /= len(features)
    acousticness /= len(features)
    instrumentalness /= len(features)
    loudness /= len(features)

    # create list of average values
    vector = [valence, energy, danceability, tempo, mode, acousticness, instrumentalness, loudness]
    return vector

    return {"valence": valence, "energy": energy, "danceability": danceability, "tempo": tempo, "mode": mode, "acousticness": acousticness, "instrumentalness": instrumentalness, "loudness": loudness}



print("love playlist")
pprint(get_playlist_features("https://open.spotify.com/playlist/37i9dQZF1EIcE10fGQVrZK?si=bdccb7779fbb4fdd"))

print("happy playlist")
pprint(get_playlist_features("https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLTmlC?si=034a405a5c604efe"))

print("sad playlist")
pprint(get_playlist_features("https://open.spotify.com/playlist/7qarwC71fp7GBE1tocN3hU?si=21a64375f3d043cf"))

print("angry playlist")
pprint(get_playlist_features("https://open.spotify.com/playlist/37i9dQZF1EIgNZCaOGb0Mi?si=f28076fffbd34ea0"))

print("excited playlist")
pprint(get_playlist_features("https://open.spotify.com/playlist/37i9dQZF1EIg65X9FWVODX?si=816d0ec3bdb444d0"))
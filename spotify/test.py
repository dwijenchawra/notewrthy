from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

import spotipy
from pprint import pprint

from dotenv import load_dotenv
from tqdm import tqdm
import os

load_dotenv()

love = [
    0.40194,
    0.5365000000000001,
    0.6223400000000001,
    115.34268000000002,
    0.88,
    0.4081372,
    0.011372955800000003,
    -7.34488,
]
happy = [
    0.59787,
    0.7359399999999999,
    0.6777299999999998,
    120.32875,
    0.71,
    0.12648247999999995,
    0.0031038976,
    -5.245430000000002,
]
sad = [
    0.3026608695652174,
    0.4466391304347825,
    0.5615760869565216,
    123.51227173913044,
    0.8586956521739131,
    0.5126115217391305,
    0.03200099934782609,
    -8.877771739130429,
]
angry = [
    0.46524799999999994,
    0.7859599999999999,
    0.5679000000000001,
    130.28026000000003,
    0.44,
    0.07928980000000001,
    0.004783572,
    -4.866699999999999,
]
excited = [
    0.52866,
    0.75794,
    0.5932600000000001,
    130.64178,
    0.82,
    0.07200495999999999,
    0.0061866928,
    -5.571400000000001,
]


class SpotifyClient:
    def __init__(self):
        client_credentials_manager = SpotifyClientCredentials(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        )
        self.client = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager,
            auth_manager=SpotifyOAuth(
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
                scope="user-read-recently-played user-library-read playlist-modify-private playlist-modify-public user-library-read user-library-modify user-top-read user-read-currently-playing user-read-playback-state user-modify-playback-state",
                cache_path=os.getenv("SPOTIFY_CACHE_PATH"),
            ),
        )

    def get_current_user(self):
        return self.client.current_user()

    def get_current_user_recently_played(self, limit=5):
        return self.client.current_user_recently_played(limit)

    def get_current_user_top_tracks(self, limit=5):
        return self.client.current_user_top_tracks(limit, time_range="short_term")

    def get_current_user_top_artists(self, limit=5):
        return self.client.current_user_top_artists(limit, time_range="short_term")

    def get_current_user_saved_tracks(self):
        return self.client.current_user_saved_tracks(limit=1000)

    def get_track_name(self, track_id):
        return self.client.track(track_id)["name"]

    def recommend_song(self, emotion):
        user_id = self.get_current_user()["id"]

        # results = self.get_current_user_saved_tracks()
        results = self.client.current_user_saved_tracks(limit=50, offset=1000)
        temp = results["items"]

        while results['next']:
            results = self.client.next(results)
            temp.extend(results['items'])

        tracks = []
        for item in temp:
            tracks.append(item["track"]["id"])

        print(len(tracks))

        # get features in batches of 50
        features = []
        for i in tqdm(range(0, len(tracks), 50)):
            features.extend(self.client.audio_features(tracks[i : i + 50]))


        trackdict = {tracks[i]: features[i] for i in range(len(tracks))}

        print(len(features))

        recommended_tracks = {}

        for element in tqdm(trackdict.keys()):
            trackfeatures = trackdict[element]
            currentvector = None

            if emotion == "love":
                currentvector = love
            elif emotion == "happy":
                currentvector = happy
            elif emotion == "sad":
                currentvector = sad
            elif emotion == "angry":
                currentvector = angry
            elif emotion == "excited":
                currentvector = excited

            # get distance to current vector
            distance = 0
            for i in range(0, 8):
                distance += (trackfeatures[i] - currentvector[i]) ** 2
            distance = distance ** 0.5

            # add to recommended tracks
            recommended_tracks[element] = distance
            


                
            

        if recommended_tracks:
            # return 5 recommended songs
            tracks_with_names = {}
            for track in recommended_tracks.keys():
                tracks_with_names[self.get_track_name(track)] = recommended_tracks[
                    track
                ]
            return tracks_with_names
        else:
            return None


# test = SpotifyClient()
# print(test.get_current_user()["display_name"])
# print("-----------------------")
# for item in test.get_current_user_recently_played()["items"]:
#     print(item["track"]["name"])
# print("-----------------------")
# for item in test.get_current_user_top_tracks()["items"]:
#     print(item["name"])
# print("-----------------------")
# for item in test.get_current_user_top_artists()["items"]:
#     print(item["name"])
# print("-----------------------")

# # for item in test.get_current_user_saved_tracks()['items'][:5]:
# # print(item['track']['name'])

# print("-----------------------")

# pprint(test.recommend_song("love"))


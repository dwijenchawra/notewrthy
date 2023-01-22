from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

import spotipy
from pprint import pprint

from dotenv import load_dotenv
import os

load_dotenv()



class SpotifyClient:

    def __init__(self):
        client_credentials_manager = SpotifyClientCredentials(client_id=os.getenv('SPOTIFY_CLIENT_ID'), client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'))
        self.client = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager,
            auth_manager=SpotifyOAuth(
                client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
                redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
                scope='user-read-recently-played user-library-read playlist-modify-private playlist-modify-public user-library-read user-library-modify user-top-read user-read-currently-playing',
                cache_path=os.getenv('SPOTIFY_CACHE_PATH'))
            )

    def get_current_user(self):
        return self.client.current_user()
    
    def get_current_user_recently_played(self, limit=5):
        return self.client.current_user_recently_played(limit)
    
    def get_current_user_top_tracks(self, limit=5):
        return self.client.current_user_top_tracks(limit, time_range='short_term')
    
    def get_current_user_top_artists(self, limit=5):
        return self.client.current_user_top_artists(limit, time_range='short_term')
    
    def get_current_user_saved_tracks(self):
        return self.client.current_user_saved_tracks(limit=1000)
    
    def get_track_name(self, track_id):
        return self.client.track(track_id)['name']


    def recommend_song(self, emotion):
        user_id = self.get_current_user()['id']
        if emotion == "happy":
            valence = 0.8
            energy = 0.6
            danceability = 0.8
            tempo = 120
        elif emotion == "sad":
            valence = 0.2
            energy = 0.4
            danceability = 0.4
            tempo = 80
        elif emotion == "love":
            valence = 0.7
            energy = 0.5
            danceability = 0.7
            tempo = 100
        elif emotion == "excited":
            valence = 0.7
            energy = 0.7
            danceability = 0.8
            tempo = 140
        elif emotion == "angry":
            valence = 0.4
            energy = 0.8
            danceability = 0.6
            tempo = 140
        else:
            print("Invalid emotion")
            return

        # results = self.get_current_user_saved_tracks()
        results = self.client.current_user_saved_tracks(limit=50, offset=0)
        temp = results['items']
        # while results['next']:
        #     results = self.client.next(results)
        #     temp.extend(results['items'])

        
        tracks = []
        for item in temp:
            tracks.append(item['track']['id'])
        
        print(len(tracks))

        features = self.client.audio_features(tracks)
        trackdict = {self.get_track_name(tracks[i]): features[i] for i in range(len(tracks))}

        print(len(features))

        recommended_tracks = {}
        

        for element in trackdict.keys():
            trackfeatures = trackdict[element]
            if emotion == "happy":
                if trackfeatures['valence'] > valence and trackfeatures['energy'] > energy and trackfeatures['danceability'] > danceability and trackfeatures['tempo'] > tempo:
                    recommended_tracks[element] = trackfeatures
            elif emotion == "sad":
                if trackfeatures['valence'] < valence and trackfeatures['energy'] < energy and trackfeatures['danceability'] < danceability and trackfeatures['tempo'] < tempo:
                    recommended_tracks[element] = trackfeatures
            elif emotion == "love":
                if trackfeatures['valence'] > valence and trackfeatures['energy'] < energy and trackfeatures['danceability'] > danceability and trackfeatures['tempo'] < tempo:
                    recommended_tracks[element] = trackfeatures
            elif emotion == "excited":
                if trackfeatures['valence'] > valence and trackfeatures['energy'] > energy and trackfeatures['danceability'] > danceability and trackfeatures['tempo'] > tempo:
                    recommended_tracks[element] = trackfeatures
            elif emotion == "angry":
                if trackfeatures['valence'] < valence and trackfeatures['energy'] > energy and trackfeatures['danceability'] < danceability and trackfeatures['tempo'] > tempo:
                    recommended_tracks[element] = trackfeatures
            else:
                print("Invalid emotion")
                return
        if recommended_tracks:
            #return 5 recommended songs
            return recommended_tracks
        else:
            return None



        


test = SpotifyClient()
print(test.get_current_user()['display_name'])
print("-----------------------")
for item in test.get_current_user_recently_played()['items']:
    print(item['track']['name'])
print("-----------------------")
for item in test.get_current_user_top_tracks()['items']:
    print(item['name'])
print("-----------------------")
for item in test.get_current_user_top_artists()['items']:
    print(item['name'])
print("-----------------------")

# for item in test.get_current_user_saved_tracks()['items'][:5]:
    # print(item['track']['name'])

print("-----------------------")

print(test.recommend_song("sad"))


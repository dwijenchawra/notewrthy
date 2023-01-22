import os
import time
import psycopg2
from flask import Flask, request, jsonify, render_template, redirect, session
from flask_caching import Cache

from flask_session import Session
from pydub import AudioSegment
from google.cloud import speech
import nltk
from cryptography.fernet import Fernet
from nltk.sentiment import SentimentIntensityAnalyzer
import spotipy
from spotipy import SpotifyClientCredentials, SpotifyOAuth, CacheFileHandler
import dotenv



dotenv.load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SESSION_TYPE'] = 'filesystem'

app.config["CACHE_TYPE"] = "FileSystemCache" # better not use this type w. gunicorn
app.config["CACHE_DIR"] = "cache"
cache = Cache(app)


Session(app)

# @app.route('/')
# def index():
#     response = startup.getUser()
#     return redirect(response)

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

vectorlist = [love, happy, sad, angry, excited]

@app.route('/callback')
def index():

    print(cache.get("username"))

    cache_handler = CacheFileHandler(username=cache.get("username"))
    auth_manager = SpotifyOAuth(
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
                scope="user-read-recently-played user-library-read playlist-modify-private playlist-modify-public user-library-read user-library-modify user-top-read user-read-currently-playing user-read-playback-state user-modify-playback-state",
                cache_path=os.getenv("SPOTIFY_CACHE_PATH"),
                cache_handler=CacheFileHandler(username=cache.get("username")),
                show_dialog=True    
            )

    if request.args.get("code"):
        print("code")
        auth_manager.get_cached_token()
        # Step 2. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        cache_handler.save_token_to_cache(auth_manager.get_cached_token())
        return redirect('/callback')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        print("not logged in")
        # Step 1. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    # Step 3. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return f'<h2>Hi {spotify.me()["display_name"]}, ' \
           f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
           f'<a href="/playlists">my playlists</a> | ' \
           f'<a href="/currently_playing">currently playing</a> | ' \
        f'<a href="/current_user">me</a>' \

@app.route('/sign_out')
def sign_out():
    session.pop("token_info", None)
    return redirect('/callback')

@app.route('/test')
def test():
    return "hello"

@app.route('/playlists')
def playlists():
    cache_handler = CacheFileHandler(username=cache.get("username"))
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    client = spotipy.Spotify(auth_manager=auth_manager)
    return jsonify(client.current_user_playlists())


@app.route("/create_playlist")
def create_playlist():
    pass


def compare_music_taste(user1_id, user2_id):
    # get music data for both users
    # expects [[songs], [artists], [genres]]
    user1_data = []
    user2_data = []
    with conn.cursor() as cur:
        cur.execute(f"SELECT top5genres, top5artists, top5songs FROM preferences WHERE user_id='{user1_id}'")
        res = cur.fetchall()
        user1_data = [res[0][2], res[0][1], res[0][0]]
        cur.execute(f"SELECT top5genres, top5artists, top5songs FROM preferences WHERE user_id='{user2_id}'")
        res = cur.fetchall()
        user2_data = [res[0][2], res[0][1], res[0][0]]

    # compare the top 5 songs
    song_match = len(set(user1_data[0]).intersection(user2_data[0])) / 3

    # compare the top 5 artists
    artist_match = len(set(user1_data[1]).intersection(user2_data[1])) / 3

    # compare the top 5 genres (weighted more heavily)
    genre_match = len(set(user1_data[2]).intersection(user2_data[2])) / 3

    # calculate the overall compatibility as a percentage
    compatibility = (song_match + (artist_match * 2) + (genre_match * 3)) / 6 * 100

    with conn.cursor() as cur:
        cur.execute(f"INSERT INTO compatibility (user_id_1, user_id_2, comp) VALUES ('{user1_id}', '{user2_id}', {compatibility})")
        conn.commit()

@app.route("/sign_up", methods=["POST"])
def sign_up():
    username = request.json['username']
    password = request.json['password']
    key = ""
    with open("secret.txt") as f:
        key = f.readline()
    fern = Fernet(key)
    password = fern.encrypt(password.encode()).decode("utf-8").strip("'")
    with conn.cursor() as cur:
        cur.execute("SELECT username, password, id FROM users")
        res = cur.fetchall()
        g = 1
        for user in res:
            if user[0] == username:
                g = 0
                if user[1] == fern.decrypt(password).decode("utf-8"):
                    cache.set("username", username)
                    return jsonify("user_login")
                else:
                    return jsonify("incorrect_pass")
        if g == 1:
            cur.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")
            cur.execute(f"SELECT user_id FROM users WHERE username='{username}'")
            user_id = cur.fetchall()[0][0]
            for user in res:
                compare_music_taste(user[2], user_id)
            conn.commit()
            cache.set("username", username)
            return jsonify("user_created")

@app.route("/get_feed")
def get_feed():
    
    curruser = cache.get("username")

    # get request to this method
    # should return a list of json objects in the following format:
    # {"username": "exampleuser", "mood": "examplemood", "spotify_link": "examplelink", "compatibility": "examplecomp"}
    with conn.cursor() as cur:

        cur.execute(f"SELECT id FROM users WHERE username='{curruser}'")
        user_id = cur.fetchall()[0][0]
        
        cur.execute("SELECT user_id, mood, playlist_link FROM feedinfo")
        feeds = cur.fetchall()
        comps = []
        # gets all of the comps where at least one of the things are the current user
        try:
            cur.execute(f"SELECT user_id_1, user_id_2, comp FROM compatability WHERE user_id_1='{user_id}'")
            comps = cur.fetchall()
        except Exception:
            cur.execute("ROLLBACK;")
        try:
            cur.execute(f"SELECT user_id_1, user_id_2, comp FROM compatability WHERE user_id_2='{user_id}'")
            comps.extend(cur.fetchall())
        except Exception:
            cur.execute("ROLLBACK;")
        print(comps)
        output = []
        for f in feeds:
            if f[0] == user_id:
                continue
            obj = {}
            print(f[0])
            foo = f[0]
            cur.execute(f"SELECT username FROM users WHERE id='{foo}'")
            username = cur.fetchall()[0][0]
            obj["username"] = username
            obj["spotify"] = f[2]
            obj["mood"] = f[1]
            for comp in comps:
                if comp[0] == f[0] or comp[1] == f[0]:
                    obj["compatibility"] = comp[2]
                    break
            output.append(obj)
    return output

def get_polarity(text):
    nltk.download('vader_lexicon')
    sid = SentimentIntensityAnalyzer()
    sentiment = sid.polarity_scores(text)

    angry_words = ["angry", "mad", "irritated", "frustrated", "annoyed"]
    for word in angry_words:
        if word in text:
            return "angry"
    emotions = {"happy": sentiment["pos"], "excited": sentiment["pos"], "sad": sentiment["neg"], "love": sentiment["pos"]}
    top_emotion = max(emotions, key=lambda key: emotions[key])
    if "love" in text:
        top_emotion = "love"
    return top_emotion

@app.route("/analyze_audio", methods = ["POST"])
def analyze_audio():
    if 'recording' not in request.files:
        return jsonify('no image uploaded')
    request.files['recording'].save("./recording.wav")                                                                
    src = "recording.wav"
    dst = "recording.mp3"                                                   
    sound = AudioSegment.from_mp3(src)
    sound.export(dst, format="mp3")
    client = speech.SpeechClient.from_service_account_file('key.json')

    file_name = dst

    with open(file_name, 'rb') as f:
        mp3_data = f.read()

    audio_file = speech.RecognitionAudio(content = mp3_data)

    config = speech.RecognitionConfig(
        sample_rate_hertz=44100,
        enable_automatic_punctuation = True,
        language_code = 'en-US'
    )

    response = client.recognize(
        config = config,
        audio = audio_file
    )
    transcript = ""
    for result in response.results:
        transcript = "{}".format(result.alternatives[0].transcript)
    emotion  = get_polarity(transcript)
    return {"emotion": emotion, "text": transcript}


@app.route("/gettopemotion/<emotion>")
def gettopemotion(emotion):

    cache_handler = CacheFileHandler(username=cache.get("username"))
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    client = spotipy.Spotify(auth_manager=auth_manager)

    with conn.cursor() as cur:
        curruser = cache.get("username")
        print(curruser)
        # get user_id using username
        cur.execute(f"SELECT id FROM users WHERE username='{curruser}'")
        user_id = cur.fetchall()[0][0]

        # select top 10 items from happydist column from songs table where preferences_id equals user_id 
        cur.execute(f"SELECT song_id FROM songs WHERE preferences_id='{user_id}' ORDER BY {emotion} ASC LIMIT 10")
        res = cur.fetchall()
        links = []
        for r in res:
            links.append(client.track(r[0])["name"])
        return jsonify(links)
        


@app.route("/loadtracksintodb")
def loadtracksintodb():
    print("loading tracks into db")
    # time.sleep(5)
    # print("loading tracks into db")

    cache_handler = CacheFileHandler(username=cache.get("username"))
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    client = spotipy.Spotify(auth_manager=auth_manager)
    


    user_id = client.current_user()["id"]
    print(user_id)

    with conn.cursor() as cur:
        curruser = cache.get("username")
        print(curruser)
        # get user_id using username
        cur.execute(f"SELECT id FROM users WHERE username='{curruser}'")
        user_id = cur.fetchall()[0][0]

        print(user_id)

        # results = self.get_current_user_saved_tracks()
        results = client.current_user_saved_tracks(limit=50, offset=0)
        temp = results["items"]

        while results['next']:
            results = client.next(results)
            temp.extend(results['items'])

        tracks = []
        for item in temp:
            tracks.append(item["track"]["id"])

        print(len(tracks))

        # get features in batches of 50
        features = []
        for i in range(0, len(tracks), 50):
            features.extend(client.audio_features(tracks[i : i + 50]))
        
        trackdict = {tracks[i]: features[i] for i in range(len(tracks))}

        recommended_tracks = {}

        counter = 0

            
        for element in trackdict.keys():
            counter += 1 
            if counter == 100:
                break

            trackfeatures = trackdict[element]
            # get acousticness, danceability, energy, instrumentalness, loudness, mode, tempo, valence from track
            try:
                featurelist = [
                    trackfeatures["valence"],
                    trackfeatures["energy"],
                    trackfeatures["danceability"],
                    trackfeatures["tempo"],
                    trackfeatures["mode"],
                    trackfeatures["acousticness"],
                    trackfeatures["instrumentalness"],
                    trackfeatures["loudness"]
                ]
            except:
                continue

            vdistance = []

            for vector in vectorlist:
                currentvector = vector
                # get distance to current vector
                distance = 0
                for i in range(0, 8):
                    distance += (featurelist[i] - currentvector[i]) ** 2
                distance = distance ** 0.5
                vdistance.append(distance)

            lovedist = vdistance[0]
            happydist = vdistance[1]
            sadist = vdistance[2]
            angrydist = vdistance[3]
            excitedist = vdistance[4]

            if element == "7wBJfHzpfI3032CSD7CE2m":
                print(featurelist)
                print(currentvector)
                print(vdistance)
            
            # upload all vector distances to database
            nullstring = "NULL"
            print(happydist)
            print(sadist)
            print(angrydist)
            print(excitedist)
            print(lovedist)
            # cur.execute(f"INSERT INTO songs (song_id, song_data, lovedist, happydist, sadist, angrydist, excitedist, preferences_id) VALUES ('{element}', {nullstring}, {lovedist}, {happydist}, {sadist}, {angrydist}, {excitedist}, '{user_id}');")

        conn.commit()

    return jsonify("done")
            


        
        


        
        

    

    


if __name__ == "__main__":
    # creating the table
    # with conn.cursor() as cur:
 
        # cur.execute("CREATE TABLE preferences (user_id UUID, top5Genres STRING[], top5Artists STRING[], top5Songs STRING[], );")

        #drop preferences table
        # cur.execute("DROP TABLE IF EXISTS songs;")

        # # make user_id in preferences a unique key and primary
        # cur.execute("CREATE TABLE preferences (user_id UUID PRIMARY KEY, top5Genres STRING[], top5Artists STRING[], top5Songs STRING[]);")

        # # time.sleep(20)


        # cur.execute("CREATE TABLE songs (song_id STRING, song_data JSONB, lovedist FLOAT, happydist FLOAT, sadist FLOAT, angrydist FLOAT, excitedist FLOAT, preferences_id UUID, FOREIGN KEY (preferences_id) REFERENCES preferences(user_id));")
        # cur.execute("CREATE INDEX lovedist_index ON songs (lovedist);")
        # cur.execute("CREATE INDEX happydist_index ON songs (happydist);")
        # cur.execute("CREATE INDEX sadist_index ON songs (sadist);")
        # cur.execute("CREATE INDEX angrydist_index ON songs (angrydist);")
        # cur.execute("CREATE INDEX excitedist_index ON songs (excitedist);")

        # conn.commit()
        # cur.execute("DROP INDEX IF EXISTS acousticness_index;")
        # cur.execute("DROP INDEX IF EXISTS instrumentalness_index;")
        # cur.execute("DROP INDEX IF EXISTS loudness_index;")
        # cur.execute("DROP INDEX IF EXISTS mode_index;")
        # cur.execute("DROP INDEX IF EXISTS tempo_index;")
        # cur.execute("DROP INDEX IF EXISTS danceability_index;")
        # cur.execute("DROP INDEX IF EXISTS energy_index;")
        # cur.execute("DROP INDEX IF EXISTS valence_index;")

        # # drop the columns as well
        # cur.execute("ALTER TABLE songs DROP COLUMN IF EXISTS valence;")
        # cur.execute("ALTER TABLE songs DROP COLUMN IF EXISTS energy;")
        # cur.execute("ALTER TABLE songs DROP COLUMN IF EXISTS danceability;")
        # cur.execute("ALTER TABLE songs DROP COLUMN IF EXISTS tempo;")
        # cur.execute("ALTER TABLE songs DROP COLUMN IF EXISTS mode;")
        # cur.execute("ALTER TABLE songs DROP COLUMN IF EXISTS acousticness;")
        # cur.execute("ALTER TABLE songs DROP COLUMN IF EXISTS instrumentalness;")
        # cur.execute("ALTER TABLE songs DROP COLUMN IF EXISTS loudness;")
        # time.sleep(2)

        # # make valence, energy, danceability, tempo, mode, acousticness, instrumentalness, loudness indexes
        # cur.execute("CREATE INDEX valence_index ON songs (valence);")
        # time.sleep(2)
        # cur.execute("CREATE INDEX energy_index ON songs (energy);")
        # time.sleep(2)
        # cur.execute("CREATE INDEX danceability_index ON songs (danceability);")
        # time.sleep(2)
        # cur.execute("CREATE INDEX tempo_index ON songs (tempo);")
        # time.sleep(2)
        # cur.execute("CREATE INDEX mode_index ON songs (mode);")
        # time.sleep(2)
        # cur.execute("CREATE INDEX acousticness_index ON songs (acousticness);")
        # time.sleep(2)
        # cur.execute("CREATE INDEX instrumentalness_index ON songs (instrumentalness);")
        # time.sleep(2)
        # cur.execute("CREATE INDEX loudness_index ON songs (loudness);")
        # time.sleep(2)



        # conn.commit()
        # cur.execute("SHOW TABLES;")
        # res = cur.fetchall()
        # print(res)
    # fern = Fernet(key)
    # message = "This is the password"
    # encMessage = fernet.encrypt(message.encode())
    # print("original string: ", message)
    # print("encrypted string: ", encMessage)
    
    # # decrypt the encrypted string with the
    # # Fernet instance of the key,
    # # that was used for encrypting the string
    # # encoded byte string is returned by decrypt method,
    # # so decode it to string with decode methods
    # decMessage = fernet.decrypt(encMessage).decode()
    
    # print("decrypted string: ", decMessage)
    app.secret_key = os.urandom(24)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host="0.0.0.0", debug=True, threaded=True)

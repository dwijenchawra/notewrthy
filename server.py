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

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return jsonify(spotify.current_user_playlists())


@app.route("/create_playlist")
def create_playlist():
    pass

@app.route("/sign_up", methods=["POST"])
def sign_up():
    username = request.json['username']
    password = request.json['password']
    print(username)
    print(password)
    key = ""
    with open("secret.txt") as f:
        key = f.readline()
    fern = Fernet(key)
    password = fern.encrypt(password.encode()).decode("utf-8").strip("'")
    with conn.cursor() as cur:
        cur.execute("SELECT username, password FROM users")
        res = cur.fetchall()
        g = 1
        for user in res:
            print(user)
            if user[0] == username:
                g = 0
                print(fern.encrypt(user[1].encode()).decode("utf-8").strip("'"))
                print(password)
                print(fern.decrypt(password).decode("utf-8"))
                if user[1] == fern.decrypt(password).decode("utf-8"):
                    cache.set("username", username)
                    return jsonify("user_login")
                else:
                    return jsonify("incorrect_pass")
        if g == 1:
            cur.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")
            conn.commit()

            cache.set("username", username)
            return jsonify("user_created")
    

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



if __name__ == "__main__":
    # creating the table
    # with conn.cursor() as cur:
 
        # cur.execute("CREATE TABLE preferences (user_id UUID, top5Genres STRING[], top5Artists STRING[], top5Songs STRING[], );")

        #drop preferences table
        # cur.execute("DROP TABLE IF EXISTS preferences;")

        # # make user_id in preferences a unique key and primary
        # cur.execute("CREATE TABLE preferences (user_id UUID PRIMARY KEY, top5Genres STRING[], top5Artists STRING[], top5Songs STRING[]);")

        # # time.sleep(20)


        # cur.execute("CREATE TABLE songs (song_id STRING, song_data JSONB, valence FLOAT, energy FLOAT, danceability FLOAT, tempo FLOAT, mode FLOAT, acousticness FLOAT, instrumentalness FLOAT, loudness FLOAT, preferences_id UUID, FOREIGN KEY (preferences_id) REFERENCES preferences(user_id));")
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

import os
import time
import psycopg2
from flask import Flask, request, jsonify, render_template, redirect
from pydub import AudioSegment
from google.cloud import speech
import nltk
from cryptography.fernet import Fernet
from nltk.sentiment import SentimentIntensityAnalyzer
import dotenv

from spotify.test import SpotifyClient


dotenv.load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')
app = Flask(__name__)

# @app.route('/')
# def index():
#     response = startup.getUser()
#     return redirect(response)

@app.route('/callback/')
def callback():
    test = SpotifyClient()
    return render_template("http://localhost:5000/callback/")




@app.route("/create_playlist")
def create_playlist():
    pass

@app.route("/sign_up", methods=["POST"])
def sign_up():
    with open("../aes-128.key") as f:
        line = f.readline()
    print(line)
    return jsonify("success")
    

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
    app.run(host="0.0.0.0", debug=True)

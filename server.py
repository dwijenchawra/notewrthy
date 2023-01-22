import os
from time import time
import psycopg2
from flask import Flask, request, jsonify
from pydub import AudioSegment
from google.cloud import speech
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

conn = psycopg2.connect(os.environ["DATABASE_URL"])
app = Flask(__name__)

@app.route("/create_playlist")
def create_playlist():
    pass

@app.route("/")
def index():
    return {"owijefw": "owiefj"}

@app.route("/sign_up", methods=["POST"])
def sign_up():
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
    with conn.cursor() as cur:
 
        # cur.execute("CREATE TABLE preferences (user_id UUID, top5Genres STRING[], top5Artists STRING[], top5Songs STRING[], );")

        # make user_id in preferences a unique key
        cur.execute("ALTER TABLE preferences ADD CONSTRAINT user_id UNIQUE (user_id);")

        cur.execute("CREATE TABLE songs (song_id STRING, song_data JSONB, valence FLOAT, energy FLOAT, danceability FLOAT, tempo FLOAT, mode FLOAT, acousticness FLOAT, instrumentalness FLOAT, loudness FLOAT, preferences_id UUID, FOREIGN KEY (preferences_id) REFERENCES preferences(user_id));")
        # make valence, energy, danceability, tempo, mode, acousticness, instrumentalness, loudness indexes
        cur.execute("CREATE INDEX valence_index ON users (valence);")
        time.sleep(2)
        cur.execute("CREATE INDEX energy_index ON users (energy);")
        time.sleep(2)
        cur.execute("CREATE INDEX danceability_index ON users (danceability);")
        time.sleep(2)
        cur.execute("CREATE INDEX tempo_index ON users (tempo);")
        time.sleep(2)
        cur.execute("CREATE INDEX mode_index ON users (mode);")
        time.sleep(2)
        cur.execute("CREATE INDEX acousticness_index ON users (acousticness);")
        time.sleep(2)
        cur.execute("CREATE INDEX instrumentalness_index ON users (instrumentalness);")
        time.sleep(2)
        cur.execute("CREATE INDEX loudness_index ON users (loudness);")
        time.sleep(2)



        conn.commit()
        cur.execute("SHOW TABLES;")
        res = cur.fetchall()
        print(res)
    # app.run(host="0.0.0.0", debug=True)

import os
import psycopg2
from flask import Flask, request, jsonify
from pydub import AudioSegment
from google.cloud import speech
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

@app.route("/create_playlist")
def create_playlist():
    pass

@app.route("/")
def index():
    return {"owijefw": "owiefj"}

@app.route("/sign_in")
def sign_in():
    pass

@app.route("/sign_up")
def sign_up():
    pass

def get_polarity(text):
    nltk.download('vader_lexicon')
    sid = SentimentIntensityAnalyzer()
    sentiment = sid.polarity_scores(text)
    
    emotions = {"happy": sentiment["pos"], "excited": sentiment["pos"], "sad": sentiment["neg"], 
                "angry": sentiment["neg"], "neutral": sentiment["neu"], "love": sentiment["pos"], 
                "stressed": sentiment["neg"]}
    top_two_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:2]
    return top_two_emotions

def get_emotions(results):
  emotions = ""
  for i in results:
    emotions += i[0] + " "
  return emotions

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

    for result in response.results:
        transcript = "{}".format(result.alternatives[0].transcript)
    result  = get_polarity(transcript)
    emotions = get_emotions(result)
    
    return {"emotions": emotions, "text": transcript}


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
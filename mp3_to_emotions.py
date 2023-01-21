from google.cloud import speech
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer


client = speech.SpeechClient.from_service_account_file('key.json')

file_name = "love.mp3"

with open(file_name, 'rb') as f:
    mp3_data = f.read()

audio_file = speech.RecognitionAudio(content=mp3_data)

config = speech.RecognitionConfig(
    sample_rate_hertz=44100,
    enable_automatic_punctuation=True,
    language_code='en-US'
)

response = client.recognize(
    config=config,
    audio=audio_file
)

for result in response.results:
    transcript = "{}".format(result.alternatives[0].transcript)

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

get_polarity(transcript)

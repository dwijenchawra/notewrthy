#pip install google-cloud-speech
#pip install -U nltk

from google.cloud import speech
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer


client = speech.SpeechClient.from_service_account_file('key.json')

file_name = "testAudio.mp3"

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

def get_polarity(text):
    nltk.download('vader_lexicon')
    sid = SentimentIntensityAnalyzer()
    sentiment = sid.polarity_scores(text)
    
    emotions = {"happy": sentiment["pos"], "excited": sentiment["pos"], "sad": sentiment["neg"], 
                "angry": sentiment["neg"], "neutral": sentiment["neu"], "love": sentiment["pos"], 
                "stressed": sentiment["neg"]}
    top_two_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:2]
    return top_two_emotions

result  = get_polarity(transcript)


def get_emotions(results):
  emotions = ""
  for i in results:
    emotions += i[0] + " "
  return emotions
get_emotions(result)
# Soundscape

### Best Use of CockroachDB Serverless

<img width="400" alt="image" src="https://user-images.githubusercontent.com/30065475/213947754-eb501b00-3d64-4aaa-8377-5990a23780b2.png">


https://devpost.com/software/soundscape-aw09nf
## Inspiration
Our inspiration for Soundscape came from our own experiences. We were tired of the limitations of traditional music streaming services, whose music recommendation system never catered to the moment. We wanted to create a platform to help music lovers like ourselves connect with others who shared similar tastes. At Soundscape, we strive to bring people together through the universal language of music and offer a unique way to discover new songs that express our moods.

## What it does
This program is designed to connect users with similar music tastes and preferences. It does this by analyzing the user's top tracks, artists, and genres, and then comparing that data with other users to determine compatibility. The program also gathers data from the user's Spotify accounts and creates playlists based on their current emotions and historical preferences. To classify emotions, the application listens to the user speak about how they are feeling and determine the sentiment associated with their speech.


## How we built it
The backend was built using Python and Flask, and the front end was built using React Native and Expo, allowing us to develop for both Android and iOS at the same time. We managed our data with CockroachDB. Using psycopg2, we created tables to store user credentials, user preferences, song information, compatibilities between users, and current feed information (see media for a detailed visualization). We also used CockroachDB to generate a secret key for the encryption of sensitive data and also used it to generate unique identifiers for each user. We used Google Cloud’s services to convert user audio to text and analyze the sentiment of the data to recommend music to the users. 

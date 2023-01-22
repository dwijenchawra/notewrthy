import os
import time
import psycopg2
from flask import Flask, request, jsonify, render_template, redirect, session
from flask_caching import Cache
from pprint import pprint

from flask_session import Session
from pydub import AudioSegment
from google.cloud import speech
import nltk
from cryptography.fernet import Fernet
from nltk.sentiment import SentimentIntensityAnalyzer
import spotipy
from spotipy import SpotifyClientCredentials, SpotifyOAuth, CacheFileHandler
import dotenv




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
        cur.execute(f"INSERT INTO compatability (user_id_1, user_id_2, comp) VALUES ('{user1_id}', '{user2_id}', {compatibility})")
        conn.commit()

conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')


with conn.cursor() as cur:


    # get all songs from songs table and then sort them
    cur.execute("UPDATE users SET username='Pradyun' WHERE id='10053061-426b-44a7-b8d5-75012bf7cd8e'")
    conn.commit()
    cur.execute("SELECT * FROM users")
    print(cur.fetchall())
    """
    res = cur.fetchall()
    res.sort(key=lambda x: x[2])
    print(res)

    print("\n\n\n\n\n")

    # get bottom 5 songs from songs table and sort them by happydist column
    cur.execute("SELECT * FROM songs ORDER BY happydist ASC LIMIT 5")
    res = cur.fetchall()
    print(res)



    # export entire songs table to csv
    # cur.execute("COPY songs TO '/tmp/songs.csv' DELIMITER ',' CSV HEADER")
    


    # cur.execute("SELECT * FROM users")
    # res = cur.fetchall()
    # print(res)
    # print("\n")
    # cur.execute("SELECT * FROM preferences")
    # res = cur.fetchall()
    # print(res)
    # print("\n")
    # cur.execute("SELECT * FROM compatability")
    # res = cur.fetchall()
    # print(res)
    # print("\n")
    # cur.execute("SELECT * FROM feedinfo")
    # res = cur.fetchall()
    # print(res)
    # print("\n")
    cur.execute("DELETE FROM users WHERE id = '7e72ea08-26c9-4f3c-890f-5be92df0bf75'")
    cur.execute("DELETE FROM users WHERE id = 'fb2076a9-6037-4349-be57-98fa96532a5d'")
    cur.execute("DELETE FROM users WHERE id = '18b8b257-0987-4a61-aadb-0a50e2d774be'")
    cur.execute("DELETE FROM users WHERE id = '296b87e2-2ca9-4f4f-8063-8381afa0b2dc'")
    conn.commit()
    """


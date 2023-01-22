import psycopg2
import os
from cryptography.fernet import Fernet
from flask import jsonify


# check if they exist in the db
# if they exist, interpret as sign in
# if they don't, interpret as sign up

conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')

def sign_up():
    username = input('what is the username?')
    password = input('what is the password?')
    key = ""
    with open("secret.txt") as f:
        key = f.readline()
    fern = Fernet(key)
    password = fern.encrypt(password.encode()).decode("utf-8").strip("'")
    with conn.cursor() as cur:
        cur.execute("SELECT username, password FROM users")
        res = cur.fetchall()
        g = 1
        print(res)
        for user in res:
            if user[0] == username:
                g = 0
                if user[1] == password:
                    return jsonify("user_login")
                else:
                    return jsonify("incorrect_pass")
        if g == 1:
            # cur.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")
            conn.commit()
            return jsonify("user_created")

sign_up()
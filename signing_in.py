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
    user_id = request.args.get("user_id")
    # get request to this method
    # should return a list of json objects in the following format:
    # {"username": "exampleuser", "mood": "examplemood", "spotify_link": "examplelink", "compatibility": "examplecomp"}
    with conn.cursor() as cur:
        cur.execute("SELECT user_id, mood, playlist_link FROM feedinfo")
        feeds = cur.fetchall()
        # gets all of the comps where at least one of the things are the current user
        cur.execute(f"SELECT user_id_1, user_id_2, comp FROM compatability WHERE user_id_1={user_id} UNION SELECT user_id_1, user_id_2, comp FROM compatability WHERE user_id_2={user_id}")
        comps = cur.fetchall()
        output = []
        for f in feeds:
            if f[0] == user_id:
                continue
            obj = {}
            cur.execute(f"SELECT username FROM users WHERE user_id='{f[0]}'")
            username = cur.fetchall()[0][0]
            obj["username"] = username
            obj["spotify_link"] = f[2]
            obj["mood"] = f[1]
            for comp in comps:
                if comp[0] == f[0] or comp[1] == f[0]:
                    obj["compatibility"] = comp[2]
                    break
            output.append(obj)
    return output
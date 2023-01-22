import psycopg2

def get_user_data(user_id):
    # connecting to the cockcroach db
    conn = psycopg2.connect("cockroachdb://user:password@host:port/database")
    cursor = conn.cursor()

    cursor.execute("SELECT songs, artists, genres FROM users WHERE id=%s", (user_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result


def compare_music_taste(user1_id, user2_id):
    # get music data for both users
    user1_data = get_user_data(user1_id)
    user2_data = get_user_data(user2_id)

    # compare the top 5 songs
    song_match = len(set(user1_data[0]).intersection(user2_data[0])) / 5

    # compare the top 5 artists
    artist_match = len(set(user1_data[1]).intersection(user2_data[1])) / 5

    # compare the top 5 genres (weighted more heavily)
    genre_match = len(set(user1_data[2]).intersection(user2_data[2])) / 5

    # calculate the overall compatibility as a percentage
    compatibility = (song_match + (artist_match * 2) + (genre_match * 3)) / 6 * 100

    return compatibility

# testing
user1_id = 1
user2_id = 2
compatibility = compare_music_taste(user1_id, user2_id)
print(f"The music taste compatibility between user {user1_id} and user {user2_id} is {compatibility}%")

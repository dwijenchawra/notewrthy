import cockroachdb

def create_account():
    # Get user's information
    username = input("Enter a new username: ")
    password = input("Enter a new password: ")

    # Connect to the CockroachDB database
    try:
        conn = cockroachdb.connect(
            host='localhost',
            port=2424,
            user='username',
            password='password',
            database='users'
        )
        cursor = conn.cursor()
    except cockroachdb.Error as e:
        print(f'Error connecting to CockroachDB: {e}')
        return

    # Insert the new account into the database
    query = f"INSERT INTO users (username, password) VALUES('{username}', '{password}')"
    try:
        cursor.execute(query)
        conn.commit()
        print("Account created successfully!")
    except cockroachdb.Error as e:
        print(f'Error creating account: {e}')
    finally:
        cursor.close()
        conn.close()

def login():
    # Get user's login information
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    # Connect to the CockroachDB database
    try:
        conn = cockroachdb.connect(
            host='localhost',
            port=2424,
            user='username',
            password='password',
            database='users'
        )
        cursor = conn.cursor()
    except cockroachdb.Error as e:
        print(f'Error connecting to CockroachDB: {e}')
        return

    # Check if the login information is correct
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        print("Welcome back!")
    else:
        print("Invalid login information.")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    while True:
        print("1. Login")
        print("2. Create an account")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            login()
        elif choice == "2":
            create_account()
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")

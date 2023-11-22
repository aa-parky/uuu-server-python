import bcrypt
import random
import string
import re
from mysql.connector import Error
from database import create_db_connection

async def register_user(websocket, db_config):
    # Loop for email validation
    while True:
        await websocket.send("Enter email address for registration:")
        email = await websocket.recv()

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            await websocket.send("Invalid email format. Please enter a valid email address.")
            continue

        # Check for blank email
        if not email.strip():
            await websocket.send("Email cannot be blank. Please enter a valid email address.")
            continue

        connection = create_db_connection(db_config)
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
            existing_email = cursor.fetchone()

            if existing_email:
                await websocket.send("Email already exists. Did you forget your password?")
                cursor.close()
                connection.close()
                return False

            # Break the loop if email validation is successful
            break

    # Loop for username validation
    while True:
        await websocket.send("Enter a username for registration (this is NOT your character name):")
        username = await websocket.recv()

        # Check for blank username
        if not username.strip():
            await websocket.send("Username cannot be blank. Please enter a valid username.")
            continue

        # Check if username already exists
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        existing_username = cursor.fetchone()

        if existing_username:
            await websocket.send("Username already exists. Please choose a different one.")
            continue

        # Break the loop if username validation is successful
        break

    # Proceed with registration using validated email and username
    try:
        # Generate a random password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Insert the new user with the hashed password into the database
        cursor.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)",
                       (email, username, hashed_password))
        connection.commit()
        cursor.close()
        connection.close()

        await websocket.send(f"Registration successful. Your username is '{username}' and your password is '{password}'.")
        return True
    except Error as e:
        print(f"Database error: {e}")
        return False

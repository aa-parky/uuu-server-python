import random
import string
from mysql.connector import Error
from database import create_db_connection


async def register_user(websocket, db_config):
    await websocket.send("Enter email address for registration:")
    email = await websocket.recv()

    connection = create_db_connection(db_config)
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
            existing_email = cursor.fetchone()
            cursor.close()

            if existing_email:
                await websocket.send("Email already exists. Did you forget your password?")
                return False
            else:
                await websocket.send("Enter a username for registration (this is NOT your character name):")
                username = await websocket.recv()
                # You can add more registration steps here if needed

                # Generate a random password
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

                # Insert the new user into the database
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)",
                               (email, username, password))
                connection.commit()
                cursor.close()
                connection.close()

                await websocket.send("Registration successful. Your username and password have been created.")
                return True
        except Error as e:
            print(f"Database error: {e}")
            return False
    else:
        return False

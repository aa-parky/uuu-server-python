import bcrypt
import random
import string
import re
from mysql.connector import Error
from database import create_db_connection
from connections import connected_users  # Import the connected_users dictionary


async def check_credentials(websocket, db_config):
    await websocket.send("Enter username:")
    username = await websocket.recv()
    if not username.strip():
        await websocket.send("Username cannot be blank.")
        return False, None

    await websocket.send("Enter password:")
    password = await websocket.recv()
    if not password.strip():
        await websocket.send("Password cannot be blank.")
        return False, None

    connection = create_db_connection(db_config)
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            user_password_hash = cursor.fetchone()
            cursor.close()

            if user_password_hash is not None:
                authenticated = bcrypt.checkpw(password.encode(), user_password_hash[0].encode())
                if authenticated:
                    connected_users[username] = websocket  # Add the user to the connected users
                    return True, username
                else:
                    await websocket.send("Incorrect username or password.")
                    return False, None
            else:
                await websocket.send("Incorrect username or password.")
                return False, None
    except Error as e:
        print(f"Database error: {e}")
        await websocket.send("An error occurred. Please try again later.")
        return False, None
    finally:
        if connection:
            connection.close()


async def register_user(websocket, db_config):
    # Loop for email validation
    while True:
        await websocket.send("Enter email address for registration:")
        email = await websocket.recv()

        # Validate email format and check for blank email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email) or not email.strip():
            await websocket.send("Invalid or blank email format. Please enter a valid email address.")
            continue

        connection = create_db_connection(db_config)
        try:
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
                existing_email = cursor.fetchone()

                if existing_email:
                    await websocket.send("Email already exists. Did you forget your password?")
                    return False

                # Break the loop if email validation is successful
                break
        except Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

    # Loop for username validation
    while True:
        await websocket.send("Enter a username for registration:")
        username = await websocket.recv()

        if not username.strip():
            await websocket.send("Username cannot be blank. Please enter a valid username.")
            continue

        connection = create_db_connection(db_config)
        try:
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
                existing_username = cursor.fetchone()

                if existing_username:
                    await websocket.send("Username already exists. Please choose a different one.")
                    continue

                # Break the loop if username validation is successful
                break
        except Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

    # Proceed with registration using validated email and username
    try:
        connection = create_db_connection(db_config)
        if connection:
            # Generate a random password and hash it
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)",
                           (email, username, hashed_password))
            connection.commit()

            await websocket.send(f"Registration successful. Your username is '{username}' and your "
                                 f"password is '{password}'.")
            return True
    except Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        cursor.close()
        connection.close()


async def handle_authentication(websocket, db_config, registration_enabled):
    await websocket.send("Type 'login' to login or 'register' to create a new account.")
    command = await websocket.recv()

    if command.lower() == 'login':
        auth_status, username = await check_credentials(websocket, db_config)
        return auth_status, 'login', username
    elif command.lower() == 'register' and registration_enabled:
        reg_status = await register_user(websocket, db_config)
        return reg_status, 'register', None
    else:
        await websocket.send("Unrecognized command. Type 'login' to login or 'register' to create a new account.")
        return False, 'unknown', None

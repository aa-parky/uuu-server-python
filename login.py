"""
This module provides functionalities for user authentication and registration,
including checking credentials and handling new user registrations.
"""
import random
import string
import re
import bcrypt
from mysql.connector import Error
from database import create_db_connection
from connections import connected_users  # Import the connected_users dictionary


async def check_credentials(websocket, db_config):
    """
    Check the provided credentials against the database.

    Args:
        websocket (WebSocket): The WebSocket connection for user interaction.
        db_config (dict): Configuration details for the database connection.

    Returns:
        tuple: A tuple containing a boolean indicating authentication success,
        and the username if authentication is successful, otherwise None.
    """

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

    connection = None
    try:
        connection = create_db_connection(db_config)
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

    except Error as e:
        print(f"Database error: {e}")
        await websocket.send("An error occurred. Please try again later.")
    finally:
        if connection:
            connection.close()

    # Moved the return statement outside the if block
    await websocket.send("Incorrect username or password.")
    return False, None


async def register_user(websocket, db_config):
    """
       Register a new user by validating their email and username, and then inserting
       their details into the database.

       This function performs a loop for email validation, ensuring the email is in
       the correct format and not already registered in the database. It then
       validates the username in a similar manner. Upon successful validation of both,
       it generates a random password, hashes it, and inserts the new user's details
       into the database. The user is then informed of their registration success
       along with their new username and password.

       Args:
           websocket (WebSocket): The WebSocket connection for user interaction.
           db_config (dict): Configuration details for the database connection.

       Returns:
           bool: True if the registration was successful, False otherwise.

       Raises:
           Error: If there is a database-related error during user registration.
       """
    cursor = None
    connection = None
    try:
        # Loop for email validation
        while True:
            await websocket.send("Enter email address for registration:")
            email = await websocket.recv()

            # Validate email format and check for blank email
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email) or not email.strip():
                await websocket.send("Invalid or blank email format. "
                                     "Please enter a valid email address.")
                continue

            connection = create_db_connection(db_config)
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
                existing_email = cursor.fetchone()

                if existing_email:
                    await websocket.send("Email already exists. Did you forget your password?")
                    return False

                # Break the loop if email validation is successful
                break

        # Loop for username validation
        while True:
            await websocket.send("Enter a username for registration:")
            username = await websocket.recv()

            if not username.strip():
                await websocket.send("Username cannot be blank. Please enter a valid username.")
                continue

            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            existing_username = cursor.fetchone()

            if existing_username:
                await websocket.send("Username already exists. Please choose a different one.")
                continue

            # Break the loop if username validation is successful
            break

        # Proceed with registration using validated email and username
        # Generate a random password and hash it
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        cursor.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)",
                       (email, username, hashed_password))
        connection.commit()

        await websocket.send(f"Registration successful. Your username is '{username}' "
                             f"and your password is '{password}'.")
        return True

    except Error as e:
        print(f"Database error: {e}")
        return False

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


async def handle_authentication(websocket, db_config, registration_enabled):
    """
       Handles user authentication and registration based on user input.

       This function first prompts the user to choose between logging in and
       registering. Based on the user's response, it either calls the function to
       check credentials (for login) or to register a new user (for registration).
       The function ensures that registration is only attempted if it's enabled.
       If the user enters an unrecognized command, they are informed and the function
       returns a status indicating an unknown command.

       Args:
           websocket (WebSocket): The WebSocket connection for user interaction.
           db_config (dict): Configuration details for the database connection.
           registration_enabled (bool): Flag indicating if new user registration is allowed.

       Returns:
           tuple: A tuple containing a boolean indicating the success of the action,
                  a string indicating the action taken ('login', 'register', 'unknown'),
                  and the username (if login was successful) or None.
       """
    await websocket.send("Type 'login' to login or 'register' to create a new account.")
    command = await websocket.recv()

    # pylint: disable=no-else-return
    if command.lower() == 'login':
        auth_status, username = await check_credentials(websocket, db_config)
        return auth_status, 'login', username
    elif command.lower() == 'register' and registration_enabled:
        reg_status = await register_user(websocket, db_config)
        return reg_status, 'register', None
    else:
        await websocket.send("Unrecognized command. Type 'login' to login or "
                             "'register' to create a new account.")
        return False, 'unknown', None

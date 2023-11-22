import bcrypt
from mysql.connector import Error
from database import create_db_connection


async def check_credentials(websocket, db_config):
    await websocket.send("Enter username:")
    username = await websocket.recv()
    await websocket.send("Enter password:")
    password = await websocket.recv()

    connection = create_db_connection(db_config)
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            user_password_hash = cursor.fetchone()
            cursor.close()
            connection.close()

            # Verify the password
            if user_password_hash is not None:
                return bcrypt.checkpw(password.encode(), user_password_hash[0].encode())

            return False

        except Error as e:
            print(f"Database error: {e}")
            return False
    else:
        return False

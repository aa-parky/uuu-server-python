import configparser


# Function to load the message of the day (MOTD) from file
import configparser
import textwrap

# Function to load the message of the day (MOTD) from file
def load_motd():
    config = configparser.ConfigParser()
    config.read('config.ini')
    motd_file = config['Messages']['motd_file']
    try:
        with open(motd_file, 'r') as file:
            motd_text = file.read()
            # Add a newline character at the beginning
            motd_text = '\n' + motd_text
            # Use textwrap to justify the text
            motd_text = textwrap.fill(motd_text, width=80)
            return motd_text
    except FileNotFoundError:
        return "MOTD file not found."



# Function to display MOTD to the client
async def display_motd(websocket):
    config = configparser.ConfigParser()
    config.read('config.ini')
    motd_enabled = config.getboolean('Settings', 'MOTD')

    if motd_enabled:
        motd = load_motd()
        await websocket.send(motd)
    else:
        await websocket.send("Welcome to the Lobby")

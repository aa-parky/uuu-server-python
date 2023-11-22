
# Function to display a welcome message to the lobby
async def display_motd(websocket):
    await websocket.send("Welcome to the Lobby")

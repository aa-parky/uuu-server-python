# uuu-server-python
_A simple python websockets server_


### server_auth.py

This script is the entry point for the WebSocket server. It handles the initialization of WebSocket connections and delegates command processing to the ContextManager.

#### load_config Function:

Reads the configuration settings from config.ini.
Retrieves settings related to registration, message of the day (MOTD), database configuration, SSL settings, server configuration, and messages.

#### server_handler Async Function:

This is the main handler for incoming WebSocket connections.

It creates an instance of **ContextManager**, passing necessary configurations such as _db_config_, _registration_, and _messages_.
Sets the initial context for the connection (e.g., 'c_server_auth') and manages the communication loop, receiving messages from the client and delegating command handling to the ContextManager.

#### start_server Async Function:

1. Sets up and starts the WebSocket server.
2. Uses SSL configuration for secure connections.
3. Listens for incoming connections and passes them to server_handler.
Running the Server:

The script starts the server by calling **asyncio.run(start_server())**.

### context_manager.py
The ContextManager class manages the current context of a user's session and delegates command handling to the appropriate context class.

#### Initialization:

ContextManager is initialized with a WebSocket object, database configuration (_db_config_), registration status (_registration_enabled_), and message configurations (_messages_).

#### set_context Async Method:

1. Dynamically loads a context class based on the given context name.
2. Instantiates the context class with necessary configurations.
3. Calls the send_greeting method of the context class if available, to send an initial greeting message to the client.

#### handle_command Async Method:

Delegates the received command to the current context's handle_command method.

This modular approach allows different contexts to handle commands specific to their functionality. **IMHO**

### c_server_auth.py & CServerAuth Class 

This class represents the server authentication context and is responsible for handling commands related to user authentication and initial interaction.

Basically allowing the user upon connection to either login or register and account (if the _config.ini_ is Registration = True)

##### Initialization:

The __init__ method initializes the CServerAuth class with the WebSocket connection (_websocket_), database configuration (_db_config_), registration enabling status (_registration_enabled_), and message templates (_messages_).

#### send_greeting Async Method:

Sends a greeting message to the client upon connecting. The message varies based on whether registration is enabled or not. This method is called immediately after the context is set in the _ContextManager_.

#### handle_command Async Method:

Handles various commands received from the client:

1. Blank Command: If the command is blank, it prompts the user to enter a command or type 'help' for available commands.
2. 'login' Command: Processes the login attempt using check_credentials. On success, sends a "Login successful" message; on failure, sends "Login failed".
3. 'register' Command: If registration is enabled, processes user registration using register_user.
4. 'help' Command: Provides information on available commands (login or register).
5. Other/Unrecognized Commands: Informs the user that the command is unrecognized and advises typing 'help' for available commands.

#### Error Handling:

Includes a _try-except block_ to catch and log any exceptions that occur during command handling, ensuring robust error handling and logging of potential issues.

#### Usage in the Application

##### CServerAuth as Initial Context:

In the WebSocket server setup (_server_auth.py_), *CServerAuth* is set as the initial context for new connections. This means that all commands received from newly connected clients are first processed by *CServerAuth*.

##### Transitioning Contexts: 

After handling initial authentication and registration, you can extend *CServerAuth* to transition to other contexts based on user actions, such as successfully logging in.

This structure allows *CServerAuth* to specifically handle the authentication phase of client interaction, keeping this logic separate from other parts of the application. Such separation of concerns enhances the modularity and maintainability of code. **IMHO**







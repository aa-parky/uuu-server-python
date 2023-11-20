<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WebSocket Client</title>
</head>
<body>
    <h2>WebSocket Client</h2>
    <div id="messageBox"></div>
    <input type="text" id="inputField" placeholder="Enter command" style="display: none;">
    <button id="sendButton" style="display: none;">Send</button>

    <script>
        var socket;
        var messageBox = document.getElementById('messageBox');
        var inputField = document.getElementById('inputField');
        var sendButton = document.getElementById('sendButton');

        function connectWebSocket() {
            // Configure the SSL context to accept self-signed certificates
            socket = new WebSocket("wss://localhost:7450", null, null, { rejectUnauthorized: false });

            socket.onopen = function() {
                console.log("Connected to the WebSocket server");
            };

            socket.onmessage = function(event) {
                console.log("Received message from server: " + event.data);
                messageBox.innerText = event.data;
                inputField.style.display = 'block';
                sendButton.style.display = 'block';

                // Check if the message includes 'Register' to enable registration
                if (event.data.includes('Register')) {
                    inputField.placeholder = 'Enter command (login or register)';
                } else {
                    inputField.placeholder = 'Enter command (login)';
                }
            };

            socket.onerror = function(error) {
                console.error('WebSocket Error: ' + error);
            };

            socket.onclose = function(event) {
                console.log("WebSocket is closed now.");
            };
        }

        function sendMessage() {
            var message = inputField.value;
            socket.send(message);
            inputField.value = '';
        }

        window.onload = connectWebSocket;
        sendButton.onclick = sendMessage;
    </script>
</body>
</html>

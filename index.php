<html ng-app="app">
<head>
    <script type="text/javascript">

    var myWebSocket;


    function connectToWS() {
        var endpoint = document.getElementById("endpoint").value;
        if (myWebSocket !== undefined) {
            myWebSocket.close()
        }

        myWebSocket = new WebSocket(endpoint);

        myWebSocket.onmessage = function(event) {
            var leng;
            if (event.data.size === undefined) {
                leng = event.data.length
            } else {
                leng = event.data.size
            }
            console.log("onmessage. size: " + leng + ", content: " + event.data);
        }

        myWebSocket.onopen = function(evt) {
            console.log("onopen.");
        };

        myWebSocket.onclose = function(evt) {
            console.log("onclose.");
        };

        myWebSocket.onerror = function(evt) {
            console.log("Error!");
        };
    }

    function sendMsg() {
        var message = document.getElementById("myMessage").value;
        myWebSocket.send(message);
    }

    function closeConn() {
        myWebSocket.close();
    }

    </script>
</head>
<body>

    <form>
        connection to: <input type="text" id="endpoint" name="endpoint" value="wss://undermine-undertakers.uk:7450"  style="width: 200px" ><br>
    </form>

    <input type="button" onclick="connectToWS()" value="connect to WebSocket endpoint" /><br><br>

    <form>
        message: <input type="text" id="myMessage" name="myMessage" value="hi there!"><br>
    </form>

    <input type="button" onclick="sendMsg()" value="Send message" />

    <input type="button" onclick="closeConn()" value="Close connection" />


</body>
</html>
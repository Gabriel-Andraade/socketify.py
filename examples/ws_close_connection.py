from socketify import App, AppOptions, OpCode, CompressOptions  # Import necessary classes from the socketify package

def ws_open(ws):
    # Function called when a WebSocket connection is enable
    print("A WebSocket got connected!")  # show connection message 
    ws.send("Hello World!", OpCode.TEXT)  # Send initial message 

def ws_message(ws, message, opcode):
    # call when a message is received
    print(message, opcode)  # show the received message 
    if message == 'close':  # Check if the received message is 'close'
        ws.close()  # Close the WebSocket connection
    else:
        # Attempt to send the message back to the client, checking for backpressure
        ok = ws.send(message, opcode)  # atempt to send message back to the client 

app = App()  # Create an instance of the application

app.ws(
    "/*",  # Route that accepts any endpoint
    {
        "compression": CompressOptions.SHARED_COMPRESSOR,  # Enable compression
        "max_payload_length": 16 * 1024 * 1024,  # Set the max payload size
        "idle_timeout": 12,  # Set the max time
        "open": ws_open,  # set the function to connection opens
        "message": ws_message,  # Function to call when a message is received
        "drain": lambda ws: print(  # set a callback for backpressure
            "WebSocket backpressure: %s", ws.get_buffered_amount()  # Show the buffered amount of data
        ),
        "close": lambda ws, code, message: print("WebSocket closed"),  # Function called when the connection closes
    },
)

# Respond with a message for requests to the root
app.any("/", lambda res, req: res.end("Nothing to see here!"))

app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)

app.run()

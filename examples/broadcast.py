from socketify import App, AppOptions, OpCode, CompressOptions


def ws_open(ws):
    print("A WebSocket got connected!") # show amessage when one conection WebSocket is set
    # Let this client listen to topic "broadcast"
    ws.subscribe("broadcast")


def ws_message(ws, message, opcode): # Show the message for  wall clients in topic "Broadcast"
    # Broadcast this message
    ws.publish("broadcast", message, opcode) 

app = App()
app.ws(
    "/*", # Define this application for all routes
    {
        "compression": CompressOptions.SHARED_COMPRESSOR,
        "max_payload_length": 16 * 1024 * 1024, # Max size of payload
        "idle_timeout": 60, #   Max time 
        "open": ws_open, # Define the function to be called when opening a connection
        "message": ws_message, # Define the function to be called when receiving a message
        # The library guarantees proper unsubscription at close
        "close": lambda ws, code, message: print("WebSocket closed"), # Show a message when closed the connection
        "subscription": lambda ws, topic, subscriptions, subscriptions_before: print(f'subscription/unsubscription on topic {topic} {subscriptions} {subscriptions_before}'),
        # Register change of inscription
    },
)
app.any("/", lambda res, req: res.end("Nothing to see here!"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()

from socketify import App, AppOptions, OpCode, CompressOptions

# Number between ok and not ok
backpressure = 1024

# Used for statistics
messages = 0
message_number = 0


def ws_open(ws):
    print("A WebSocket got connected!")
    # We begin our example by sending until we have backpressure
    global message_number
    global messages
    while ws.get_buffered_amount() < backpressure:
        ws.send("This is a message, let's call it %i" % message_number)
        message_number = message_number + 1
        messages = messages + 1


def ws_drain(ws):
    # Continue sending when we have drained (some)
    global message_number
    global messages
    while ws.get_buffered_amount() < backpressure:
        ws.send("This is a message, let's call it %i" % message_number)
        message_number = message_number + 1
        messages = messages + 1
    # This function is called all time when buffer is empty,allowing the server for sending message again until the limit

app = App()
app.ws(
    "/*",
    {
        "compression": CompressOptions.DISABLED,
        "max_payload_length": 16 * 1024 * 1024, # Max size payload
        "idle_timeout": 60, # Max time 
        "open": ws_open, # Define the open event
        "drain": ws_drain, # Define the drain event
    },
)
app.any("/", lambda res, req: res.end("Nothing to see here!"))
    # Define one route for all other request, it sends a message 
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()

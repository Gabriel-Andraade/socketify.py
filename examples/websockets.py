from socketify import App, AppOptions, OpCode, CompressOptions


def ws_open(ws): 
    # function called when a websocket connection is enable
    print("A WebSocket got connected!") # show connection message
    ws.send("Hello World!", OpCode.TEXT) # send initial message


def ws_message(ws, message, opcode): 
    # call when a message is received
    print(message, opcode) # show the received message 
    # Ok is false if backpressure was built up, wait for drain
    ok = ws.send(message, opcode) # attempt to send message back to the client


app = App() # create an intance of the application 


app.ws(
    
    "/*",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR, # enable compression
        "max_payload_length": 16 * 1024 * 1024, # set max size payload
        "idle_timeout": 12, # set max time
        "open": ws_open, # set the function to connected open
        "message": ws_message, # set function to call when received a message
        "drain": lambda ws: print( # set a csllbsck for backpressure
            "WebSocket backpressure: %s", ws.get_buffered_amount() # show the buffered amount of data
        ),
        "close": lambda ws, code, message: print("WebSocket closed"), # function called when the connection closes
    },
)
    # respond a message for request to the root
app.any("/", lambda res, req: res.end("Nothing to see here!'"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()

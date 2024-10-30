from socketify import App, AppOptions, OpCode, CompressOptions

    # is called when websckot client can conected, sending a message 
def ws_open(ws):
    print("A WebSocket got connected!")
    ws.send("Hello World!", OpCode.TEXT)

    # handle with receive message
def ws_message(ws, message, opcode):
    print(message, opcode)
    # Ok is false if backpressure was built up, wait for drain
    ok = ws.send(message, opcode)

    # handles the update process upon reiceiving specific request headers
def ws_upgrade(res, req, socket_context):
    key = req.get_header("sec-websocket-key")
    protocol = req.get_header("sec-websocket-protocol")
    extensions = req.get_header("sec-websocket-extensions")
    res.upgrade(key, protocol, extensions, socket_context)


app = App()
app.ws(
    "/*",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR, # configure compression 
        "max_payload_length": 16 * 1024 * 1024, # give the max size of payload
        "idle_timeout": 12, # give thetime before clossing
        "open": ws_open, # call ws_open when open conecting 
        "message": ws_message, # handle message
        "upgrade": ws_upgrade, # manage the update of websocket
        "drain": lambda ws: print( # here the function show backpressure
            "WebSocket backpressure: %s", ws.get_buffered_amount()
        ),
        "close": lambda ws, code, message: print("WebSocket closed"),
    },
)
    # set standard response for other request
app.any("/", lambda res, req: res.end("Nothing to see here!"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()

from socketify import App, AppOptions, OpCode, CompressOptions
import asyncio


def ws_open(ws):
    print("A WebSocket got connected!")
    ws.send("Hello World!", OpCode.TEXT)

 # function for read the sended message
def ws_message(ws, message, opcode):
    print(message, opcode)
    # Ok is false if backpressure was built up, wait for drain
    ok = ws.send(message, opcode)

 # function to manage websocket protocol update 
async def ws_upgrade(res, req, socket_context):
        # header for websocket conection
    key = req.get_header("sec-websocket-key")
    protocol = req.get_header("sec-websocket-protocol")
    extensions = req.get_header("sec-websocket-extensions")
    await asyncio.sleep(2) # stop for 2 seconds to simulate an async process
    res.upgrade(key, protocol, extensions, socket_context)


app = App()
app.ws(
    "/*",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR, # configure the compression
        "max_payload_length": 16 * 1024 * 1024, # give the max size of payload
        "idle_timeout": 12, # give the max time before closing 
        "open": ws_open, # call ws_open when open conection
        "message": ws_message, # handle message
        "upgrade": ws_upgrade, # manages the update of websocket
        "drain": lambda ws: print( # function to show backpressure
            "WebSocket backpressure: %s", ws.get_buffered_amount()
        ),
        "close": lambda ws, code, message: print("WebSocket closed"),
    },
)
    # set standard response for other requests
app.any("/", lambda res, req: res.end("Nothing to see here!"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()

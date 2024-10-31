from socketify import App, AppOptions, OpCode, CompressOptions

    # É chamado qunando o cliente websocket pode ser conectado, enviando uma mensagem
def ws_open(ws):
    print("A WebSocket got connected!")
    ws.send("Hello World!", OpCode.TEXT)

    # Manuseia com mensagem recebida
def ws_message(ws, message, opcode):
    print(message, opcode)
    # Ok é false se a backpressure foi criada, aguarde o drain
    ok = ws.send(message, opcode)

    # Manuseia o processo de atualização ao receber o header de solicitação específico
def ws_upgrade(res, req, socket_context):
    key = req.get_header("sec-websocket-key")
    protocol = req.get_header("sec-websocket-protocol")
    extensions = req.get_header("sec-websocket-extensions")
    res.upgrade(key, protocol, extensions, socket_context)


app = App()
app.ws(
    "/*",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR, # configura a compression
        "max_payload_length": 16 * 1024 * 1024, # Tamanho máximo do payload
        "idle_timeout": 12, # Tempo máximo
        "open": ws_open, # Define a função a ser chamada ao receber
        "message": ws_message, # manuseia a mensagem 
        "upgrade": ws_upgrade, # Gerencia a atualização do websocket
        "drain": lambda ws: print( # Aqui a função mostra a backpressure
            "WebSocket backpressure: %s", ws.get_buffered_amount()
        ),
        "close": lambda ws, code, message: print("WebSocket closed"),
    },
)
    # Define resposta padrão para outras solicitação 
app.any("/", lambda res, req: res.end("Nothing to see here!"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()

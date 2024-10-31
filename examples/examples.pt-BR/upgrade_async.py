from socketify import App, AppOptions, OpCode, CompressOptions
import asyncio


def ws_open(ws):
    print("A WebSocket got connected!")
    ws.send("Hello World!", OpCode.TEXT)

 # Função para ler a mensagem enviada
def ws_message(ws, message, opcode):
    print(message, opcode)
    # OK é falso se a backpressure foi criada, aguarda o drain
    ok = ws.send(message, opcode)

 # Função para gerenciar a atualização do protocolo websocket
async def ws_upgrade(res, req, socket_context):
        # Header para conexão websocket
    key = req.get_header("sec-websocket-key")
    protocol = req.get_header("sec-websocket-protocol")
    extensions = req.get_header("sec-websocket-extensions")
    await asyncio.sleep(2) # Pare por 2 para simular um processo async
    res.upgrade(key, protocol, extensions, socket_context)


app = App()
app.ws(
    "/*",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR,
        "max_payload_length": 16 * 1024 * 1024, # Tamanho máximo do payload
        "idle_timeout": 12, # Tempo máximo
        "open": ws_open, # Define a função a ser chamada ao receber
        "message": ws_message, # Manuseia a mensagem 
        "upgrade": ws_upgrade, # Gerencia a atualização do websocket
        "drain": lambda ws: print( # Função para mostrar a backpressure 
            "WebSocket backpressure: %s", ws.get_buffered_amount()
        ),
        "close": lambda ws, code, message: print("WebSocket closed"),
    },
)
    # Defina resposta padrão para outras solicitações 
app.any("/", lambda res, req: res.end("Nothing to see here!"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()

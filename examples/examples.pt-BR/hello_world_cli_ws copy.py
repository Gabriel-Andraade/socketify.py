from socketify import App, OpCode

def run(app: App): 
    # Adicione suas rotas aqui
    app.get("/", lambda res, req: res.end("Hello World!"))
    

# cli usará esta configuração para servir na rota "/*", você ainda pode usar .ws("/*", config) se quiser, mas as opções --ws* não terão efeito
websocket = {
    "open": lambda ws: ws.send("Hello World!", OpCode.TEXT),
    "message": lambda ws, message, opcode: ws.send(message, opcode),
    "close": lambda ws, code, message: print("WebSocket closed"),
}
# python -m socketify hello_world_cli_ws:run --ws hello_world_cli_ws:websocket --port 8080 --workers 2
# python3 -m socketify hello_world_cli_ws:run --ws hello_world_cli_ws:websocket--port 8080 --workers 2
# pypy3 -m socketify hello_world_cli_ws:run --ws hello_world_cli_ws:websocket--port 8080 --workers 2

# veja as opções usando no terminal: python3 -m socketify --help
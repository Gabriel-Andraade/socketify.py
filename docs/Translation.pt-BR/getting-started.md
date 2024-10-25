## começando.

Primeiro vamos instalar seguindo:[Installation Guide](installation.md).

Agora que temos tudo instalado, vamos dar uma olhada em uns exemplos rápido

Hello world app
```python
from socketify import App

def make_app(app: App):
    app.get("/", lambda res, req: res.end("Hello World socketify from Python!"))

if __name__ == "__main__":
    app = App()
    make_app(app)
    app.listen(3000, lambda config: print("Listening on port http://localhost:%d now\n" % config.port))
    app.run()
```
> Este exemplo mostra como é intuitivo iniciar um app simples, tipo Hello World

SSL amostra
``` python
from socketify import App, AppOptions

def make_app(app):
    app.get("/", lambda res, req: res.end("Hello World socketify from Python!"))

if __name__ == "__main__":
    app = App(AppOptions(key_file_name="./misc/key.pem", cert_file_name="./misc/cert.pem", passphrase="1234"))
    app.listen(3000, lambda config: print("Listening on port http://localhost:%d now\n" % config.port))
    app.run()
```

> Temos muitas opções de SSL, mas esta é a mais comum, você pode ver todas as opções na [API Reference](api.md)

WebSockets
```python
from socketify import App, AppOptions, OpCode, CompressOptions

def ws_open(ws):
    print('A WebSocket got connected!')
    ws.send("Hello World!", OpCode.TEXT)

def ws_message(ws, message, opcode):
    #Ok é false se a backpressure foi criada, aguarda odrain
    ok = ws.send(message, opcode)

def make_app(app):    
    app.ws("/*", {
        'compression': CompressOptions.SHARED_COMPRESSOR,
        'max_payload_length': 16 * 1024 * 1024,
        'idle_timeout': 12,
        'open': ws_open,
        'message': ws_message,
        'drain': lambda ws: print('WebSocket backpressure: %i' % ws.get_buffered_amount()),
        'close': lambda ws, code, message: print('WebSocket closed')
    })
    app.any("/", lambda res,req: res.end("Nothing to see here!'"))


if __name__ == "__main__":
    app = App()
    make_app(app)
    app.listen(3000, lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)))
    app.run()
```

> Podemos ter várias rotas para Websockets `SHARED_COMPRESSOR`, `max_payload_length` de 1MB e um tempo limite ocioso de 12s apenas mostrando alguns recursos mais comumentes usados, você pode ver todas essas opções na [API Reference](api.md)


Se você quiser ver mais alguns exemplos, pode ir para nossa[examples folder](https://github.com/cirospaciari/socketify.py/tree/main/examples) para mais de 25 exemplos.

### próximo [Corking Concept](corking.md)

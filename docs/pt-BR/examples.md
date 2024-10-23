# Exemplos

Middleware
```python
from socketify import App, middleware


async def get_user(authorization):
    if authorization:
        # Você pode fazer algum async aqui
        return {"greeting": "Hello, World"}
    return None


async def auth(res, req, data=None):
    user = await get_user(req.get_header("authorization"))
    if not user:
        res.write_status(403).end("not authorized")
        # Retornando Falsy em middlewares, apenas pare a execução do próximo middleware
        return False

    # Retorna datas extras
    return user


def another_middie(res, req, data=None):
    # Agora podemos misturar sync e async e alterar os dados aqui
    if isinstance(data, dict):
        gretting = data.get("greeting", "")
        data["greeting"] = f"{gretting} from another middie ;)"
    return data


def home(res, req, user=None):
    res.cork_end(user.get("greeting", None))


app = App()
app.get("/", middleware(auth, another_middie, home))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

# Você também pode fazer um loop no MiddlewareRouter no middleware_router.py ;)
```

Broadcast
```python
from socketify import App, AppOptions, OpCode, CompressOptions


def ws_open(ws):
    print("A WebSocket got connected!")
    # Deixe o cliente escutar o tópico "broadcast"
    ws.subscribe("broadcast")


def ws_message(ws, message, opcode):
    # transmita está mensagem
    ws.publish("broadcast", message, opcode)

app = App()
app.ws(
    "/*",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR,
        "max_payload_length": 16 * 1024 * 1024,
        "idle_timeout": 60,
        "open": ws_open,
        "message": ws_message,
        # A library garante o cancelamento de assinatura adequado no fechamento
        "close": lambda ws, code, message: print("WebSocket closed"),
        "subscription": lambda ws, topic, subscriptions, subscriptions_before: print(f'subscription/unsubscription on topic {topic} {subscriptions} {subscriptions_before}'),
    },
)
app.any("/", lambda res, req: res.end("Nothing to see here!"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()
```

HTTPS
```python
from socketify import App, AppOptions

app = App(
    AppOptions(
        key_file_name="./misc/key.pem",
        cert_file_name="./misc/cert.pem",
        passphrase="1234",
    )
)
app.get("/", lambda res, req: res.end("Hello World socketify from Python!"))
app.listen(
    54321,
    lambda config: print("Listening on port https://localhost:%d now\n" % config.port),
)
app.run()

# mkdir misc
# openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -passout pass:1234 -keyout ./misc/key.pem -out ./misc/cert.pem
```

Backpressure
```python
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


app = App()
app.ws(
    "/*",
    {
        "compression": CompressOptions.DISABLED,
        "max_payload_length": 16 * 1024 * 1024,
        "idle_timeout": 60,
        "open": ws_open,
        "drain": ws_drain,
    },
)
app.any("/", lambda res, req: res.end("Nothing to see here!"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()
```

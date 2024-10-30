from socketify import App, AppOptions, OpCode, CompressOptions

# Número entre ok e não ok
backpressure = 1024

# Usado para estatísticas
messages = 0
message_number = 0


def ws_open(ws):
    print("A WebSocket got connected!")
    
    # Começamos nosso exemplo enviando até termos backpressure
    global message_number
    global messages
    while ws.get_buffered_amount() < backpressure:
        ws.send("This is a message, let's call it %i" % message_number)
        message_number = message_number + 1
        messages = messages + 1


def ws_drain(ws):
    
    # Continuar enviando quando tivermos drenado (algumas)
    global message_number
    global messages
    while ws.get_buffered_amount() < backpressure:
        ws.send("This is a message, let's call it %i" % message_number)
        message_number = message_number + 1
        messages = messages + 1
        
    # Esta função é chamada sempre que o buffer estiver vazio, permitindo que o servidor envie mensagens novamente até o limite

app = App()
app.ws(
    "/*",
    {
        "compression": CompressOptions.DISABLED,
        "max_payload_length": 16 * 1024 * 1024, # Tamanho máximo do payload
        "idle_timeout": 60, # Tempo máximo 
        "open": ws_open, # Defina o evento de abertura
        "drain": ws_drain, # Defina o evento de drenagem
    },
)
app.any("/", lambda res, req: res.end("Nothing to see here!"))

    # Defina uma rota para todas as outras request, ela envia uma mensagem  
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()

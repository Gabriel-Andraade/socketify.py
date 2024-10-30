from socketify import App, AppOptions, OpCode, CompressOptions


def ws_open(ws):
    print("A WebSocket got connected!") # Mostrar uma mensagem quando uma conexão WebSocket for definida
    # Deixar este cliente ouvir o tópico "broadcast"
    ws.subscribe("broadcast")


def ws_message(ws, message, opcode): # Mostrar a mensagem para clientes de parede no tópico "Broadcast"
    # Broadcast this message
    ws.publish("broadcast", message, opcode) 

app = App()
app.ws(
    "/*", # Definir esta aplicação para todas as rotas
    {
        "compression": CompressOptions.SHARED_COMPRESSOR,
        "max_payload_length": 16 * 1024 * 1024, # Tamanho máximo do payload
        "idle_timeout": 60, # Tempo máximo
        "open": ws_open, # Defina a função a ser chamada ao receber 
        "message": ws_message, # Defina a função a ser chamada ao receber uma mensagem
        # A biblioteca garante o cancelamento de inscrição adequado ao  fechar 
        "close": lambda ws, code, message: print("WebSocket closed"), # Exiba uma mensagem ao fechar a conexão 
        "subscription": lambda ws, topic, subscriptions, subscriptions_before: print(f'subscription/unsubscription on topic {topic} {subscriptions} {subscriptions_before}'),
        # Registre a alteração da inscrição 
    },
)
app.any("/", lambda res, req: res.end("Nothing to see here!"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()

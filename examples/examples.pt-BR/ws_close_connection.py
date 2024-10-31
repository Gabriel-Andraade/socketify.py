from socketify import App, AppOptions, OpCode, CompressOptions  # Importa classes necessárias do pacote socketify

def ws_open(ws):
    # Função chamada quando uma conexão WebSovket é habilitada
    print("A WebSocket got connected!")  # Mostra mensagem de conexão  
    ws.send("Hello World!", OpCode.TEXT)  # Manda mensagem inicial

def ws_message(ws, message, opcode):
    # Chama quando uma mensagem é recebida 
    print(message, opcode)  # Mostra a mensagem recebida 
    if message == 'close':  # Verifica se a mensagem recebida é "close"
        ws.close()  # Fecha a conexão WebSocket
    else:
        # Tenta enviar a mensagem de volta ao cliente, verificando a backpressure
        ok = ws.send(message, opcode)  # Tenta enviar a mensagem de volta ao cliente 

app = App()  # Cria uma instância do aplicativo

app.ws(
    "/*",  # Rota que aceita qualquer ponto final
    {
        "compression": CompressOptions.SHARED_COMPRESSOR,  # ativa a compression
        "max_payload_length": 16 * 1024 * 1024,  # Tamanho máximo do upload
        "idle_timeout": 12,  # Tempo máximo
        "open": ws_open,  # Define a função para abrir conexão
        "message": ws_message,  # Função a ser chamada quando uma mensagem for recebida
        "drain": lambda ws: print(  # Define um callback para backpressure
            "WebSocket backpressure: %s", ws.get_buffered_amount()  # Mostra a quantidade de dados armazenados em buffer
        ),
        "close": lambda ws, code, message: print("WebSocket closed"),  # Função chamada quando a conexão for fechada
    },
)

# Responder com uma mensagem para solicitações à raiz
app.any("/", lambda res, req: res.end("Nothing to see here!"))

app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)

app.run()

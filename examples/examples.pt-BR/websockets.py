from socketify import App, AppOptions, OpCode, CompressOptions


def ws_open(ws): 
    # Função chamada quando uma conexão websoket é habilitada
    print("A WebSocket got connected!") # Mostra mensagem de conexão
    ws.send("Hello World!", OpCode.TEXT) # AEnvia mensagem inicial


def ws_message(ws, message, opcode): 
    # Chama quando uma mensagem é recebida 
    print(message, opcode) # Mostra a mensagem recebida 
    # Ok é false se a backpressure foi criada, espere o drain
    ok = ws.send(message, opcode) # Tenta enviar mensagem de volta para o cliente


app = App() # Cria uma instância do aplicativo


app.ws(
    
    "/*",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR, # Configura a compression 
        "max_payload_length": 16 * 1024 * 1024, # Tamanho máximo do payload
        "idle_timeout": 12, # Tempo máximo
        "open": ws_open, # Define a função a ser chamada ao receber 
        "message": ws_message, # Define a função para chamar quando receber uma mensagem
        "drain": lambda ws: print( # Define a callback para backpressure
            "WebSocket backpressure: %s", ws.get_buffered_amount() # Mostra a quantidade de dados armazenados em buffer
        ),
        "close": lambda ws, code, message: print("WebSocket closed"), # Função chamada quando a conexão fecha
    },
)
    # Responde uma mensagem para a solicitação à raiz
app.any("/", lambda res, req: res.end("Nothing to see here!'"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()

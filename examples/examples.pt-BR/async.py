from socketify import App, AppOptions, AppListenOptions
import asyncio

app = App()


async def delayed_hello(delay, res):
    await asyncio.sleep(delay)  # Faça algo async
    res.cork_end("Hello with delay!") # Envie a resposta ao cliente


def home(res, req):
    # O request object só se mantem durante esse momento
    # Pega parameters, query, headers tudo que você precisa está aqui!
    delay = req.get_query("delay")
    delay = 0 if delay == None else float(delay)
    # Diga à resposta para executar isso no loop de eventos
    # O abort handler é capturado aqui, então as respostas só serão enviadas se  res.aborted == False
    res.run_async(delayed_hello(delay, res))
    # Executa "delayed_hello" no modo async

async def json(res, req):
    # Request object só dura o tempo dessa chamada
    # Obtém parameters, query, headers e tudo mais um pouco que você precisa antes do primeiro awit:)
    user_agent = req.get_header("user-agent")
    # Talvez async não esteja disponível em funções async anexadas diretamente após await  
    await asyncio.sleep(2)  # Faz algum async

    res.cork_end({"message": "I'm delayed!", "user-agent": user_agent})
        # Esta resposta com Json

def not_found(res, req):
    res.write_status(404).end("Not Found")  # Retorna erro 404 para rotas que não encontramos 


app.get("/", home)  # Rota nomeada de "/" chamada de 'home'
app.get("/json", json)  # Rota nomeada  "/json" chamada de 'json'
app.any("/*", not_found)    # todas as rotas retornam o erro 404

    # aqui é a configuração do servidor para testar 
app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)

app.run()

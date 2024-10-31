from socketify import App, AppOptions, AppListenOptions
import asyncio
from datetime import datetime, timedelta

app = App()


def home(res, req):
    res.end("Hello :)")


def anything(res, req):
    res.end("Any route with method: %s" % req.get_method())


def cookies(res, req):
    # Cookies são gravados após o fim
    res.set_cookie(
        "spaciari",
        "1234567890",
        {
            # expires
            # path
            # comment
            # domain
            # max-age
            # secure
            # version
            # httponly
            # samesite
            "path": "/",
            # "domain": "*.test.com",
            "httponly": True,
            "samesite": "None",
            "secure": True,
            "expires": datetime.utcnow() + timedelta(minutes=30),
        },
    )
    res.end("Your session_id cookie is: %s" % req.get_cookie("session_id"))

    # Mostra o tipo de usuário
def useragent(res, req):
    res.end("Your user agent is: %s" % req.get_header("user-agent"))


def user(res, req):
    try:
        if int(req.get_parameter(0)) == 1:
            return res.end("Hello user with id 1!")
        # get_parameters retorna uma matriz de parâmetros
        # params = req.get_parameters()

    finally:
        # Para o usuário inválido, aparece para ir a rota válida (quando não aparece)
        req.set_yield(1)


async def delayed_hello(delay, res):
    await asyncio.sleep(delay)  # Faça algum async aqui 
    res.cork_end("Hello sorry for the delay!")
    # Cork_end é uma maneira menos esticada de escrever
    # res.cork(lambda res: res.end("Hello sorry for the delay!"))


def delayed(res, req):
    # O objeto de solicitação só vive durante o tempo de vida desta chamada
    # Obtém parameter, query, header e tudo o que você precisa aqui
    delay = req.get_query("delay")
    delay = 1 if delay == None else float(delay)

    # Obtém retorno de queries com dict com todas as string da query
    # queries = req.get_queries()

    # Diz à resposta para executar isso em loop de eventos
    # O abort handler é capturado aqui, então as respostas só serão enviadas se res.aborted == false
    res.run_async(delayed_hello(delay, res))


def json(res, req):
    # Se você passar um objeto, escreverá automaticamente um header com application/json
    res.end({"message": "I'm an application/json!"})


async def sleepy_json(res, req):
    # Obtém parameter, query, header e tudo o que você precisa antes do primeiro await :)
    user_agent = req.get_header("user-agent")
    # Exibe todo o header
    req.for_each_header(lambda key, value: print("Header %s: %s" % (key, value)))
    # Ou se você quiser obter todos os header em um dict
    print("All headers", req.get_headers())

    # req talvez não esteja disponivel em funções async anexadas diretamente após await
    # Mas se você não se importa com as informações de req, você pode fazer isso 
    await asyncio.sleep(2)  # Faz algum async 
    res.cork_end({"message": "I'm delayed!", "user-agent": user_agent})


def custom_header(res, req):
    res.write_header("Content-Type", "application/octet-stream")
    res.write_header("Content-Disposition", 'attachment; filename="message.txt"')
    res.end("Downloaded this ;)")


def send_in_parts(res, req):
    # Write e end aceita bytes e str ou tenta despejar em um json
    res.write("I can")
    res.write(" send ")
    res.write("messages")
    res.end(" in parts!")


def redirect(res, req):
    # Código de status é opcional, o padrão é 302
    res.redirect("/redirected", 302)


def redirected(res, req):
    res.end("You got redirected to here :D")


def not_found(res, req):
    res.write_status(404).end("Not Found")


# app.any, app.get, app.put, app.post, app.head, app.options, app.delete, app.patch, app.connect and app.trace estão disponíveis
app.get("/", home)
app.any("/anything", anything)
app.get("/user/agent", useragent)
app.get("/user/:id", user)
app.get("/delayed", delayed)
app.get("/json", json)
app.get("/sleepy", sleepy_json)
app.get("/custom_header", custom_header)
app.get("/cookies", cookies)
app.get("/send_in_parts", send_in_parts)
app.get("/redirect", redirect)
app.get("/redirected", redirected)
# Para ver sobre app.post vá para ./upload_or_post.py :D
# coringa finalmente :)
app.any("/*", not_found)

app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)
app.run()

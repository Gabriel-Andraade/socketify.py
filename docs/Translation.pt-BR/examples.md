# Exemplos

Router_and_basics
```python
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

```

Middleware
```python
from socketify import App, middleware

        # Se o usuário tiver autorização, retornar uma mensagem
async def get_user(authorization):
    if authorization:
        # Você pode fazer algum async aqui
        return {"greeting": "Hello, World"}
    return None

    # Verifica se o usuário está autorizado com middleware de autorização  
async def auth(res, req, data=None):
    user = await get_user(req.get_header("authorization"))
    if not user:
        res.write_status(403).end("not authorized")
        # Retorna False em middleware apenas se interromper a execução do próximo middleware e mostrar uma mensagem de erro '403'
        return False

    # Retorna dados extras
    return user

    # Outros middleware alterna a saudação
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

# Você também pode fazer um loop no MiddlewareRouter em middleware_router.py ;)
```

Middleware_async
```python
from socketify import App

# Este é apenas um exemplo de implementação que você pode importar usando from socketify import middleware para uma versão mais completa
# Aqui você vê o que pode fazer para autenticação de usuário ser válido

async def get_user(authorization):
    if authorization: # Verifique se existe autorização 
        # Faça m async aqui
        return {"greeting": "Hello, World"} # Retorne um dict se tiver a autorização 
    return None # Retorna None se não tiver a autorização


def auth(route):
    # na async query string, arguments e headers são válidos apenas até o primeiro await
    async def auth_middleware(res, req):
        
        # get_headers preservará headers (e cookies) dentro de req, após await 
        headers = req.get_headers()
        
        # get_parameters preservará todos os parâmetros dentro de req após await
        params = req.get_parameters()
        
        # get_queries preservará todas as queries dentro de req após await
        queries = req.get_queries()
        # Ou apenas use req.preserve() para preservar tudo

        user = await get_user(headers.get("authorization", None)) # Verificar autorização 
        if user: # Se o usuário estiver autorizado, chame a rota 
            return route(res, req, user)

        return res.write_status(403).cork_end("not authorized") # Retorna 403 'error' se não estiver autorizado

    return auth_middleware # Retorna no modo middleware

def home(res, req, user=None):
    theme = req.get_query("theme_color") # Define a cor do tema da query 
    
    theme = theme if theme else "light" # Define o tipo de tema
    
    greeting = user.get("greeting", None) # Define o tipo de saudação
    
    user_id = req.get_parameter(0) # Obtém o ID do usuário route
    
    res.cork_end(f"{greeting} <br/> theme: {theme} <br/> id: {user_id}") # Enviar a resposta

app = App() # Criar novo aplicativo 
app.get("/user/:id", auth(home)) # Define nota com middleware de autenticação
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()


# curl --location --request GET 'http://localhost:3000/user/10?theme_color=dark' --header 'Authorization: Bearer 23456789'
```

Middleware_router
```python
from socketify import App, MiddlewareRouter, middleware

    # Aqui você configura um app web com middleware para autenticação e manipulação de dados. Ele usa um MiddlewareRouter para gerenciar rotas e permitir que vários middleware sejam aplicados a cada rota,
        # Retorna saudações ou mensagens personalizadas dependendo da autenticação. 


async def get_user(authorization):
    if authorization:
        # Você pode fazer algum async aqui :)
        return {"greeting": "Hello, World"}
    return None

async def auth(res, req, data=None):
    # Middleware de autenticação 
    user = await get_user(req.get_header("authorization")) # Verificar autenticação 
    if not user: # Se não autorizado (obviamente)
        res.write_status(403).end("not authorized") # Mostra o erro '403' se não estiver autorizado
        # Retorna False em middlewares, apenas para a execução do próximo middleware
        return False

    # Retorna os dados extra
    return user


def another_middie(res, req, data=None):
    # Agora podemos misturar sync e async e alterar os dados aqui
    if isinstance(data, dict):
        gretting = data.get("greeting", "") # Escolha a saudação
        data["greeting"] = f"{gretting} from another middie ;)" # Você pode sempre alterar a saudação
    return data # Retorna o dado modificado


def home(res, req, user=None):
    res.cork_end(user.get("greeting", None))


app = App()

# Você pode usar um roteador middleware para adicionar middlewares a cada rota que você definir
auth_router = MiddlewareRouter(app, auth)
auth_router.get("/", home)
# Você também pode misturar middleware() com middlewarerouter
auth_router.get("/another", middleware(another_middie, home))

# Você também pode passar vários middlewares no middlewareRouter
other_router = MiddlewareRouter(app, auth, another_middie)
other_router.get("/another_way", home) # Defina outra rota com middleware


app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

```

Middleware_sync
```python
from socketify import App

# Este é apenas um exemplo de implementação que você pode importar usando from socketify import middleware para uma versão mais completa

# Defina uma função de middleware personalizada que aceite várias funções de middleware
def middleware(*functions):
    
    def middleware_route(res, req):
        data = None
        # Ciclo para todos os middlewares
        for function in functions:
            # Chama todos os middlewares
            data = function(res, req, data)
            # Para se retorna False
            if not data:
                break

    return middleware_route

     # Esta função verifica a autorização do usuário  

def get_user(authorization_header):
    if authorization_header:
        return {"greeting": "Hello, World"}
    return None

     # Esta autenticação de middleware verifica se tem um usuário autorizado
def auth(res, req, data=None):
    user = get_user(req.get_header("authorization"))
    if not user:
        res.write_status(403).end("not authorized") # Retorna o erro '403' se não autorizado
        return False

    # Retorna dados extras
    return user

    # Função principal para cumprimentar usu;arios
def home(res, req, user=None):
    res.end(user.get("greeting", None))

app = App()
app.get("/", middleware(auth, home))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

```

Broadcast
```python
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
```

Better_logging
```python
# Este exemplo mostra apenas como usar o registro em python para registrar request

from socketify import App
import logging
# Configure o formato de registro tipo esse

Logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO
)

# Simplesmente função de alta ordem devlog, você também pode criar um middleware para usar o registro, veja middleware_router.py e middleware.py

def devlog(handler):
    def devlog_route(res, req):
        logging.info(f'{req.get_method()} {req.get_full_url()} {req.get_headers()=}')
        handler(res, req)
    return devlog_route

# Agora ée usar a função devlog ou middleware

app = App()

def home(res, req):
    res.end("Hello World!") # Resposta para a rota 

app.get("/", devlog(home)) # Aplicar o registro na rota

app.listen(
    3000,
    lambda config: logging.info("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

Custom_json_serializer
```python
from socketify import App
import ujson

app = App()


# Defina o serializador json para json 
# O serializador json deve ter duas funções dumps e loads 
app.json_serializer(ujson)

app.get("/", lambda res, req: res.end({"Hello":"World!"}))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

Error_handler
```python
from socketify import App, AppOptions, AppListenOptions
import asyncio

app = App()


def xablau(res, req):
    raise RuntimeError("Xablau!")

    # Defina async se você receber um erro
async def async_xablau(res, req):
    raise RuntimeError("Async Xablau!")



# Este aqui pode ser um async sem problema
@app.on_error
def on_error(error, res, req):
    # Aqui você pode registrar corretamente o erro e fazer uma resposta para seu cliente
    print("Somethind goes %s" % str(error))
    # Resposta e solicitação  podem ser None se o erro estiver em uma função async
    if res != None:
        # Se a resposta existir, tente enviar algo 
        res.write_status(500)
        res.end("Sorry we did something wrong")

        # Mostre a mensagem no terminal quando puder executar, apenas xablau!
app.get("/", xablau)
app.get("/async", async_xablau)

# Você também pode usar set_error_handler
# app.set_error_handler(on_error)

app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)
app.run()
```

File_stream
```python
from socketify import App
import aiofiles
import time
import mimetypes
import os
from os import path
    # Precisa importar esses tipos de biblioteca
    
mimetypes.init()
    # Habilita o tipo "MIME"

async def home(res, req):
    # Este é apenas um exemplo de implementação, veja o exemplo static_files.py para uso de sendfilr e app.static
    # Há um auxiliar static_aiofile.py e um auxiliar static.aiofiles usando a implementação async disto
    # Async com IO é muito lento, então implementaremos "aiofile" usando libuv dentro do socketify no futuro (:

    # Defina o caminho do arquivo a ser servido
    filename = "./public/media/flower.webm"
    
    # Leia os header antes do primeiro await
    if_modified_since = req.get_header("if-modified-since")
    range_header = req.get_header("range")
    bytes_range = None
    start = 0
    end = -1
    # Analisar header em intervalo
    if range_header:
        bytes_range = range_header.replace("bytes=", "").split("-")
        start = int(bytes_range[0])
        if bytes_range[1]: # Verificar se o intervalo final foi especificado
            end = int(bytes_range[1])
    try:
        exists = path.exists(filename) # Verificar se o arquivo existe
        
        # Se não for encontrado
        if not exists:
            return res.write_status(404).end(b"Not Found") # Mostrar isto se não for encontrado

        # Obter tamanho e data da última modificação
        stats = os.stat(filename)
        total_size = stats.st_size
        size = total_size
        last_modified = time.strftime(
            "%a, %d %b %Y %H:%M:%S GMT", time.gmtime(stats.st_mtime)
        )

        # Verifique se está modificado desde que é fornecido 
        if if_modified_since == last_modified:
            return res.write_status(304).end_without_body() # Irá mostrar isso sem nem ter modificado 
        
        # Informa ao navegador a data da última modificação feita
        res.write_header(b"Last-Modified", last_modified)

        # Adicione o tipo de conteúdo
        (content_type, encoding) = mimetypes.guess_type(filename, strict=True)
        if content_type and encoding:
            res.write_header(b"Content-Type", "%s; %s" % (content_type, encoding))
        elif content_type:
            res.write_header(b"Content-Type", content_type)

        with open(filename, "rb") as fd: # Abra o arquivo
            # Verifique o intervalo e suporte-o
            if start > 0 or not end == -1:
                if end < 0 or end >= size:
                    end = size - 1
                size = end - start + 1
                fd.seek(start)  # Mova o arquivo para o intervalo inicial 
                if start > total_size or size > total_size or size < 0 or start < 0:
                    return res.write_status(416).end_without_body() # Retorna 416 se o intervalo não for válido
                res.write_status(206) # Retorne 206 caso for um intervalo parcial 
            else:
                end = size - 1
                res.write_status(200) # Retornará 200 caso o intervalo for bem sucedido 
                # Se você quiser, você pode trocar a numeração :)

            # Informe ao navegador que oferecemos suporte a intervalo
            res.write_header(b"Accept-Ranges", b"bytes")
            res.write_header(
                b"Content-Range", "bytes %d-%d/%d" % (start, end, total_size)
            )
            pending_size = size
            # Continue enviando até cancelar(aborted) ou terminar(done)
            while not res.aborted:
                chunk_size = 16384  # Tamanho de 16kb
                if chunk_size > pending_size:
                    chunk_size = pending_size
                buffer = fd.read(chunk_size) # isso aqui lê o pedaço do arquivo  
                pending_size = pending_size - chunk_size # Aqui atualiza o tamanho do arquivo 
                (ok, done) = await res.send_chunk(buffer, size)
                if not ok or done:  # não é possivel enviar porque provavelmente foi aborted
                    break

    except Exception as error:
        res.write_status(500).end("Internal Error") # Retorna 500 caso der erro


app = App() # Cria um novo app
app.get("/", home)
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

graceful_shutdown
```python
from socketify import App, AppOptions, AppListenOptions

app = App()

    # Defina uma função de desligamneto que será chamada quandp um cliente acessar a função de desligamento
def shutdown(res, req):
    res.end("Good bye!") # Envia uma resposta para o cliente
    app.close() # Fecha o app após enviar a resposta

    # Define a rota principal "/" quando o cliente retornar 
app.get("/", lambda res, req: res.end("Hello!"))
    # Define a rota "/shutdowm"(desligar) para executar a função shutdowm 
app.get("/shutdown", shutdown)

app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)
app.run()
print("App Closed!")
```

graphiql_raw
```python
import dataclasses
import strawberry  # Usado para definir esquema do GraphQL e criar dicas
import strawberry.utils.graphiql # Ferramenta para interface Web

from socketify import App
from typing import List, Optional


    # Definir o tipo de classe chamada
@strawberry.type
class User:
    name: str


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> Optional[User]:
        return User(name="Hello")

    # Cria esquema GraphQL a partir da classe de query =
schema = strawberry.Schema(Query)

    # Definir função async para manipular solicitações POST no GraphiQL
async def graphiql_post(res, req):
    # Podemos passar o que quisermos para context, query, headers ou params, cookies e etc
    context_value = req.preserve()

    # Obter todos os dados de entrada e analisar como json
    body = await res.get_json()
    # Extrair a query e possíveis variáveis de entrada
    query = body["query"]
    variables = body.get("variables", None)
    root_value = body.get("root_value", None)
    operation_name = body.get("operation_name", None)
    # Execute a query GraphQL usando o esquema 
    data = await schema.execute(
        query,
        variables,
        context_value,
        root_value,
        operation_name,
    )
    # Envie uma resposta json para cliente com dados, erros e extensões 
    res.cork_end(
        {
            "data": (data.data),
            **({"errors": data.errors} if data.errors else {}),
            **({"extensions": data.extensions} if data.extensions else {}),
        }
    )

    # Configure o servidor usando a biblioteca de app
app = App()
    # Roteie GET retornamos a interface GraphiQL HTML para um teste de facilidade 
app.get("/", lambda res, req: res.end(strawberry.utils.graphiql.get_graphiql_html()))
    # Postar rota para processar consultas GraphQL
app.post("/", graphiql_post)
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

graphiql
```python
import dataclasses
import strawberry
import strawberry.utils.graphiql

from socketify import App
from typing import List, Optional
from helpers.graphiql import graphiql_from

    # Definir tipo de usuário para GraphQL
@strawberry.type
class User:
    name: str

    # Self.Context é o AppRequest, tem dados de request
@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> Optional[User]:
        # Self.Context é o AppRequest, tem dados de request
        return User(name="Hello")

app = App()
    # Definir rota GET para consultas GraphiQL, retornando ao HTML para o navegador
app.get("/", lambda res, req: res.end(strawberry.utils.graphiql.get_graphiql_html()))
    # Aqui define a rota POST para consultas GraphQL de processo, usando função graphiql_from
app.post("/", graphiql_from(Query))
# Você também pode passar uma Mutação como segundo parâmetro
# app.post("/", graphiql_from(Query, Mutation))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

Http
```python
from socketify import App, AppOptions

app = App(
    AppOptions(
        key_file_name="./misc/key.pem", # Caminho arquivo da chave privada
        cert_file_name="./misc/cert.pem", # Caminho do arquivo certificado
        passphrase="1234", # Senha
    )
        # Define uma rota para responder
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

Http_request_cache
```python
from socketify import App
import redis
import aiohttp
import asyncio
from helpers.twolevel_cache import TwoLevelCache # Importe dois níveis de caches

# Criar enquete redis + conexões
redis_pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
redis_connection = redis.Redis(connection_pool=redis_pool)
# CACHE DE 2 NÍVEIS (Redis para compartilhar entre os trabalhadores, Memória para ser muito mais rápida)
# Cache na memória é de 30s, cache no redis é de 60s de duração
cache = TwoLevelCache(redis_connection, 30, 60)

###
# Model
###

    # Função async para buscar dados de um Pokémon específico usando PokeAPI
async def get_pokemon(number):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://pokeapi.co/api/v2/pokemon/{number}"
        ) as response:
            pokemon = await response.text() # Resposta com texto
            # Cache só funciona com strings/bytes
            # Não mudaremos nada aqui, então não precisa analisar o json
            return pokemon.encode("utf-8")

    # Função async para buscar uma lista de 151 Pokémon originais
async def get_original_pokemons():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://pokeapi.co/api/v2/pokemon?limit=151"
        ) as response:
            # Cache só funciona com string/bytes 
            # Aqui não muda nada, não precisa analisar
            pokemons = await response.text()
            return pokemons.encode("utf-8") # Convert text in bytes for cache 


###
# Routes
###

    # função para listar Pokémon originais com cache
def list_original_pokemons(res, req):

    # Verifique o cache para a resposta mais rápida
    value = cache.get("original_pokemons") # Verificar cache para todos
    if value != None:
        return res.end(value) # Responder com cache disponível

    # Aqui obtém async do modelo
    async def get_originals():
        value = await cache.run_once("original_pokemons", 5, get_original_pokemons)
        res.cork_end(value) # Enviar resposta com dados

    res.run_async(get_originals())  # Função de execução async

    # Função de buscar e listar Pokémon específico por números com cache
def list_pokemon(res, req):

    # Obter parâmetros necessários
    try:
        number = int(req.get_parameter(0))
    except:
        # Número inválido
        return req.set_yield(1)

    # Verifica o cache para desempenhar uma resposta rápida
    cache_key = f"pokemon-{number}" # Crie uma chave de cache específica para um Pokémon 
    value = cache.get(cache_key) # Verifica um cache
    if value != None:
        return res.end(value) # Responde com cache se estiver disponível

    # Função async para dados de pesquisa de un Pokémon se não tiver no cache
    async def find_pokemon(number, res):
        # Sincronize(sync) com o bloqueio do redis para executar apenas uma vez
        # Se mais de 1 worker/request tentar fazer esta solicitação, apenas um chamará o modelo e os outros obterão do cache
        value = await cache.run_once(cache_key, 5, get_pokemon, number)
        res.cork_end(value) # Envia uma resposta com dados

    res.run_async(find_pokemon(number, res)) # execute a função async


###
# Aqui eu decidi usar sync primeiro e async somente se for necessário, mas você pode usar async diretamente veja ./aync.py
###
app = App()
app.get("/", list_original_pokemons) # Rota para uma lista de 151 pokémon original 
app.get("/:number", list_pokemon) # Rota dinâmica para pesquisar Pokémon específico
app.any("/*", lambda res, _: res.write_status(404).end("Not Found"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

Listen_option
```python
from socketify import App, AppListenOptions

app = App()

    # Defina uma rota na raiz "/" que responde 'Olá mundo socketify do Python!'
app.get("/", lambda res, req: res.end("Hello World socketify from Python!"))
app.listen(
    AppListenOptions(port=3000, host="0.0.0.0"),
    lambda config: print(
        "Listening on port http://%s:%d now\n" % (config.host, config.port)
    ),
)
app.run()
```

Not_found
```python
from socketify import App, AppOptions, AppListenOptions

app = App()

 # Rota principal responde com async
async def home(res, req):
    res.end("Hello, World!")


def user(res, req):
    try:
        if int(req.get_parameter(0)) == 1: # Verifica o usário 
            return res.end("Hello user 1!") # Responde apenas o 'usuário 1'
    finally:
        # Para o usuário inválido aparece para ir para a rota válida (não encontrada)
        req.set_yield(1)

        # Quando usuário inválido tentar, mostrará o erro '404' (não encontrado):)
def not_found(res, req):
    res.write_status(404).end("Not Found ):")

        # Configura rotas
app.get("/", home)
app.get("/user/:user_id", user)
app.any("/*", not_found)

app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)
app.run()
```

Proxy
```python
from socketify import App

    # Apenas para exibir o IP 
def home(res, req):
    res.write("<html><h1>")
    res.write("Your proxied IP is: %s" % res.get_proxied_remote_address()) # Mostra o servidor IP proxy
    res.write("</h1><h1>")
    res.write("Your IP as seen by the origin server is: %s" % res.get_remote_address()) # Mostra o IP de origem
    res.end("</h1></html>")


app = App()
app.get("/*", home)
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

Template_jinja2
```python
from socketify import App

# Veja helper/templates.py para implementação de plugin
from helpers.templates import Jinja2Template

 # Aqui são a configuração para jinja2
app = App()
app.template(Jinja2Template("./templates", encoding="utf-8", followlinks=False))

 # Aqui é a configuração para renderizar o template de jinja2 
def home(res, req):
    res.render("jinja2_home.html", title="Hello", message="Hello, World")

 # Defina uma rota para "/" para executar a função "home"
app.get("/", home)
app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)
app.run()
```

Template_mako
```python
from socketify import App

# Veja helper/templates.py para implementação de plugin
from helpers.templates import MakoTemplate

 # Aqui são a configuração para mako
app = App()
app.template(
    MakoTemplate(
        directories=["./templates"], output_encoding="utf-8", encoding_errors="replace"
    )
)

 # Aqui é a configuração para renderizar o template de mako
def home(res, req):
    res.render("mako_home.html", message="Hello, World")

 # Defina uma rota para "/" para executar a função "home"
app.get("/", home)
app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)
app.run()
```

Upgrade
```python
from socketify import App, AppOptions, OpCode, CompressOptions

    # É chamado qunando o cliente websocket pode ser conectado, enviando uma mensagem
def ws_open(ws):
    print("A WebSocket got connected!")
    ws.send("Hello World!", OpCode.TEXT)

    # Manuseia com mensagem recebida
def ws_message(ws, message, opcode):
    print(message, opcode)
    # Ok é false se a backpressure foi criada, aguarde o drain
    ok = ws.send(message, opcode)

    # Manuseia o processo de atualização ao receber o header de solicitação específico
def ws_upgrade(res, req, socket_context):
    key = req.get_header("sec-websocket-key")
    protocol = req.get_header("sec-websocket-protocol")
    extensions = req.get_header("sec-websocket-extensions")
    res.upgrade(key, protocol, extensions, socket_context)


app = App()
app.ws(
    "/*",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR, # configura a compression
        "max_payload_length": 16 * 1024 * 1024, # Tamanho máximo do payload
        "idle_timeout": 12, # Tempo máximo
        "open": ws_open, # Define a função a ser chamada ao receber
        "message": ws_message, # manuseia a mensagem 
        "upgrade": ws_upgrade, # Gerencia a atualização do websocket
        "drain": lambda ws: print( # Aqui a função mostra a backpressure
            "WebSocket backpressure: %s", ws.get_buffered_amount()
        ),
        "close": lambda ws, code, message: print("WebSocket closed"),
    },
)
    # Define resposta padrão para outras solicitação 
app.any("/", lambda res, req: res.end("Nothing to see here!"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()
```

Upgrade_async
```python
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
```

Upload_and_post
```python
from socketify import App

###
# Sempre recomendamos verificar res.aborted em operações async
###


def upload(res, req):
    # Lida com os dados simples
    print(f"Posted to {req.get_url()}")

    def on_data(res, chunk, is_end):
        # Callback com um vhunk de dados recebido 
        print(f"Got chunk of data with length {len(chunk)}, is_end: {is_end}") # Mostrar tamanho do chunk recebido 
        if is_end:
            res.cork_end("Thanks for the data!") # Responder o cliente quando receber todos os dados

    res.on_data(on_data) # Registrar função de callback para receber dados


async def upload_chunks(res, req):
    print(f"Posted to {req.get_url()}") # Mostrar upload de URL
    # Aguardar todos os dados, retornar os chunks recebidos se falhar (provavelmente a falha é de aborted request)
    data = await res.get_data() # Aguarda todos os dados recebidos

    print(f"Got {len(data.getvalue())} bytes of data!")  # Mostra o tamanho máximo
    
    # Responde quando terminamos
    res.cork_end("Thanks for the data!")


async def upload_json(res, req):
    print(f"Posted to {req.get_url()}")
    # Aguarda todos os dados e analisa como json, retorna false se falhar
    info = await res.get_json() # Aguarda e analisa os dados como json

    print(info)
    
    # Respondemos quando terminamos
    res.cork_end("Thanks for the data!")


async def upload_text(res, req):
    # Manipule de função async com upload
    print(f"Posted to {req.get_url()}")
    # Aguarda todos os dados e decodifica como text, retorna None se falhar
    text = await res.get_text()  # O primeiro parâmetro é a codificação (Padrão  utf-8)

    print(f"Your text is {text}") # Mostra o texto recebido 

    # Respondemos quando terminarmos 
    res.cork_end("Thanks for the data!")


async def upload_urlencoded(res, req):
    print(f"Posted to {req.get_url()}")
    # Aguarde todos os dados e decodifica como application/x-www-form-urlencode, retorna None se falhar
    form = (
        await res.get_form_urlencoded()
    )  # O primeiro parâmetro é a codficação (padrão utf-8)

    print(f"Your form is {form}") # Mostra os dados do formulário recebidos

    # Respodemos quando terminarmos 
    res.cork_end("Thanks for the data!")


async def upload_multiple(res, req):
    print(f"Posted to {req.get_url()}")
    content_type = req.get_header("content-type")
    # Podemos verificar o Content-Type para aceitar vários formatos
    if content_type == "application/json":
        data = await res.get_json()
    elif content_type == "application/x-www-form-urlencoded":
        data = await res.get_form_urlencoded()
    else:
        data = await res.get_text()

    print(f"Your data is {data}") # Mostrar dados recebidos

    # Respondemos quando terminarmos
    res.cork_end("Thanks for the data!") # Responder quando todos os dados forem entregues

def upload_formdata(res, req):
    # Usando o pacote streaming_form_data para análise
    from streaming_form_data import StreamingFormDataParser # analisar os dados em tempo real
    from streaming_form_data.targets import ValueTarget, FileTarget

    print(f"Posted to {req.get_url()}")
    parser = StreamingFormDataParser(headers=req.get_headers())
    name = ValueTarget()
    parser.register('name', name)
    file = FileTarget('/tmp/file')
    file2 = FileTarget('/tmp/file2')
    parser.register('file', file)
    parser.register('file2', file2)


    def on_data(res, chunk, is_end):   
        parser.data_received(chunk)
        if is_end:
            res.cork(on_finish)


    def on_finish(res):
        print(name.value)
        
        print(file.multipart_filename)
        print(file.multipart_content_type)

        print(file2.multipart_filename)
        print(file2.multipart_content_type)

        res.end("Thanks for the data!")

    res.on_data(on_data)


async def upload_formhelper(res, req):
    # Usando o pacote streaming_form_data para análise + auxiliar
    from streaming_form_data import StreamingFormDataParser
    from streaming_form_data.targets import ValueTarget, FileTarget
    from helpers.form_data import get_formdata


    print(f"Posted to {req.get_url()}")
        # Cria um parser para processar dados de formulários multipart a partir dos headers do request
    parser = StreamingFormDataParser(headers=req.get_headers())
    name = ValueTarget()
    parser.register('name', name)
    file = FileTarget('/tmp/file')
    file2 = FileTarget('/tmp/file2')
    parser.register('file', file)
    parser.register('file2', file2)

    await get_formdata(res, parser)

    print(name.value)
    
    print(file.multipart_filename)
    print(file.multipart_content_type)

    print(file2.multipart_filename)
    print(file2.multipart_content_type)

    res.cork_end("Thanks for the data!")


app = App()
app.post("/", upload) # simple upload route
app.post("/chunks", upload_chunks) # chunk upload route
app.post("/json", upload_json) # json upload route 
app.post("/text", upload_text) # text upload route
app.post("/urlencoded", upload_urlencoded) # Codificado URL upload route
app.post("/multiple", upload_multiple) # multiple upload route
app.post("/formdata", upload_formdata) #  data form upload route
app.post("/formdata2", upload_formhelper) # formhelper upload route

app.any("/*", lambda res, _: res.write_status(404).end("Not Found"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

Websocket
```python
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
```

Ws_close_connection
```python
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
```

Hello_world
```python
from socketify import App

app = App()
app.get("/", lambda res, req: res.end("Hello World!"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

Hello_world_unix_domain
```python
from socketify import App, AppListenOptions

app = App()
app.get("/", lambda res, req: res.end("Hello World!"))
    # Configurar servidor para socket unix
app.listen(
    AppListenOptions(domain="/tmp/test.sock"),
    lambda config: print("Listening on port %s http://localhost/ now\n" % config.domain),
)
app.run()

# Você pode testar com curl -GET --unix-socket /tmp/test.sock http://localhost/
```

Hello_world_cli
```python
from socketify import App

# O aplicativo será criado pelo cli com todas as coisas que você deseja configurar
def run(app: App): 
    # add your routes here
    app.get("/", lambda res, req: res.end("Hello World!"))
    
# python -m socketify hello_world_cli:run --port 8080 --workers 2
# python3 -m socketify hello_world_cli:run --port 8080 --workers 2
# pypy3 -m socketify hello_world_cli:run --port 8080 --workers 2

# Veja as opções usando no terminal: python3 -m socketify --help
```

Hello_world_cli_ws
```python
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
```

Static_files
```python
# Temos uma versão disso usando aiofile e aiofiles
# Esta é uma versão de sync sem nehuma dependência, normalmente é muito rápido em CPython e PyPy3
# Em produção, recomendado fortemente usar CDN como CloudFlare ou e/ NGINX ou similar para arquivos estáticos (em qualquer linguagem/framework)

# Alguns dados da minha máquina rodando (Debian 12/testing, i7-7700HQ, 32GB RAM, Samsung 970 PRO NVME)
# Usando oha -c 400 -z 5s http://localhost:3000/

# nginx     - try_files                 -  77630.15 req/s
# pypy3     - socketify static          -  16797.30 req/s
# python3   - socketify static          -  10140.19 req/s
# node.js   - @fastify/static           -   5437.16 req/s
# node.js   - express.static            -   4077.49 req/s
# python3   - socketify static_aiofile  -   2390.96 req/s
# python3   - socketify static_aiofiles -   1615.12 req/s
# python3   - scarlette static uvicorn  -   1335.56 req/s
# python3   - fastapi static gunicorn   -   1296.14 req/s
# pypy3     - socketify static_aiofile  -    639.70 req/s
# pypy3     - socketify static_aiofiles -    637.55 req/s
# pypy3     - fastapi static gunicorn   -    253.31 req/s
# pypy3     - scarlette static uvicorn  -    279.45 req/s

# Conclusão:
# Com PyPy3 somente estático é realmente utilizável gunicorn/uvicorn, aiofiles e aiofile são realmente lentos no PyPy3 talvez isso mude com HPy
# Python3 com qualquer opção será mais rápido que gunicorn/uvicorn mas com PyPy3 com estático obtivemos 4x (ou quase isso no caso de fastify) desempenho do node.js
# Mas mesmo PyPy3 + socketify estático é 5x mais lento que NGINX

# De qualquer forma, realmente recomendamos usar NGINX ou similar + CDN para produção como todo mundo
# Recomendações de produto Gunicorn: https://docs.gunicorn.org/en/latest/deploy.html#deploying-gunicorn
# Recomendações de produto Express: https://expressjs.com/en/advanced/best-practice-performance.html
# Recomendações de produto Fastify: https://www.fastify.io/docs/latest/Guides/Recommendations/

from socketify import App, sendfile


app = App()


# Enviar home
async def home(res, req):
    # Envia o arquivo inteiro com 304 e suporte a intervalo de bytes
    await sendfile(res, req, "./public/index.html")


app.get("/", home)

# Serve todos os arquivos na pasta pública sob /*rota (você pode usar qualquer rota como/assets)
app.static("/", "./public")

app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

```
## Todas as coisas básicas

Esta seção mostra os conceitos básicos de`AppResponse` e `AppRequest`

### Escrevendo Datas

`res.write(message)` Onde a mensagem pode ser String, bytes ou um Object que pode ser convertido para json, envie a mensagem para a resposta sem terminar.

`res.cork_end(message, end_connection=False)` ou `res.end(message, end_connection=False)` Onde a mensagem pode ser String, bytes ou um Object que pode ser convertido para json, enviar a mensagem para a resposta e finalizar a resposta.

A chamada `res.end()` ou `res.cork_end()` acima irá na verdade chamar três funções de envio separadas; `res.write_status`, `res.write_header` e tudo o que ele faz ao agrupar a chamada `res.cork` ou `res.cork_end` você garante que essas três função de envio sejam eficientes e resultem apenas em um único Syscall(chamada do sistema) de envio e um único bloco SSL se estiver usando SSL.


`res.send(message, content_type=b'text/plain, status=b'200 OK', headers=None, end_connection=False)` e `res.cork_send(message, content_type=b'text/plain', status=b'200 OK', headers=None, end_connection=False)`
Combina `res.write_status()`, `res.write_headers()`, e `res.end()` de uma forma que seja mais fácil de usar, se você quiser enviar tudo em chamada apenas usando Parameters nomeados. Os Headers podem receber qualquer iterador de iterators/tuple como `iter(tuple(str, str))` onde o primeiro valor é o nome do Headers e o seguinte valor, usar `res.cork_send` garantirá o envio de todos os dados em um estado corked.
    

Usando `res.write_continue()` escreve HTTP/1.1 100 Continue como resposta.

`res.write_offset(offset)` Define o deslocamento para gravação de dados.

`res.get_write_offset()` Obtém o deslocamento de gravação atual. 

`res.pause()` e `res.resume()` Pausam e retornam a resposta.

```python
def send_in_parts(res, req):
    # Write e end aceita bytes e str ou tenta despejar em um json
    res.write("I can")
    res.write(" send ")
    res.write("messages")
    res.end(" in parts!")
    
```

### terminando sem body
```python
def empty(res, req):
    res.end_without_body()
```

## verificando se já respondeu
`res.has_responded()` Retorna True se a resposta já foi feita.

### Redirecionando
```python
def redirect(res, req):
    # Código de status é opcional, o padrão é 302.
    res.redirect("/redirected", 302)

```

### Escrevendo status
```python
def not_found(res, req):
    res.write_status(404).end("Not Found")

def ok(res, req):
    res.write_status("200 OK").end("OK")
```

### Usando o send
```python
def not_found(res, req):
    res.send("Not Found", status=404)

def ok(res, req):
    res.send("OK", status="200 OK")

def json(res, req):
    res.send({"Hello", "World!"})

def with_headers(res, req):
    res.send({"Hello": "World!"}, headers=(("X-Rate-Limit-Remaining", "10"), (b'Another-Headers', b'Value')))
```


### Conferir o URL ou method

`req.get_full_url()` retornará o caminho com a string de consulta
`req.get_url()` retornará o caminho sem a string de consulta
`req.get_method()` retornará o método HTTP(diferencia maiúsculas de minúsculas).

### Parameters

Você pode usar `req.get_parameters(index)` para obter o valor do parâmetro como string ou usar `req.get_parameters()` para obter uma lista de parâmetros.

```python
def user(res, req):
    if int(req.get_parameter(0)) == 1:
            return res.end("Hello user with id 1!")
    params = req.get_parameters()
    print('All params', params)

app.get("/user/:id", user)
```

### Headers

Você pode usar `req.get_header(lowercase_header_name)` para obter o valor da string do Headers como String ou usar `req.get_headers()` para obter como um dict, `req.for_each_header()` se você quiser apenas iterar nos headers. Você também pode definir o Headers usando `res.write_header(name, value)`.

```python
def home(res, req):
    auth = req.get_header("authorization")
    headers = req.get_headers()
    print("All headers", headers)

def custom_header(res, req):
    res.write_header("Content-Type", "application/octet-stream")
    res.write_header("Content-Disposition", 'attachment; filename="message.txt"')
    res.end("Downloaded this ;)")

def list_headers(res, req):
    req.for_each_header(lambda key, value: print("Header %s: %s" % (key, value)))

```

### Query String
Você pode usar `req.get_query(parameter_name)` para obter o query string ou usar `req.get_queries()` para obter como um dict.

```python
def home(res, req):
    search = req.get_query("search")
    
    queries = req.get_queries()
    print("All queries", queries)
```

### Cookies

Também temos um `req.get_cookie(cookie_name)` para obter um valor de cookie como um string `res.set_cookie(name, value, options=None)` para definir um cookie.

```python

def cookies(res, req):
    # cookies são gravados após o término
    res.set_cookie(
        "session_id",
        "1234567890",
        {
            # expira
            # caminho
            # comentário
            # domínio
            # idade-máxima
            # seguro
            # versão
            # apenas HTTP
            # mesmo caminho do site
            "path": "/",
            # "domínio": "*.test.com",
            "httponly": True,
            "samesite": "None",
            "secure": True,
            "expires": datetime.utcnow() + timedelta(minutes=30),
        },
    )
    res.end("Your session_id cookie is: %s" % req.get_cookie("session_id"))
```


## Obtendo o endereço remoto
VocÊ pode obter o endereço remoto usando `get_remote_address_bytes`, `get_remote_address` e o endereço proxy `get_proxied_remote_address_bytes` ou `get_proxied_remote_address`

```python
def home(res, req):
    res.write("<html><h1>")
    res.write("Your proxied IP is: %s" % res.get_proxied_remote_address())
    res.write("</h1><h1>")
    res.write("Your IP as seen by the origin server is: %s" % res.get_remote_address())
    res.end("</h1></html>")
```
> A diferença entre a versão _bytes() e a non bytes é que uma retorna String e a outra raw bytes.


## Pub/Sub de app
`app.num_subscribers(topic)` retornará o número de inscritos no tópico.
`app.publish(topic, message, opcode=OpCode.BINARY, compress=False)` irá enviar uma mensagem para todos os inscritos no tópico.


## Verifique o aborted
Se a conexão for abortada você pode marcar `res.aborted` que retornará True ou False. Você também pode pegar o aborded, ao usar uma rota assíncrona, o Socketify sempre capturará automaticamente o manipulador de aborto.

```python
def home(res, req):
     def on_abort(res):
        res.aborted = True
        print("aborted!")
            
    res.on_aborted(on_abort)
```

## Executando async a partir da rota de sincronização
Se você quiser otimizar muito e não usar async sem necessidade você pode usar `res.run_async() or app.run_async()` para executar uma corrotina

```python
from socketify import App, sendfile

def route_handler(res, req):
    if in_memory_text:
        res.end(in_memory_text)
    else:
        # pegue o abort handler adicionando-o a 'res.aborted' se for aborted
        res.grab_aborted_handler() 
        res.run_async(sendfile(res, req, "my_text"))
```


## Usando o  ujson, orjson ou qualquer serializador JSON personalizado 
socketify por padrão usa o módulo `json` integrado com ótimo desempenho no PyPy, mas se você quiser usar outro módulo em vez do padrão, basta registrar-se usando `app.json_serializer(module)`

```python
from socketify import App
import ujson
app = App()

# configure o serializador json para ujson
# serializador json deve ter funções de dumps e carregamento
app.json_serializer(ujson)

app.get("/", lambda res, req: res.end({"Hello":"World!"}))
```

## Raw socket pointer

Se for algum motivo você precisar do ponteiro de soquete bruto, você pode usar `res.get_native_handle()` e irá obter um manipulador CFFI

## Raw event loop pointer

Se você precisar acessar o ponteiro bruto de `libuv` você pode usar `app.get_native_handle()` e irá obter um manipulador CFFI

## Preserve data for use after waiting

Objeto HttpRequest sendo alogado na pilha e válido apenas em uma única invocação de retorno de chamada, portanto, válido apenas no primeiro "segmento" antes da primeira espera. Se você deseja apenas preservar cabeçalhos, url, métodos, cookies, e string de consulta, você pode usar `req.preserve()` para copiar todos os dados e mantê-los no objeto de solicitação, mas haverá alguma penalidade no desempenho.


# Lifespan/Lifecycle event

Você pode usar eventos de início e encerramento do socketify para criar/limpar pools de threads, pools de conexões, etc. quando o aplicativo inicia ou desliga sozinho.

Se ocorrer alguma exceção no evento de início, o aplicativo continuará e iniciará normalmente, se você quiser que  uma inicialização falhe, você precisa capturar a exceção e usar `sys.exit(1)` para desligar prematuramente.

Tanto `app.on_start` e `app.on_shutdown` podem ser sincronizados e async.


```python
from socketify import App

def run(app: App):
    
    @app.on_start
    async def on_start():
        print("wait...")
        await asyncio.sleep(1)
        print("start!")

    @app.on_shutdown
    async def on_shutdown():
        print("wait...")
        await asyncio.sleep(1)
        print("shutdown!")

    router = app.router()

    @router.get("/")
    def home(res, req):
        res.send("Hello, World!")

```

# Error handler events

Você pode definir um manipulador de erros para dar ao usuário 500 personalizada e/ou para fazer o log corretamente.

Usando o decorador `app.set_error_handler(on_error)` ou `app.on_error` 


```python
from socketify import App

def run(app: App):

    @app.on_error
    def on_error(error, res, req):
        # aqui você pode registrar corretamente o erro e fazer uma resposta bonita para seus clientes
        print("Somethind goes %s" % str(error))
        # resposta e solicitação podem ser None se o erro estiver em uma função assíncrona
        if res != None:
            # se a resposta existir, tente enviar algo 
            res.write_status(500)
            res.end("Sorry we did something wrong")

    router = app.router()

    @router.get("/")
    def home(res, req):
        raise RuntimeError("Oops!")


```
### próximo [Upload and Post](upload-post.md)
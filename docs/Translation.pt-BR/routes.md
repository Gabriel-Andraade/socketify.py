# App.get, post, options, delete, patch, put, head, connect, trace e qualquer routes

Você anexa o funcionamento a "URL routes". Uma function/lambda é pareada com um "método"(método HTTP) e um padrão (o padrão de URL).

Os métodos são muitos, mas os mais comuns são provavelemente get e post. Todos eles têm a mesma assinatura, vamos dar uma olhada em um exemplo:

```python
app.get("/", lambda res, req: res.end("Hello World!"))
```

```python
def home(res, req):
    res.end("Hello World!")

app.get("/", home)
```

```python
async def home(res, req):
    body = await res.get_json()
    user = await get_user(body)
    res.cork_end(f"Hello World! {user.name}")
    
app.post("/", home)
```
> Sempre que seu retorno de callback for uma corrotina, como async/await, o roking automático só pode ocorrer na primeira parte da corrotica(considere await um separador que essencialmente corta a corrotina em segmentos menores). Apenas o primeiro "segment" da corrotina será chamado do socketify, os seguintes segment async serão chamados pelo loop de eventos asyncio em um momento posterior e, portanto, não estarão sob nosso controle com o roking padrão habilidado, o objeto HttpRequest sendo alocado ns pilha e válido apenas em uma única invocação de callback, portanto, válido apenas no primeiro "segment" antes do primeiro await. Se desejar preservar headers, URL, method, cookies e query string você pode usar `req.preserve()` para copiar todos os dados e mantê-los no request object, mas haverá alguma falha no desempenho. Dê uma olhada em [Corking] (corking.md) para obter informações mais afundo sobre.


Você também pode usar o `Decorator router` como o nome sugere, este roteador permite o uso de decoradores para roteamento e também vem com uma opção de prefixo e suporte a middleware.

```python
from socketify import App

app = App()
router = app.router()

@router.get("/")
def home(res, req):
   res.end("Hello World!")

api = app.router(prefix="/api")

# Servirá em /api/hello
@api.get("/hello") 
def hello(res, req):
   res.end("Hello API!")

private = app.router("/api", auth_middleware)

# Servirá em /api/users e usará auth_middleware
@private.get("/users")
def get_users(res, req, auth):
   res.end("Hello private API!")
```

## Corrrespondência de padrões

As rotas são correspondidas em ordem de especificidade, não pela ordem em que você as registra:

- Highest priority - static routes, pense em "/hello/this/is/static".
- Middle priority - parameter routes, pense em "/candy/:kind", onde o valor de :kind é recuperado `req.get_parameter(0)`.
- Lowest priority - wildcard routes, pense em "/hello/*".

Em outras palavras, quanto mais específica for uma route, mais cedo ela corresponderá. Isso permite que você wildcard routes que correspondam a uma ampla gama de URLs e, em seguida, "esculpa" um comportamento mais específico a partir disso.

"Qualquer" routes, aquelas que correspondem a qualquer method HTTP, corresponderão com prioridade mais baixa do que route que especificam seus method HTTP específicado (como GET) se e somente se as duas route forem igualmente específicas

## Ignorando a próxima route
Se você quiser dizer ao roteador para ir para a próxima route, você pode chamar `req.set_yield(1)`

Example
```python
def user(res, req):
    try:
        if int(req.get_parameter(0)) == 1:
            return res.end("Hello user 1!")
    finally:
        # Usuário inválido diz para ir a próxima route, route válida
        req.set_yield(1)


def not_found(res, req):
    res.write_status(404).end("Not Found")

app.get("/", home)
app.get("/user/:user_id", user)
app.any("/*", not_found)

```

## Error handler

No caso de algumas exceções não capturadas, sempre tentaremos o nosso melhor para chamar o Error Handler, você pode definir o manipulador usando `app.set_error_handler(handler)`

```python

def xablau(res, req):
    raise RuntimeError("Xablau!")


async def async_xablau(res, req):
    await asyncio.sleep(1)
    raise RuntimeError("Async Xablau!")


# Isso pode ser um async sem problemas
def on_error(error, res, req):
    # Aqui você pode registrar corretamente o erro e fazer uma resposta bonita para seus clientes
    print("Something goes %s" % str(error))
    # resposta e solicitação podem ser None se o erro estiver em uma função async
    if res != None:
        # se a resposta existir, tente enviar algo
        res.write_status(500)
        res.end("Sorry we did something wrong")


app.get("/", xablau)
app.get("/async", async_xablau)
app.set_error_handler(on_error)
```

## Proxies

implementamos `Proxy Protocol v2` para que possa usar `res.get_proxied_remote_address()` para obter o IP proxy

```python
from socketify import App


def home(res, req):
    res.write("<html><h1>")
    res.write("Your proxied IP is: %s" % res.get_proxied_remote_address())
    res.write("</h1><h1>")
    res.write("Your IP as seen by the origin server is: %s" % res.get_remote_address())
    res.end("</h1></html>")


app = App()
app.get("/*", home)
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

### Suporte HttpRouter po SNI

```python

def default(res, req):
    res.end("Hello from catch-all context!")

app.get("/*", default)

  
# A seguir está o contexto para o domínio *.google.*
# PS: as opções são opcionais se você não estiver usando SSL
app.add_server_name("*.google.*", AppOptions(key_file_name="./misc/key.pem", cert_file_name="./misc/cert.pem", passphrase="1234"))

def google(res, req):
    res.end("Hello from *.google.* context!")

app.domain("*.google.*").get("/*", google)

#Você também pode remover um nome de
app.remove_server_name("*.google.*")

```

### próximo [Middlewares](middlewares.md)

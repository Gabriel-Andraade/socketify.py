# Middlewares

Temos suporte para Middlewares usando a função auxiliar `middleware` e o  `MiddlewareRouter`.
Como comentado na seção [routes](routes.md) e na [corking](corking.md) Sempra que seu retorno de chamada for uma corrotina, como async/await, o roking automático so pode acontecer na primeira parte da corrotina (considere await um separador que essencialmente corta a corrotina em segmentos menores). Aoenas o primeiro "segmento" da corrotina será chamado do socketify, os seguintes segmentos async serão chamados pelo loop de eventos async em um ponto posterior no tempo e, portanto, não estarão sob nosso controle com o roking padrão habilidado. O objeto HttpRequest sendo alocado na pilha e válido apenas em uma única callback, portanto, válido apenas no primeiro "drgmento" antes do primeiro await.

No caso de middlewares, se um deles for uma corrotina, chamamos automaticamente `req.preserve()` para preservar os dados da solicitação entre os middlewares. 

Os middleware são executados em série, então se os dados retornados forem Falsy (False/None etc.) resultarão no fim da execução, se não forem Falsy, os dados passarão para o próximo middleware como um terceiro parameter.



```python
from socketify import App, MiddlewareRouter, middleware


async def get_user(authorization):
    if authorization:
        # Você pode fazer um async aqui
        return {"greeting": "Hello, World"}
    return None


async def auth(res, req, data=None):
    user = await get_user(req.get_header("authorization"))
    if not user:
        res.write_status(403).end("not authorized")
        # Retornando Falsy em middlewares, apenas pare a execução do próximo middleware 
        return False

    # retorna dados extras
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

# Você pode usar um Middleware diretamente no roteador padrão
app.get('/direct',  middleware(auth, another_middie, home))

# Você pode usar um roteador Middleware para adicionar middleware a cada rota que você definir
auth_router = MiddlewareRouter(app, auth)
auth_router.get("/", home)
# Você também pode misturar middleware() com MiddlewareRouter
auth_router.get("/another", middleware(another_middie, home))

# Você também pode passar vários Middlewares no MiddlewareRouter
other_router = MiddlewareRouter(app, auth, another_middie)
other_router.get("/another_way", home)

# Você também pode usar Middlewares ao usar o roteador decorador
private = app.router("/api", auth, another_middie)

# Servirá em /api/users e usará
@private.get("/users")
def get_users(res, req, user):
   res.cork_end("Hello private API!")

app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

```

### Próximo [Basics](basics.md)
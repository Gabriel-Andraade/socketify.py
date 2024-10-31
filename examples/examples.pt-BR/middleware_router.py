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

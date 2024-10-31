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
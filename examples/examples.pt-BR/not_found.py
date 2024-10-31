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

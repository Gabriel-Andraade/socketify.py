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

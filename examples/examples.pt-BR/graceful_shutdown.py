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

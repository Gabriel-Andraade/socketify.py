from socketify import App

app = App()
app.get("/", lambda res, req: res.end("Hello World socketify from Python!")) # Defina uma rota para o aplicativo
    # Res: Mostre a resposta que foi mostrada para o cliente
    # Req: Mostre a solicitação para o cliente
    # Res.end: Exiba a resposta
app.listen(
    0, lambda config: print("Listening on port http://localhost:%d now\n" % config.port) 
)
app.run()

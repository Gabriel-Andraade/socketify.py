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

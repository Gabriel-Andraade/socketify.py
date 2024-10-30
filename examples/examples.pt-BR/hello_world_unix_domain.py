from socketify import App, AppListenOptions

app = App()
app.get("/", lambda res, req: res.end("Hello World!"))
    # Configurar servidor para socket unix
app.listen(
    AppListenOptions(domain="/tmp/test.sock"),
    lambda config: print("Listening on port %s http://localhost/ now\n" % config.domain),
)
app.run()

# Você pode testar com curl -GET --unix-socket /tmp/test.sock http://localhost/
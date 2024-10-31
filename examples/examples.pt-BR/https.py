from socketify import App, AppOptions

app = App(
    AppOptions(
        key_file_name="./misc/key.pem", # Caminho arquivo da chave privada
        cert_file_name="./misc/cert.pem", # Caminho do arquivo certificado
        passphrase="1234", # Senha
    )
        # Define uma rota para responder
)
app.get("/", lambda res, req: res.end("Hello World socketify from Python!"))
app.listen(
    54321,
    lambda config: print("Listening on port https://localhost:%d now\n" % config.port),
)
app.run()

# mkdir misc
# openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -passout pass:1234 -keyout ./misc/key.pem -out ./misc/cert.pem

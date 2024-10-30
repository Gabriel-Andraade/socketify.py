from socketify import App
import ujson

app = App()


# Defina o serializador json para json 
# O serializador json deve ter duas funções dumps e loads 
app.json_serializer(ujson)

app.get("/", lambda res, req: res.end({"Hello":"World!"}))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

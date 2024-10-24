## Enviando File e servindo Static Files
`app.static(route, path)` servirá tods os arquivos no diretório como estáticos e adionará suporte a intervalos de bytes, 304, 404
Se você quiser enviar um único arquivo, pode usar o auxiliar `sendfile` para isso

Example:
```python
from socketify import App, sendfile


app = App()


# Manda home page index.html
async def home(res, req):
    # Envia o arquivo inteiro com 304 e suporte a intervalo de bytes
    await sendfile(res, req, "./public/index.html")


app.get("/", home)

# Serve todos os arquivos na pasta pública sob a /* route (você pode utilizar qualquer route como /assets)
app.static("/", "./public")

app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

```

### Próximo [Templates](templates.md)
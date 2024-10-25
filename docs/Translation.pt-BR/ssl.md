
# SSL / HTTPS

É muito fácil passar a `key_file_name`, `cert_file_name` e `passphrase` para fazer o SSL funcionar, você também pode passar `ssl_ciphers`, `ca_file_name` para ele.

```python
from socketify import App, AppOptions

app = App(
    AppOptions(
        key_file_name="./misc/key.pem",
        cert_file_name="./misc/cert.pem",
        passphrase="1234",
    )
)
app.get("/", lambda res, req: res.end("Hello World socketify from Python!"))
app.listen(
    3000,
    lambda config: print("Listening on port https://localhost:%d now\n" % config.port),
)
app.run()
```

```python
class AppOptions:
    key_file_name: str = None,
    cert_file_name: str = None,
    passphrase: str = None,
    dh_params_file_name: str = None,
    ca_file_name: str = None,
    ssl_ciphers: str = None,
    ssl_prefer_low_memory_usage: int = 0
```
### Próximo [CLI, ASGI and WSGI](cli.md)
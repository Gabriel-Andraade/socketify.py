## Carregando ou obtendo os Posting data

### Obtendo os chunks manualmente
Usando `res.on_data` você pode pegar qualquer chunk enviado para a request.

```python
def upload(res, req):
    def on_data(res, chunk, is_end):
        print(f"Got chunk of data with length {len(chunk)}, is_end: {is_end}")
        if is_end:
            res.cork_end("Thanks for the data!")

    res.on_data(on_data)
```

### Obtendo em uma única chamada
Criamos um `res.get_data()` para obter todos os dados de uma vez internamente, ciraremos um ByteslO para você.

```python
async def upload_chunks(res, req):
    print(f"Posted to {req.get_url()}")
    # Aguarda todos os dados, retorna os chunks recebidos se falhar (provavelmente falhas são request aborted)
    data = await res.get_data()

    print(f"Got {len(data.getvalue())} bytes of data!")
    
    # Respondemos quando terminamos
    res.cork_end("Thanks for the data!")
```
### Obtendo dados utf-8/encoded
Semelhantes a `res.get_data()`, `res.get_text(encoding="utf-8")` decodificará como texto com a codificação que você deseja.
```python
async def upload_text(res, req):
    print(f"Posted to {req.get_url()}")
    # O await junta os dados e decotifica como texto, retorna None caso falhar
    text = await res.get_text()  # O primeiro parameteré a codificação (padrão utf-8)

    print(f"Your text is ${text}")

    # Respondemos quando terminamos
    res.cork_end("Thanks for the data!")
```

### Obtendo dados JSON
Semelhante a `res.get_data()`, `res.get_json()` decodificará o json como dict.
```python
async def upload_json(res, req):
    print(f"Posted to {req.get_url()}")
    # await junta todos os dados e analisa como json, retorna None caso falhar
    info = await res.get_json()

    print(info)


    # Respondemos quando terminamos
    res.cork_end("Thanks for the data!")
```

### Obtendo dados de application/x-www-form-urlencoded
Semelhante a `res.get_data()`, `res.get_form_urlencoded(encoding="utf-8")` decodificará application/x-www-form-urlencoded como dict.

```python
async def upload_urlencoded(res, req):
    print(f"Posted to {req.get_url()}")
    # await junta todos os dados e decodifica como application/x-www-form-urlencoded, retorna Mone se falhar
    form = await res.get_form_urlencoded()# Primeiro parameter é a codificação (padrão utf-8)

    print(f"Your form is ${form}")

    # Respondemos quando terminar
    res.cork_end("Thanks for the data!")
```
### Verificação de Dynamic content-type
Você sempre pode verificar o header Content-Type para a verificação Dynamic e converter em vários formatos.

```python
async def upload_multiple(res, req):
    print(f"Posted to {req.get_url()}")
    content_type = req.get_header("content-type")
    # Podemos verificar o Content-Type para aceitar vários formatos
    if content_type == "application/json":
        data = await res.get_json()
    elif content_type == "application/x-www-form-urlencoded":
        data = await res.get_form_urlencoded()
    else:
        data = await res.get_text()

    print(f"Your data is ${data}")

    # Respondemos quando terminamos
    res.cork_end("Thanks for the data!")
```

### Próximo [Streaming Data](streaming-data.md)
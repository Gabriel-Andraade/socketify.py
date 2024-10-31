from socketify import App

###
# Sempre recomendamos verificar res.aborted em operações async
###


def upload(res, req):
    # Lida com os dados simples
    print(f"Posted to {req.get_url()}")

    def on_data(res, chunk, is_end):
        # Callback com um vhunk de dados recebido 
        print(f"Got chunk of data with length {len(chunk)}, is_end: {is_end}") # Mostrar tamanho do chunk recebido 
        if is_end:
            res.cork_end("Thanks for the data!") # Responder o cliente quando receber todos os dados

    res.on_data(on_data) # Registrar função de callback para receber dados


async def upload_chunks(res, req):
    print(f"Posted to {req.get_url()}") # Mostrar upload de URL
    # Aguardar todos os dados, retornar os chunks recebidos se falhar (provavelmente a falha é de aborted request)
    data = await res.get_data() # Aguarda todos os dados recebidos

    print(f"Got {len(data.getvalue())} bytes of data!")  # Mostra o tamanho máximo
    
    # Responde quando terminamos
    res.cork_end("Thanks for the data!")


async def upload_json(res, req):
    print(f"Posted to {req.get_url()}")
    # Aguarda todos os dados e analisa como json, retorna false se falhar
    info = await res.get_json() # Aguarda e analisa os dados como json

    print(info)
    
    # Respondemos quando terminamos
    res.cork_end("Thanks for the data!")


async def upload_text(res, req):
    # Manipule de função async com upload
    print(f"Posted to {req.get_url()}")
    # Aguarda todos os dados e decodifica como text, retorna None se falhar
    text = await res.get_text()  # O primeiro parâmetro é a codificação (Padrão  utf-8)

    print(f"Your text is {text}") # Mostra o texto recebido 

    # Respondemos quando terminarmos 
    res.cork_end("Thanks for the data!")


async def upload_urlencoded(res, req):
    print(f"Posted to {req.get_url()}")
    # Aguarde todos os dados e decodifica como application/x-www-form-urlencode, retorna None se falhar
    form = (
        await res.get_form_urlencoded()
    )  # O primeiro parâmetro é a codficação (padrão utf-8)

    print(f"Your form is {form}") # Mostra os dados do formulário recebidos

    # Respodemos quando terminarmos 
    res.cork_end("Thanks for the data!")


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

    print(f"Your data is {data}") # Mostrar dados recebidos

    # Respondemos quando terminarmos
    res.cork_end("Thanks for the data!") # Responder quando todos os dados forem entregues

def upload_formdata(res, req):
    # Usando o pacote streaming_form_data para análise
    from streaming_form_data import StreamingFormDataParser # analisar os dados em tempo real
    from streaming_form_data.targets import ValueTarget, FileTarget

    print(f"Posted to {req.get_url()}")
    parser = StreamingFormDataParser(headers=req.get_headers())
    name = ValueTarget()
    parser.register('name', name)
    file = FileTarget('/tmp/file')
    file2 = FileTarget('/tmp/file2')
    parser.register('file', file)
    parser.register('file2', file2)


    def on_data(res, chunk, is_end):   
        parser.data_received(chunk)
        if is_end:
            res.cork(on_finish)


    def on_finish(res):
        print(name.value)
        
        print(file.multipart_filename)
        print(file.multipart_content_type)

        print(file2.multipart_filename)
        print(file2.multipart_content_type)

        res.end("Thanks for the data!")

    res.on_data(on_data)


async def upload_formhelper(res, req):
    # Usando o pacote streaming_form_data para análise + auxiliar
    from streaming_form_data import StreamingFormDataParser
    from streaming_form_data.targets import ValueTarget, FileTarget
    from helpers.form_data import get_formdata


    print(f"Posted to {req.get_url()}")
        # Cria um parser para processar dados de formulários multipart a partir dos headers do request
    parser = StreamingFormDataParser(headers=req.get_headers())
    name = ValueTarget()
    parser.register('name', name)
    file = FileTarget('/tmp/file')
    file2 = FileTarget('/tmp/file2')
    parser.register('file', file)
    parser.register('file2', file2)

    await get_formdata(res, parser)

    print(name.value)
    
    print(file.multipart_filename)
    print(file.multipart_content_type)

    print(file2.multipart_filename)
    print(file2.multipart_content_type)

    res.cork_end("Thanks for the data!")


app = App()
app.post("/", upload) # simple upload route
app.post("/chunks", upload_chunks) # chunk upload route
app.post("/json", upload_json) # json upload route 
app.post("/text", upload_text) # text upload route
app.post("/urlencoded", upload_urlencoded) # Codificado URL upload route
app.post("/multiple", upload_multiple) # multiple upload route
app.post("/formdata", upload_formdata) #  data form upload route
app.post("/formdata2", upload_formhelper) # formhelper upload route

app.any("/*", lambda res, _: res.write_status(404).end("Not Found"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

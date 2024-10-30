from socketify import App
import aiofiles
import time
import mimetypes
import os
from os import path
    # Precisa importar esses tipos de biblioteca
    
mimetypes.init()
    # Habilita o tipo "MIME"

async def home(res, req):
    # Este é apenas um exemplo de implementação, veja o exemplo static_files.py para uso de sendfilr e app.static
    # Há um auxiliar static_aiofile.py e um auxiliar static.aiofiles usando a implementação async disto
    # Async com IO é muito lento, então implementaremos "aiofile" usando libuv dentro do socketify no futuro (:

    # Defina o caminho do arquivo a ser servido
    filename = "./public/media/flower.webm"
    
    # Leia os header antes do primeiro await
    if_modified_since = req.get_header("if-modified-since")
    range_header = req.get_header("range")
    bytes_range = None
    start = 0
    end = -1
    # Analisar header em intervalo
    if range_header:
        bytes_range = range_header.replace("bytes=", "").split("-")
        start = int(bytes_range[0])
        if bytes_range[1]: # Verificar se o intervalo final foi especificado
            end = int(bytes_range[1])
    try:
        exists = path.exists(filename) # Verificar se o arquivo existe
        
        # Se não for encontrado
        if not exists:
            return res.write_status(404).end(b"Not Found") # Mostrar isto se não for encontrado

        # Obter tamanho e data da última modificação
        stats = os.stat(filename)
        total_size = stats.st_size
        size = total_size
        last_modified = time.strftime(
            "%a, %d %b %Y %H:%M:%S GMT", time.gmtime(stats.st_mtime)
        )

        # Verifique se está modificado desde que é fornecido 
        if if_modified_since == last_modified:
            return res.write_status(304).end_without_body() # Irá mostrar isso sem nem ter modificado 
        
        # Informa ao navegador a data da última modificação feita
        res.write_header(b"Last-Modified", last_modified)

        # Adicione o tipo de conteúdo
        (content_type, encoding) = mimetypes.guess_type(filename, strict=True)
        if content_type and encoding:
            res.write_header(b"Content-Type", "%s; %s" % (content_type, encoding))
        elif content_type:
            res.write_header(b"Content-Type", content_type)

        with open(filename, "rb") as fd: # Abra o arquivo
            # Verifique o intervalo e suporte-o
            if start > 0 or not end == -1:
                if end < 0 or end >= size:
                    end = size - 1
                size = end - start + 1
                fd.seek(start)  # Mova o arquivo para o intervalo inicial 
                if start > total_size or size > total_size or size < 0 or start < 0:
                    return res.write_status(416).end_without_body() # Retorna 416 se o intervalo não for válido
                res.write_status(206) # Retorne 206 caso for um intervalo parcial 
            else:
                end = size - 1
                res.write_status(200) # Retornará 200 caso o intervalo for bem sucedido 
                # Se você quiser, você pode trocar a numeração :)

            # Informe ao navegador que oferecemos suporte a intervalo
            res.write_header(b"Accept-Ranges", b"bytes")
            res.write_header(
                b"Content-Range", "bytes %d-%d/%d" % (start, end, total_size)
            )
            pending_size = size
            # Continue enviando até cancelar(aborted) ou terminar(done)
            while not res.aborted:
                chunk_size = 16384  # Tamanho de 16kb
                if chunk_size > pending_size:
                    chunk_size = pending_size
                buffer = fd.read(chunk_size) # isso aqui lê o pedaço do arquivo  
                pending_size = pending_size - chunk_size # Aqui atualiza o tamanho do arquivo 
                (ok, done) = await res.send_chunk(buffer, size)
                if not ok or done:  # não é possivel enviar porque provavelmente foi aborted
                    break

    except Exception as error:
        res.write_status(500).end("Internal Error") # Retorna 500 caso der erro


app = App() # Cria um novo app
app.get("/", home)
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

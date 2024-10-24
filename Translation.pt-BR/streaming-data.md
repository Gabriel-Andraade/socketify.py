# Streaming data
Você nunca deve chamar `res.end(huge buffer)`. `res.end` garante o envio, então a pressão de retorno provavelmente aumentará. Em vez disso, você deve usar `res.try_end` para transmitir dados enormes parte por parte. Use em combinação com os callbacks `res.on_writable` e `res.on_aborted`.
Para simplificar, você pode usar `res.send_chunk`, isso retornará um Future e usará `res.on_writable` e `res.on_aborted` para você.

Usando send_chunk:

```python
async def home(res, req):
    res.write_header("Content-Type", "audio/mpeg")
   
    filename = "./file_example_MP3_5MG.mp3"
    total = os.stat(filename).st_size
    
    async with aiofiles.open(filename, "rb") as fd:
        while not res.aborted:
            buffer = await fd.read(16384)  #16kb buffer
            (ok, done) = await res.send_chunk(buffer, total)
            if not ok or done: #if cannot send probably aborted
                break 
```

If you want to understand `res.send_chunk`, check out the implementation:
```python
def send_chunk(self, buffer, total_size):
        self._chunkFuture = self.loop.create_future()
        self._lastChunkOffset = 0

        def is_aborted(self):
            self.aborted = True
            try:
                if not self._chunkFuture.done():
                    self._chunkFuture.set_result(
                        (False, True)
                    )  # Se aborted for definido como done True e ok False
            except:
                pass

        def on_writeble(self, offset):
            # Aqui o tempo limite está desativado, podemos gastar o tempo que quisermos antes de chamar try_end
            (ok, done) = self.try_end(
                buffer[offset - self._lastChunkOffset : :], total_size
            )
            if ok:
                self._chunkFuture.set_result((ok, done))
            return ok

        self.on_writable(on_writeble)
        self.on_aborted(is_aborted)

        if self.aborted:
            self._chunkFuture.set_result(
                (False, True)
            )  # se aborted for definido como done True e ok False
            return self._chunkFuture

        (ok, done) = self.try_end(buffer, total_size)
        if ok:
            self._chunkFuture.set_result((ok, done))
            return self._chunkFuture
        # falhou em enviar ao chunk
        self._lastChunkOffset = self.get_write_offset()

        return self._chunkFuture
```

### Próximo [Send File and Static Files](static-files.md)
from socketify import App

###
# We always recommend check res.aborted in async operations
###


def upload(res, req):
    # handle with simple upload data
    print(f"Posted to {req.get_url()}")

    def on_data(res, chunk, is_end):
        # callback called with a data chunk is received
        print(f"Got chunk of data with length {len(chunk)}, is_end: {is_end}") # show chunk size
        if is_end:
            res.cork_end("Thanks for the data!") # respond client when all datas is receive

    res.on_data(on_data) # register function callback for receive data


async def upload_chunks(res, req):
    print(f"Posted to {req.get_url()}") # show upload of URL 
    # await all the data, returns received chunks if fail (most likely fail is aborted requests)
    data = await res.get_data() # await all received data 

    print(f"Got {len(data.getvalue())} bytes of data!")  # show the maximum size
    
    # We respond when we are done
    res.cork_end("Thanks for the data!")


async def upload_json(res, req):
    print(f"Posted to {req.get_url()}")
    # await all the data and parses as json, returns None if fail
    info = await res.get_json() # await and analyzes datas like json

    print(info)
    
    # We respond when we are done
    res.cork_end("Thanks for the data!")


async def upload_text(res, req):
    # async function handle with upload
    print(f"Posted to {req.get_url()}")
    # await all the data and decode as text, returns None if fail
    text = await res.get_text()  # first parameter is the encoding (default utf-8)

    print(f"Your text is {text}") # show you text received

    # We respond when we are done
    res.cork_end("Thanks for the data!")


async def upload_urlencoded(res, req):
    print(f"Posted to {req.get_url()}")
    # await all the data and decode as application/x-www-form-urlencoded, returns None if fails
    form = (
        await res.get_form_urlencoded()
    )  # first parameter is the encoding (default utf-8)

    print(f"Your form is {form}") # show form data received

    # We respond when we are done
    res.cork_end("Thanks for the data!")


async def upload_multiple(res, req):
    print(f"Posted to {req.get_url()}")
    content_type = req.get_header("content-type")
    # we can check the Content-Type to accept multiple formats
    if content_type == "application/json":
        data = await res.get_json()
    elif content_type == "application/x-www-form-urlencoded":
        data = await res.get_form_urlencoded()
    else:
        data = await res.get_text()

    print(f"Your data is {data}") # show received data

    # We respond when we are done
    res.cork_end("Thanks for the data!") # respond when all datas is received

def upload_formdata(res, req):
    # using streaming_form_data package for parsing
    from streaming_form_data import StreamingFormDataParser #
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
    # using streaming_form_data package for parsing + helper
    from streaming_form_data import StreamingFormDataParser
    from streaming_form_data.targets import ValueTarget, FileTarget
    from helpers.form_data import get_formdata


    print(f"Posted to {req.get_url()}")
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
app.post("/urlencoded", upload_urlencoded) # codified URL upload route
app.post("/multiple", upload_multiple) # multiple upload route
app.post("/formdata", upload_formdata) #  data form upload route
app.post("/formdata2", upload_formhelper) # formhelper upload route

app.any("/*", lambda res, _: res.write_status(404).end("Not Found"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

from socketify import App
import aiofiles
import time
import mimetypes
import os
from os import path
    # Nedd to import this types of Library
    
mimetypes.init()
    # Enable the type "MIME"

async def home(res, req):
    # This is just an implementation example see static_files.py example for use of sendfile and app.static usage
    # There is an static_aiofile.py helper and static.aiofiles helper using async implementation of this
    # Asyncio with IO is really slow so, we will implement "aiofile" using libuv inside socketify in future

    # Set the path of the archive to be served
    filename = "./public/media/flower.webm"
    
    # Read headers before the first await
    if_modified_since = req.get_header("if-modified-since")
    range_header = req.get_header("range")
    bytes_range = None
    start = 0
    end = -1
    # parse range header
    if range_header:
        bytes_range = range_header.replace("bytes=", "").split("-")
        start = int(bytes_range[0])
        if bytes_range[1]: # Verify if final range is specified
            end = int(bytes_range[1])
    try:
        exists = path.exists(filename) # Verify if the archive exist
        
        # If not found 
        if not exists:
            return res.write_status(404).end(b"Not Found") # Show this if not found

        # get size and last modified date
        stats = os.stat(filename)
        total_size = stats.st_size
        size = total_size
        last_modified = time.strftime(
            "%a, %d %b %Y %H:%M:%S GMT", time.gmtime(stats.st_mtime)
        )

        # check if modified since is provided
        if if_modified_since == last_modified:
            return res.write_status(304).end_without_body() # Show this if not even modified
        
        # tells the browser the last modified date
        res.write_header(b"Last-Modified", last_modified)

        # add content type
        (content_type, encoding) = mimetypes.guess_type(filename, strict=True)
        if content_type and encoding:
            res.write_header(b"Content-Type", "%s; %s" % (content_type, encoding))
        elif content_type:
            res.write_header(b"Content-Type", content_type)

        with open(filename, "rb") as fd: # Open the archive 
            # check range and support it
            if start > 0 or not end == -1:
                if end < 0 or end >= size:
                    end = size - 1
                size = end - start + 1
                fd.seek(start)  # Move the archive for beginning range 
                if start > total_size or size > total_size or size < 0 or start < 0:
                    return res.write_status(416).end_without_body() # Return 416 if range is not valid
                res.write_status(206) # Return 206 for partial range
            else:
                end = size - 1
                res.write_status(200) # Return for success Range
                # If you want, you cant switch the number! :)

            # tells the browser that we support range
            res.write_header(b"Accept-Ranges", b"bytes")
            res.write_header(
                b"Content-Range", "bytes %d-%d/%d" % (start, end, total_size)
            )
            pending_size = size
            # keep sending until abort or done
            while not res.aborted:
                chunk_size = 16384  # Size of: 16kb chunks
                if chunk_size > pending_size:
                    chunk_size = pending_size
                buffer = fd.read(chunk_size) # Read the chunk of archive 
                pending_size = pending_size - chunk_size # Update chunk size 
                (ok, done) = await res.send_chunk(buffer, size)
                if not ok or done:  # if cannot send probably aborted
                    break

    except Exception as error:
        res.write_status(500).end("Internal Error") # Return 500 for error


app = App() # Create a new application
app.get("/", home)
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

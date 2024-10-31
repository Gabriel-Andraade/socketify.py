# Examples

Router_and_basics
```python
from socketify import App, AppOptions, AppListenOptions
import asyncio
from datetime import datetime, timedelta

app = App()

def home(res, req):
    res.end("Hello :)")

def anything(res, req):
    res.end("Any route with method: %s" % req.get_method())

def cookies(res, req):
    # cookies are written after end
    res.set_cookie(
        "spaciari",
        "1234567890",
        {
            # expires
            # path
            # comment
            # domain
            # max-age
            # secure
            # version
            # httponly
            # samesite
            "path": "/",
            # "domain": "*.test.com",
            "httponly": True,
            "samesite": "None",
            "secure": True,
            "expires": datetime.utcnow() + timedelta(minutes=30),
        },
    )
    res.end("Your session_id cookie is: %s" % req.get_cookie("session_id"))

    # Show the type of user
def useragent(res, req):
    res.end("Your user agent is: %s" % req.get_header("user-agent"))

def user(res, req):
    try:
        if int(req.get_parameter(0)) == 1:
            return res.end("Hello user with id 1!")
        # get_parameters returns an array of parameters
        # params = req.get_parameters()

    finally:
        # invalid user tells to go, to the next route valid route (not found)
        req.set_yield(1)

async def delayed_hello(delay, res):
    await asyncio.sleep(delay)  # do something async
    res.cork_end("Hello sorry for the delay!")
    # cork_end is a less verbose way of writing
    # res.cork(lambda res: res.end("Hello sorry for the delay!"))

def delayed(res, req):
    # request object only lives during the life time of this call
    # get parameters, query, headers anything you need here
    delay = req.get_query("delay")
    delay = 1 if delay == None else float(delay)

    # get queries returns an dict with all query string
    # queries = req.get_queries()

    # tell response to run this in the event loop
    # abort handler is grabbed here, so responses only will be send if res.aborted == False
    res.run_async(delayed_hello(delay, res))

def json(res, req):
    # if you pass an object will auto write an header with application/json
    res.end({"message": "I'm an application/json!"})

async def sleepy_json(res, req):
    # get parameters, query, headers anything you need here before first await :)
    user_agent = req.get_header("user-agent")
    # print all headers
    req.for_each_header(lambda key, value: print("Header %s: %s" % (key, value)))
    # or if you want get all headers in an dict
    print("All headers", req.get_headers())

    # req maybe will not be available in direct attached async functions after await
    # but if you dont care about req info you can do it
    await asyncio.sleep(2)  # do something async
    res.cork_end({"message": "I'm delayed!", "user-agent": user_agent})

def custom_header(res, req):
    res.write_header("Content-Type", "application/octet-stream")
    res.write_header("Content-Disposition", 'attachment; filename="message.txt"')
    res.end("Downloaded this ;)")

def send_in_parts(res, req):
    # write and end accepts bytes and str or its try to dumps to an json
    res.write("I can")
    res.write(" send ")
    res.write("messages")
    res.end(" in parts!")

def redirect(res, req):
    # status code is optional default is 302
    res.redirect("/redirected", 302)

def redirected(res, req):
    res.end("You got redirected to here :D")

def not_found(res, req):
    res.write_status(404).end("Not Found")

# app.any, app.get, app.put, app.post, app.head, app.options, app.delete, app.patch, app.connect and app.trace are available
app.get("/", home)
app.any("/anything", anything)
app.get("/user/agent", useragent)
app.get("/user/:id", user)
app.get("/delayed", delayed)
app.get("/json", json)
app.get("/sleepy", sleepy_json)
app.get("/custom_header", custom_header)
app.get("/cookies", cookies)
app.get("/send_in_parts", send_in_parts)
app.get("/redirect", redirect)
app.get("/redirected", redirected)
# too see about app.post go to ./upload_or_post.py :D
# Wildcard at last always :)
app.any("/*", not_found)

app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)
app.run()
```

Middleware
```python
from socketify import App, middleware

        # if user have authorization, return a message 
async def get_user(authorization):
    if authorization:
        # you can do something async here
        return {"greeting": "Hello, World"}
    return None

    # verify if user is authorized with middleware authorized 
async def auth(res, req, data=None):
    user = await get_user(req.get_header("authorization"))
    if not user:
        res.write_status(403).end("not authorized")
        # returning Falsy in middlewares just stop the execution of the next middleware and show a message error '403'
        return False

    # returns extra data
    return user

    # other middleware switch the greeting
def another_middie(res, req, data=None):
    # now we can mix sync and async and change the data here
    if isinstance(data, dict):
        gretting = data.get("greeting", "")
        data["greeting"] = f"{gretting} from another middie ;)"
    return data


def home(res, req, user=None):
    res.cork_end(user.get("greeting", None))


app = App()
app.get("/", middleware(auth, another_middie, home))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

# You can also take a loop on MiddlewareRouter in middleware_router.py ;)
 ```

Middleware_async
```python
from socketify import App

# this is just an example of implementation you can just import using from socketify import middleware for an more complete version
# Here you see what you can do for authentication of valid user

async def get_user(authorization):
    if authorization: # Verify if exist authorization
        # do actually something async here
        return {"greeting": "Hello, World"} # Return one dict 
    return None # Return none if dont have authorization

def auth(route):
    # in async query string, arguments and headers are only valid until the first await
    async def auth_middleware(res, req):
        # get_headers will preserve headers (and cookies) inside req, after await
        headers = req.get_headers()
        # get_parameters will preserve all params inside req after await
        params = req.get_parameters()
        # get queries will preserve all queries inside req after await
        queries = req.get_queries()
        # or just use req.preserve() to preserve all

        user = await get_user(headers.get("authorization", None)) # Verify authorization 
        if user: # If user is authorized, call the route
            return route(res, req, user)

        return res.write_status(403).cork_end("not authorized") # return 403'error' if not authorized

    return auth_middleware # Return in middleware mode

def home(res, req, user=None):
    theme = req.get_query("theme_color") # Set query theme color
    theme = theme if theme else "light" # Set the type of theme
    greeting = user.get("greeting", None) # Set type of greeting
    user_id = req.get_parameter(0) # Get the user ID route
    res.cork_end(f"{greeting} <br/> theme: {theme} <br/> id: {user_id}") # Send the answer

app = App() # Create new application
app.get("/user/:id", auth(home)) # Set route with authentication middleware
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

# curl --location --request GET 'http://localhost:3000/user/10?theme_color=dark' --header 'Authorization: Bearer 23456789'
```

middleware_router
```python
from socketify import App, MiddlewareRouter, middleware

    # Here you sets up a web application with middleware for authentication and data manipulation. It uses a MiddlewareRouter to manage routes and allows multiple middlewares to be applied to each route,
        # returning greetings or custom messages depending on authentication.


async def get_user(authorization):
    if authorization:
        # you can do something async here :)
        return {"greeting": "Hello, World"}
    return None

async def auth(res, req, data=None):
    # authentication middleware
    user = await get_user(req.get_header("authorization")) # Verify authentication 
    if not user: # If not authorized (obviously)
        res.write_status(403).end("not authorized") # Show the error number "403" if not
        # returning Falsy in middlewares just stop the execution of the next middleware
        return False

    # returns extra data
    return user


def another_middie(res, req, data=None):
    # now we can mix sync and async and change the data here
    if isinstance(data, dict):
        gretting = data.get("greeting", "") # Pick the greeting
        data["greeting"] = f"{gretting} from another middie ;)" # You can also chance the greeting
    return data # return modified data


def home(res, req, user=None):
    res.cork_end(user.get("greeting", None))


app = App()

# you can use an Middleware router to add middlewares to every route you set
auth_router = MiddlewareRouter(app, auth)
auth_router.get("/", home)
# you can also mix middleware() with MiddlewareRouter
auth_router.get("/another", middleware(another_middie, home))

# you can also pass multiple middlewares on the MiddlewareRouter
other_router = MiddlewareRouter(app, auth, another_middie)
other_router.get("/another_way", home) # Set other route with middleware


app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

middleware_sync
```python

from socketify import App

# this is just an example of implementation you can just import using from socketify import middleware for an more complete version

    # Set a custom middleware function that accepts multiple middleware function
def middleware(*functions):
    
    def middleware_route(res, req):
        data = None
        # cicle to all middlewares
        for function in functions:
            # call all middlewares
            data = function(res, req, data)
            # stops if returns Falsy
            if not data:
                break

    return middleware_route

     # this function verify user authorization 

def get_user(authorization_header):
    if authorization_header:
        return {"greeting": "Hello, World"}
    return None

     # this middleware authentication checks whether it has an authorized user      
def auth(res, req, data=None):
    user = get_user(req.get_header("authorization"))
    if not user:
        res.write_status(403).end("not authorized") # return error '403' if not authorized
        return False

    # returns extra data
    return user

    # main function for greeting users
def home(res, req, user=None):
    res.end(user.get("greeting", None))

app = App()
app.get("/", middleware(auth, home))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

Broadcast

```python
from socketify import App, AppOptions, OpCode, CompressOptions


def ws_open(ws):
    print("A WebSocket got connected!") # show amessage when one conection WebSocket is set
    # Let this client listen to topic "broadcast"
    ws.subscribe("broadcast")


def ws_message(ws, message, opcode): # Show the message for  wall clients in topic "Broadcast"
    # Broadcast this message
    ws.publish("broadcast", message, opcode) 

app = App()
app.ws(
    "/*", # Define this application for all routes
    {
        "compression": CompressOptions.SHARED_COMPRESSOR,
        "max_payload_length": 16 * 1024 * 1024, # Max size of payload
        "idle_timeout": 60, #   Max time 
        "open": ws_open, # Define the function to be called when opening a connection
        "message": ws_message, # Define the function to be called when receiving a message
        # The library guarantees proper unsubscription at close
        "close": lambda ws, code, message: print("WebSocket closed"), # Show a message when closed the connection
        "subscription": lambda ws, topic, subscriptions, subscriptions_before: print(f'subscription/unsubscription on topic {topic} {subscriptions} {subscriptions_before}'),
        # Register change of inscription
    },
)
app.any("/", lambda res, req: res.end("Nothing to see here!"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()
```

HTTPS
```python
from socketify import App, AppOptions

app = App(
    AppOptions(
        key_file_name="./misc/key.pem", # private key file path
        cert_file_name="./misc/cert.pem", # certificate file path
        passphrase="1234", # private key password
    )
        # Set a route to respond
)
app.get("/", lambda res, req: res.end("Hello World socketify from Python!"))
app.listen(
    54321,
    lambda config: print("Listening on port https://localhost:%d now\n" % config.port),
)
app.run()

# mkdir misc
# openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -passout pass:1234 -keyout ./misc/key.pem -out ./misc/cert.pem
```

Backpressure
```python
from socketify import App, AppOptions, OpCode, CompressOptions

# Number between ok and not ok
backpressure = 1024

# Used for statistics
messages = 0
message_number = 0


def ws_open(ws):
    print("A WebSocket got connected!")
    # We begin our example by sending until we have backpressure
    global message_number
    global messages
    while ws.get_buffered_amount() < backpressure:
        ws.send("This is a message, let's call it %i" % message_number)
        message_number = message_number + 1
        messages = messages + 1


def ws_drain(ws):
    # Continue sending when we have drained (some)
    global message_number
    global messages
    while ws.get_buffered_amount() < backpressure:
        ws.send("This is a message, let's call it %i" % message_number)
        message_number = message_number + 1
        messages = messages + 1
    # This function is called all time when buffer is empty,allowing the server for sending message again until the limit

app = App()
app.ws(
    "/*",
    {
        "compression": CompressOptions.DISABLED,
        "max_payload_length": 16 * 1024 * 1024, # Max size payload
        "idle_timeout": 60, # Max time 
        "open": ws_open, # Define the open event
        "drain": ws_drain, # Define the drain event
    },
)
app.any("/", lambda res, req: res.end("Nothing to see here!"))
    # Define one route for all other request, it sends a message 
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()
```

Better_logging
```python

# This example just show how to use python logging to log requests

from socketify import App
import logging
# Setup log format
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO
)

# simply devlog high-order function, you can also create an middleware to use logging, see middleware_router.py and middleware.py
def devlog(handler):
    def devlog_route(res, req):
        logging.info(f'{req.get_method()} {req.get_full_url()} {req.get_headers()=}')
        handler(res, req)
    return devlog_route

# Now is just use the devlog function or middleware

app = App()

def home(res, req):
    res.end("Hello World!") # Answer for the route

app.get("/", devlog(home)) # Apply o logging in route

app.listen(
    3000,
    lambda config: logging.info("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

custom_json_serializer
```python
from socketify import App
import ujson

app = App()

# set json serializer to ujson
# json serializer must have dumps and loads functions
app.json_serializer(ujson)

app.get("/", lambda res, req: res.end({"Hello":"World!"}))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

Error_handler
```python
from socketify import App, AppOptions, AppListenOptions
import asyncio

app = App()

def xablau(res, req):
    raise RuntimeError("Xablau!")

    # Set Async if you get an error
async def async_xablau(res, req):
    raise RuntimeError("Async Xablau!")

# this can be async no problems
@app.on_error
def on_error(error, res, req):
    # here you can log properly the error and do a response for you client
    print("Somethind goes %s" % str(error))
    # response and request can be None if the error is in an async function
    if res != None:
        # if response exists try to send something
        res.write_status(500)
        res.end("Sorry we did something wrong")

        # Show the message in terminal when can execute, just xablau!
app.get("/", xablau)
app.get("/async", async_xablau)

# you can also use set_error_handler
# app.set_error_handler(on_error)

app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)
app.run()
```

File_stream
```python
from socketify import App
import aiofiles
import time
import mimetypes
import os
from os import path
    # Need to import this types of Library
    
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
```

graceful_shutdown
```python
from socketify import App, AppOptions, AppListenOptions

app = App()

    # Set a shutdown function that will be called when a client accesses the shutdown entity 
def shutdown(res, req):
    res.end("Good bye!") # Send a response to the client
    app.close() # Close the app after sending the response

    # Set main route "/" when return to the client
app.get("/", lambda res, req: res.end("Hello!"))
    # Set "/shutdown" route to perform the shutdowmn function 
app.get("/shutdown", shutdown)

app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)
app.run()
print("App Closed!")
```

graphiql_raw
```python
import dataclasses
import strawberry  # Used for to Set schema from GraphQL and create tips
import strawberry.utils.graphiql # Tool for web interface 

from socketify import App
from typing import List, Optional


    # Set type of class called 
@strawberry.type
class User:
    name: str


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> Optional[User]:
        return User(name="Hello")

    # Creates schema GraphQL from the query class
schema = strawberry.Schema(Query)

    # Set async function to handle requests POST in GraphiQL
async def graphiql_post(res, req):
    # we can pass whatever we want to context, query, headers or params, cookies etc
    context_value = req.preserve()

    # get all incoming data and parses as json
    body = await res.get_json()
    # extracts the query and possible input variables
    query = body["query"]
    variables = body.get("variables", None)
    root_value = body.get("root_value", None)
    operation_name = body.get("operation_name", None)
    # execute the query GraphQL using schema
    data = await schema.execute(
        query,
        variables,
        context_value,
        root_value,
        operation_name,
    )
    # send a response JSON for the client with datas, errors and extensios
    res.cork_end(
        {
            "data": (data.data),
            **({"errors": data.errors} if data.errors else {}),
            **({"extensions": data.extensions} if data.extensions else {}),
        }
    )

    # Configure the server using the app library
app = App()
    # Route GET we return GraphiQL interface HTML for a facility test
app.get("/", lambda res, req: res.end(strawberry.utils.graphiql.get_graphiql_html()))
    # Post route to process GraphQL querys using graphiql_post function
app.post("/", graphiql_post)
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

graphiql
```python
import dataclasses
import strawberry
import strawberry.utils.graphiql

from socketify import App
from typing import List, Optional
from helpers.graphiql import graphiql_from

    # Define User type for GraphQL, with camp "name"
@strawberry.type
class User:
    name: str

    # Set the query clas as entry point for GraphQL 
@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> Optional[User]:
        # self.context is the AppRequest, have datas of request
        return User(name="Hello")

app = App()
    # Set route GET for GraphiQL queries, returning HTML for the browser
app.get("/", lambda res, req: res.end(strawberry.utils.graphiql.get_graphiql_html()))
    # set route POST for proccess GraphQL queries, using function graphiql_from 
app.post("/", graphiql_from(Query))
# you can also pass an Mutation as second parameter
# app.post("/", graphiql_from(Query, Mutation))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

http_request_cache
```python
from socketify import App
import redis
import aiohttp
import asyncio
from helpers.twolevel_cache import TwoLevelCache # Import two level of caches

# create redis poll + connections
redis_pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
redis_connection = redis.Redis(connection_pool=redis_pool)
# 2 LEVEL CACHE (Redis to share among workers, Memory to be much faster)
# cache in memory is 30s, cache in redis is 60s duration
cache = TwoLevelCache(redis_connection, 30, 60)

# Model
    # Function async to fetch data from a specific Pokémon using PokeAPI
async def get_pokemon(number):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://pokeapi.co/api/v2/pokemon/{number}"
        ) as response:
            pokemon = await response.text() # Response with text 
            # cache only works with strings/bytes
            # we will not change nothing here so no needs to parse json
            return pokemon.encode("utf-8")

    # Function async for fetch one list for 151 pokémon originals
async def get_original_pokemons():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://pokeapi.co/api/v2/pokemon?limit=151"
        ) as response:
            # cache only works with strings/bytes
            # we will not change nothing here so no needs to parse json
            pokemons = await response.text()
            return pokemons.encode("utf-8") # Convert text in bytes for cache 

# Routes
    # function for list original pokemon with cache
def list_original_pokemons(res, req):

    # check cache for faster response
    value = cache.get("original_pokemons") # Verify cache for datas 
    if value != None:
        return res.end(value) # Respond with available cache

    # get asynchronous from Model
    async def get_originals():
        value = await cache.run_once("original_pokemons", 5, get_original_pokemons)
        res.cork_end(value) # Send answer with datas

    res.run_async(get_originals())  # execution function async

    # Function search and list specific pokémon by number with cache
def list_pokemon(res, req):

    # get needed parameters
    try:
        number = int(req.get_parameter(0))
    except:
        # invalid number
        return req.set_yield(1)

    # check cache for faster response
    cache_key = f"pokemon-{number}" # create a key of specific cache for a pokémon 
    value = cache.get(cache_key) # Verify a cache
    if value != None:
        return res.end(value) # respond with cache if available

    # Function async for search datas of a pokemon if not have in cache
    async def find_pokemon(number, res):
        # sync with redis lock to run only once
        # if more than 1 worker/request try to do this request, only one will call the Model and the others will get from cache
        value = await cache.run_once(cache_key, 5, get_pokemon, number)
        res.cork_end(value) # send a response with datas

    res.run_async(find_pokemon(number, res)) # execute function async

# Here i decided to use an sync first and async only if needs, but you can use async directly see ./async.py
app = App()
app.get("/", list_original_pokemons) # Route for a list of 151 pokémon original 
app.get("/:number", list_pokemon) # Dynamic route for search specific pokémon
app.any("/*", lambda res, _: res.write_status(404).end("Not Found"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

https
```python
from socketify import App, AppOptions

app = App(
    AppOptions(
        key_file_name="./misc/key.pem", # private key file path
        cert_file_name="./misc/cert.pem", # certificate file path
        passphrase="1234", # private key password
    )
        # Set a route to respond
)
app.get("/", lambda res, req: res.end("Hello World socketify from Python!"))
app.listen(
    54321,
    lambda config: print("Listening on port https://localhost:%d now\n" % config.port),
)
app.run()

# mkdir misc
# openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -passout pass:1234 -keyout ./misc/key.pem -out ./misc/cert.pem
```

listen_options
```python
from socketify import App, AppListenOptions

app = App()

    # Set rote in root "/" that responds "Hello World socketify from Python!"
app.get("/", lambda res, req: res.end("Hello World socketify from Python!"))
app.listen(
    AppListenOptions(port=3000, host="0.0.0.0"),
    lambda config: print(
        "Listening on port http://%s:%d now\n" % (config.host, config.port)
    ),
)
app.run()
```

not_found
```python
from socketify import App, AppOptions, AppListenOptions

app = App()

 # main route respond with async 
async def home(res, req):
    res.end("Hello, World!")

def user(res, req):
    try:
        if int(req.get_parameter(0)) == 1: # check the user
            return res.end("Hello user 1!") # respond only the 'user 1'
    finally:
        # invalid user tells to go, to the next route valid route (not found)
        req.set_yield(1)

        # when invalid user try, show the error '404'(not found ):)
def not_found(res, req):
    res.write_status(404).end("Not Found ):")

        # configure routes
app.get("/", home)
app.get("/user/:user_id", user)
app.any("/*", not_found)

app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)
app.run()
```

Proxy
```python
from socketify import App

    # just to display the IP
def home(res, req):
    res.write("<html><h1>")
    res.write("Your proxied IP is: %s" % res.get_proxied_remote_address()) # show the proxy IP server
    res.write("</h1><h1>")
    res.write("Your IP as seen by the origin server is: %s" % res.get_remote_address()) # show the origin IP
    res.end("</h1></html>")

app = App()
app.get("/*", home)
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

Template_jinja2
```python
from socketify import App

# see helper/templates.py for plugin implementation
from helpers.templates import Jinja2Template

 # here give the setting for jinja2
app = App()
app.template(Jinja2Template("./templates", encoding="utf-8", followlinks=False))

 # configure the settings for render the template of jinja2
def home(res, req):
    res.render("jinja2_home.html", title="Hello", message="Hello, World")

 # set one route for "/" to execute function "home"
app.get("/", home)
app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)
app.run()
```

template_mako
```python
from socketify import App

# see helper/templates.py for plugin implementation
from helpers.templates import MakoTemplate

 # here give the setting for mako
app = App()
app.template(
    MakoTemplate(
        directories=["./templates"], output_encoding="utf-8", encoding_errors="replace"
    )
)

 # configure the setting for render the template of mako
def home(res, req):
    res.render("mako_home.html", message="Hello, World")

 # set one route for "/" to execute function "home"
app.get("/", home)
app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)
app.run()
```

upgrade
```python
from socketify import App, AppOptions, OpCode, CompressOptions

    # is called when websckot client can conected, sending a message 
def ws_open(ws):
    print("A WebSocket got connected!")
    ws.send("Hello World!", OpCode.TEXT)

    # handle with receive message
def ws_message(ws, message, opcode):
    print(message, opcode)
    # Ok is false if backpressure was built up, wait for drain
    ok = ws.send(message, opcode)

    # handles the update process upon reiceiving specific request headers
def ws_upgrade(res, req, socket_context):
    key = req.get_header("sec-websocket-key")
    protocol = req.get_header("sec-websocket-protocol")
    extensions = req.get_header("sec-websocket-extensions")
    res.upgrade(key, protocol, extensions, socket_context)

app = App()
app.ws(
    "/*",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR, # configure compression 
        "max_payload_length": 16 * 1024 * 1024, # give the max size of payload
        "idle_timeout": 12, # give thetime before clossing
        "open": ws_open, # call ws_open when open conecting 
        "message": ws_message, # handle message
        "upgrade": ws_upgrade, # manage the update of websocket
        "drain": lambda ws: print( # here the function show backpressure
            "WebSocket backpressure: %s", ws.get_buffered_amount()
        ),
        "close": lambda ws, code, message: print("WebSocket closed"),
    },
)
    # set standard response for other request
app.any("/", lambda res, req: res.end("Nothing to see here!"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()
```
upgrade_async
```python
from socketify import App, AppOptions, OpCode, CompressOptions
import asyncio

def ws_open(ws):
    print("A WebSocket got connected!")
    ws.send("Hello World!", OpCode.TEXT)

 # function for read the sended message
def ws_message(ws, message, opcode):
    print(message, opcode)
    # Ok is false if backpressure was built up, wait for drain
    ok = ws.send(message, opcode)

 # function to manage websocket protocol update 
async def ws_upgrade(res, req, socket_context):
        # header for websocket conection
    key = req.get_header("sec-websocket-key")
    protocol = req.get_header("sec-websocket-protocol")
    extensions = req.get_header("sec-websocket-extensions")
    await asyncio.sleep(2) # stop for 2 seconds to simulate an async process
    res.upgrade(key, protocol, extensions, socket_context)

app = App()
app.ws(
    "/*",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR, # configure the compression
        "max_payload_length": 16 * 1024 * 1024, # give the max size of payload
        "idle_timeout": 12, # give the max time before closing 
        "open": ws_open, # call ws_open when open conection
        "message": ws_message, # handle message
        "upgrade": ws_upgrade, # manages the update of websocket
        "drain": lambda ws: print( # function to show backpressure
            "WebSocket backpressure: %s", ws.get_buffered_amount()
        ),
        "close": lambda ws, code, message: print("WebSocket closed"),
    },
)
    # set standard response for other requests
app.any("/", lambda res, req: res.end("Nothing to see here!"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()
```
upload_or_post
```python
from socketify import App

# We always recommend check res.aborted in async operations

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
```

websockets
```python
from socketify import App, AppOptions, OpCode, CompressOptions


def ws_open(ws): 
    # function called when a websocket connection is enable
    print("A WebSocket got connected!") # show connection message
    ws.send("Hello World!", OpCode.TEXT) # send initial message


def ws_message(ws, message, opcode): 
    # call when a message is received
    print(message, opcode) # show the received message 
    # Ok is false if backpressure was built up, wait for drain
    ok = ws.send(message, opcode) # attempt to send message back to the client


app = App() # create an intance of the application 


app.ws(
    
    "/*",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR, # enable compression
        "max_payload_length": 16 * 1024 * 1024, # set max size payload
        "idle_timeout": 12, # set max time
        "open": ws_open, # set the function to connected open
        "message": ws_message, # set function to call when received a message
        "drain": lambda ws: print( # set a csllbsck for backpressure
            "WebSocket backpressure: %s", ws.get_buffered_amount() # show the buffered amount of data
        ),
        "close": lambda ws, code, message: print("WebSocket closed"), # function called when the connection closes
    },
)
    # respond a message for request to the root
app.any("/", lambda res, req: res.end("Nothing to see here!'"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)
app.run()
```

ws_close_connection
```python
from socketify import App, AppOptions, OpCode, CompressOptions  # Import necessary classes from the socketify package

def ws_open(ws):
    # Function called when a WebSocket connection is enable
    print("A WebSocket got connected!")  # show connection message 
    ws.send("Hello World!", OpCode.TEXT)  # Send initial message 

def ws_message(ws, message, opcode):
    # call when a message is received
    print(message, opcode)  # show the received message 
    if message == 'close':  # Check if the received message is 'close'
        ws.close()  # Close the WebSocket connection
    else:
        # Attempt to send the message back to the client, checking for backpressure
        ok = ws.send(message, opcode)  # atempt to send message back to the client 

app = App()  # Create an instance of the application

app.ws(
    "/*",  # Route that accepts any endpoint
    {
        "compression": CompressOptions.SHARED_COMPRESSOR,  # Enable compression
        "max_payload_length": 16 * 1024 * 1024,  # Set the max payload size
        "idle_timeout": 12,  # Set the max time
        "open": ws_open,  # set the function to connection opens
        "message": ws_message,  # Function to call when a message is received
        "drain": lambda ws: print(  # set a callback for backpressure
            "WebSocket backpressure: %s", ws.get_buffered_amount()  # Show the buffered amount of data
        ),
        "close": lambda ws, code, message: print("WebSocket closed"),  # Function called when the connection closes
    },
)

# Respond with a message for requests to the root
app.any("/", lambda res, req: res.end("Nothing to see here!"))

app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)),
)

app.run()

```

hello_world
```python
from socketify import App

app = App()
app.get("/", lambda res, req: res.end("Hello World!"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

hello_world_unix_domain
```python
from socketify import App, AppListenOptions

app = App()
app.get("/", lambda res, req: res.end("Hello World!"))
    #Configure server for socket unix   
app.listen(
    AppListenOptions(domain="/tmp/test.sock"),
    lambda config: print("Listening on port %s http://localhost/ now\n" % config.domain),
)
app.run()

# you can test with curl -GET --unix-socket /tmp/test.sock http://localhost/
```

hello_world_cli
```python
from socketify import App

# App will be created by the cli with all things you want configured
def run(app: App): 
    # add your routes here
    app.get("/", lambda res, req: res.end("Hello World!"))
    
# python -m socketify hello_world_cli:run --port 8080 --workers 2
# python3 -m socketify hello_world_cli:run --port 8080 --workers 2
# pypy3 -m socketify hello_world_cli:run --port 8080 --workers 2

# see options in with: python3 -m socketify --help
```

hello_world_cli_ws
```python
from socketify import App, OpCode

def run(app: App): 
    # add your routes here
    app.get("/", lambda res, req: res.end("Hello World!"))
    

# cli will use this configuration for serving in "/*" route, you can still use .ws("/*", config) if you want but --ws* options will not have effect
websocket = {
    "open": lambda ws: ws.send("Hello World!", OpCode.TEXT),
    "message": lambda ws, message, opcode: ws.send(message, opcode),
    "close": lambda ws, code, message: print("WebSocket closed"),
}
# python -m socketify hello_world_cli_ws:run --ws hello_world_cli_ws:websocket --port 8080 --workers 2
# python3 -m socketify hello_world_cli_ws:run --ws hello_world_cli_ws:websocket--port 8080 --workers 2
# pypy3 -m socketify hello_world_cli_ws:run --ws hello_world_cli_ws:websocket--port 8080 --workers 2

# see options in with: python3 -m socketify --help
```

```python
# We have an version of this using aiofile and aiofiles
# This is an sync version without any dependencies is normally much faster in CPython and PyPy3
# In production we highly recommend to use CDN like CloudFlare or/and NGINX or similar for static files (in any language/framework)

# Some performance data from my personal machine (Debian 12/testing, i7-7700HQ, 32GB RAM, Samsung 970 PRO NVME)
# using oha -c 400 -z 5s http://localhost:3000/

# nginx     - try_files                 -  77630.15 req/s
# pypy3     - socketify static          -  16797.30 req/s
# python3   - socketify static          -  10140.19 req/s
# node.js   - @fastify/static           -   5437.16 req/s
# node.js   - express.static            -   4077.49 req/s
# python3   - socketify static_aiofile  -   2390.96 req/s
# python3   - socketify static_aiofiles -   1615.12 req/s
# python3   - scarlette static uvicorn  -   1335.56 req/s
# python3   - fastapi static gunicorn   -   1296.14 req/s
# pypy3     - socketify static_aiofile  -    639.70 req/s
# pypy3     - socketify static_aiofiles -    637.55 req/s
# pypy3     - fastapi static gunicorn   -    253.31 req/s
# pypy3     - scarlette static uvicorn  -    279.45 req/s

# Conclusions:
# With PyPy3 only static is really usable gunicorn/uvicorn, aiofiles and aiofile are really slow on PyPy3 maybe this changes with HPy
# Python3 with any option will be faster than gunicorn/uvicorn but with PyPy3 with static we got 4x (or almost this in case of fastify) performance of node.js
# But even PyPy3 + socketify static is 5x+ slower than NGINX

# Anyway we really recommends using NGINX or similar + CDN for production like everybody else
# Gunicorn production recommendations: https://docs.gunicorn.org/en/latest/deploy.html#deploying-gunicorn
# Express production recommendations: https://expressjs.com/en/advanced/best-practice-performance.html
# Fastify production recommendations: https://www.fastify.io/docs/latest/Guides/Recommendations/

from socketify import App, sendfile


app = App()


# send home page index.html
async def home(res, req):
    # sends the whole file with 304 and bytes range support
    await sendfile(res, req, "./public/index.html")


app.get("/", home)

# serve all files in public folder under /* route (you can use any route like /assets)
app.static("/", "./public")

app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

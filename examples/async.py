from socketify import App, AppOptions, AppListenOptions
import asyncio

app = App()


async def delayed_hello(delay, res):
    await asyncio.sleep(delay)  # do something async
    res.cork_end("Hello with delay!") # Send the responde for the client


def home(res, req):
    # request object only lives during the life time of this call
    # get parameters, query, headers anything you need here
    delay = req.get_query("delay")
    delay = 0 if delay == None else float(delay)
    # tell response to run this in the event loop
    # abort handler is grabbed here, so responses only will be send if res.aborted == False
    res.run_async(delayed_hello(delay, res))
    # Execute "delayed_hello" in async mode

async def json(res, req):
    # request object only lives during the life time of this call
    # get parameters, query, headers anything you need here before first await :)
    user_agent = req.get_header("user-agent")
    # req maybe will not be available in direct attached async functions after await
    await asyncio.sleep(2)  # do something async

    res.cork_end({"message": "I'm delayed!", "user-agent": user_agent})
        # This respond with Json

def not_found(res, req):
    res.write_status(404).end("Not Found")  # Returns error 404 for routes we not found


app.get("/", home)  # route named "/" is called 'home'
app.get("/json", json)  # Route named "/json" is called 'json'
app.any("/*", not_found)    # All routes return 404

    # Configure the server to test
app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)

app.run()

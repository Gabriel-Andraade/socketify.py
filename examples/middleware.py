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

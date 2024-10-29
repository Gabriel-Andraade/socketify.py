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

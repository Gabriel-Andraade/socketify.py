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

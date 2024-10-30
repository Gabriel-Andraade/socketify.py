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

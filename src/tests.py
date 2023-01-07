from socketify import App

app = App()

def extension(request, response, ws):

    @request.method
    async def get_user(self):
        token = self.get_header("token")
        self.token = token
        return { "name": "Test" } if token else { "name", "Anonymous" }

    @request.method
    async def get_cart(self):
        return [{ "quantity": 10, "name": "T-Shirt" }]

    request.property("token", "testing")

# extensions must be registered before routes
app.register(extension)

def auth_middleware(res, req, data):
    token = req.get_query("token")
    print("token?", token)
    req.token = token
    return { "name": "Test" } if token else { "name", "Anonymous" }

router = app.router("")

@router.get("/")
def home(res, req, data=None):
    # print(data)
    # print("token", req.token)
    # cart = await req.get_cart()
    # print("cart", cart)
    # user = await req.get_user()
    # print("user", user)
    # print("token", req.token)
    res.send({"Hello": "World!"}, headers=(("X-Rate-Limit-Remaining", "10"), (b'Another-Headers', b'Value')))


app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()


# uws_websocket_drain_handler
# uws_websocket_subscription_handler
# uws_websocket_open_handler
# uws_websocket_message_handler
# uws_websocket_pong_handler
# uws_websocket_ping_handler
# uws_websocket_close_handler
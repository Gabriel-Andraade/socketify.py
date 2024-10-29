from socketify import App

app = App()
app.get("/", lambda res, req: res.end("Hello World socketify from Python!")) # Define one route for the application
    # Res: show the answer who showed for the client
    # Req: show the request for client
    # Res.end: display the answer
app.listen(
    0, lambda config: print("Listening on port http://localhost:%d now\n" % config.port) 
)
app.run()

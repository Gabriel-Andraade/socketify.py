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

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

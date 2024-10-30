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

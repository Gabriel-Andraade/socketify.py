from socketify import App

# see helper/templates.py for plugin implementation
from helpers.templates import Jinja2Template

 # here give the setting for jinja2
app = App()
app.template(Jinja2Template("./templates", encoding="utf-8", followlinks=False))

 # configure the settings for render the template of jinja2
def home(res, req):
    res.render("jinja2_home.html", title="Hello", message="Hello, World")

 # set one route for "/" to execute function "home"
app.get("/", home)
app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)
app.run()

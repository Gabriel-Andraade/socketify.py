from socketify import App

# Veja helper/templates.py para implementação de plugin
from helpers.templates import Jinja2Template

 # Aqui são a configuração para jinja2
app = App()
app.template(Jinja2Template("./templates", encoding="utf-8", followlinks=False))

 # Aqui é a configuração para renderizar o template de jinja2 
def home(res, req):
    res.render("jinja2_home.html", title="Hello", message="Hello, World")

 # Defina uma rota para "/" para executar a função "home"
app.get("/", home)
app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)
app.run()

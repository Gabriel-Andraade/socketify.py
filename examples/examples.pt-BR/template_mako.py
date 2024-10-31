from socketify import App

# Veja helper/templates.py para implementação de plugin
from helpers.templates import MakoTemplate

 # Aqui são a configuração para mako
app = App()
app.template(
    MakoTemplate(
        directories=["./templates"], output_encoding="utf-8", encoding_errors="replace"
    )
)

 # Aqui é a configuração para renderizar o template de mako
def home(res, req):
    res.render("mako_home.html", message="Hello, World")

 # Defina uma rota para "/" para executar a função "home"
app.get("/", home)
app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)
app.run()

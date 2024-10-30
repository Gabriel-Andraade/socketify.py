# Este exemplo mostra apenas como usar o registro em python para registrar request

from socketify import App
import logging
# Configure o formato de registro tipo esse

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO
)

# Simplesmente função de alta ordem devlog, você também pode criar um middleware para usar o registro, veja middleware_router.py e middleware.py

def devlog(handler):
    def devlog_route(res, req):
        logging.info(f'{req.get_method()} {req.get_full_url()} {req.get_headers()=}')
        handler(res, req)
    return devlog_route

# Agora ée usar a função devlog ou middleware

app = App()

def home(res, req):
    res.end("Hello World!") # Resposta para a rota 

app.get("/", devlog(home)) # Aplicar o registro na rota

app.listen(
    3000,
    lambda config: logging.info("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()



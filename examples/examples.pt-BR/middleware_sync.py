from socketify import App

# Este é apenas um exemplo de implementação que você pode importar usando from socketify import middleware para uma versão mais completa

# Defina uma função de middleware personalizada que aceite várias funções de middleware
def middleware(*functions):
    
    def middleware_route(res, req):
        data = None
        # Ciclo para todos os middlewares
        for function in functions:
            # Chama todos os middlewares
            data = function(res, req, data)
            # Para se retorna False
            if not data:
                break

    return middleware_route

     # Esta função verifica a autorização do usuário  

def get_user(authorization_header):
    if authorization_header:
        return {"greeting": "Hello, World"}
    return None

     # Esta autenticação de middleware verifica se tem um usuário autorizado
def auth(res, req, data=None):
    user = get_user(req.get_header("authorization"))
    if not user:
        res.write_status(403).end("not authorized") # Retorna o erro '403' se não autorizado
        return False

    # Retorna dados extras
    return user

    # Função principal para cumprimentar usu;arios
def home(res, req, user=None):
    res.end(user.get("greeting", None))


app = App()
app.get("/", middleware(auth, home))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

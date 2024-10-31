from socketify import App

# Este é apenas um exemplo de implementação que você pode importar usando from socketify import middleware para uma versão mais completa
# Aqui você vê o que pode fazer para autenticação de usuário ser válido

async def get_user(authorization):
    if authorization: # Verifique se existe autorização 
        # Faça m async aqui
        return {"greeting": "Hello, World"} # Retorne um dict se tiver a autorização 
    return None # Retorna None se não tiver a autorização


def auth(route):
    # na async query string, arguments e headers são válidos apenas até o primeiro await
    async def auth_middleware(res, req):
        
        # get_headers preservará headers (e cookies) dentro de req, após await 
        headers = req.get_headers()
        
        # get_parameters preservará todos os parâmetros dentro de req após await
        params = req.get_parameters()
        
        # get_queries preservará todas as queries dentro de req após await
        queries = req.get_queries()
        # Ou apenas use req.preserve() para preservar tudo

        user = await get_user(headers.get("authorization", None)) # Verificar autorização 
        if user: # Se o usuário estiver autorizado, chame a rota 
            return route(res, req, user)

        return res.write_status(403).cork_end("not authorized") # Retorna 403 'error' se não estiver autorizado

    return auth_middleware # Retorna no modo middleware


def home(res, req, user=None):
    theme = req.get_query("theme_color") # Define a cor do tema da query 
    
    theme = theme if theme else "light" # Define o tipo de tema
    
    greeting = user.get("greeting", None) # Define o tipo de saudação
    
    user_id = req.get_parameter(0) # Obtém o ID do usuário route
    
    res.cork_end(f"{greeting} <br/> theme: {theme} <br/> id: {user_id}") # Enviar a resposta


app = App() # Criar novo aplicativo 
app.get("/user/:id", auth(home)) # Define nota com middleware de autenticação
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()


# curl --location --request GET 'http://localhost:3000/user/10?theme_color=dark' --header 'Authorization: Bearer 23456789'

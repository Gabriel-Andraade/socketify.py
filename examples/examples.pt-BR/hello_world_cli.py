from socketify import App

# O aplicativo será criado pelo cli com todas as coisas que você deseja configurar
def run(app: App): 
    # add your routes here
    app.get("/", lambda res, req: res.end("Hello World!"))
    
# python -m socketify hello_world_cli:run --port 8080 --workers 2
# python3 -m socketify hello_world_cli:run --port 8080 --workers 2
# pypy3 -m socketify hello_world_cli:run --port 8080 --workers 2

# Veja as opções usando no terminal: python3 -m socketify --help
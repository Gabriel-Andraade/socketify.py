## Mecanismo de Template
É muito fácil adicionar suporte a Template, já adicionamos `Mako` e `Jinja2` em /src/examples/helpers/templates.py.

### Implementação de extensão de Template
```python
# Exemplo simples de plugins de modelo mako e jinja2 para socketify.py
from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions


from jinja2 import Environment, FileSystemLoader


class Jinja2Template:
    def __init__(self, searchpath, encoding="utf-8", followlinks=False):
        self.env = Environment(
            loader=FileSystemLoader(searchpath, encoding, followlinks)
        )

    # Você também pode adicionar estratégia de cache e registro aqui se quiser :]
    def render(self, templatename, **kwargs):
        try:
            template = self.env.get_template(templatename)
            return template.render(**kwargs)
        except Exception as err:
            return str(err)


class MakoTemplate:
    def __init__(self, **options):
        self.lookup = TemplateLookup(**options)

    # Você também pode adicionar estratégia de cache e registro aqui se quiser ;]
    def render(self, templatename, **kwargs):
        try:
            template = self.lookup.get_template(templatename)
            return template.render(**kwargs)
        except Exception as err:
            return exceptions.html_error_template().render()
```

### Usando templates
`app.template(instance)` registrará a extensão Template e a chamará qunado você usar `res.render(...)`

```python
from socketify import App
# Veja helper/templates.py para a implementação de plugin
from helpers.templates import MakoTemplate


app = App()
# Registrar templates
app.template(
    MakoTemplate(
        directories=["./templates"], output_encoding="utf-8", encoding_errors="replace"
    )
)


def home(res, req):
    res.render("mako_home.html", message="Hello, World")


app.get("/", home)
app.listen(
    3000,
    lambda config: print(
        "Listening on port http://localhost:%s now\n" % str(config.port)
    ),
)
app.run()

```

### Próximos [GraphiQL](graphiql.md)
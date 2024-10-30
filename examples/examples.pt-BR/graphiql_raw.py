import dataclasses
import strawberry  # Usado para definir esquema do GraphQL e criar dicas
import strawberry.utils.graphiql # Ferramenta para interface Web

from socketify import App
from typing import List, Optional


    # Definir o tipo de classe chamada
@strawberry.type
class User:
    name: str


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> Optional[User]:
        return User(name="Hello")

    # Cria esquema GraphQL a partir da classe de query =
schema = strawberry.Schema(Query)

    # Definir função async para manipular solicitações POST no GraphiQL
async def graphiql_post(res, req):
    # Podemos passar o que quisermos para context, query, headers ou params, cookies e etc
    context_value = req.preserve()

    # Obter todos os dados de entrada e analisar como json
    body = await res.get_json()
    # Extrair a query e possíveis variáveis de entrada
    query = body["query"]
    variables = body.get("variables", None)
    root_value = body.get("root_value", None)
    operation_name = body.get("operation_name", None)
    # Execute a query GraphQL usando o esquema 
    data = await schema.execute(
        query,
        variables,
        context_value,
        root_value,
        operation_name,
    )
    # Envie uma resposta json para cliente com dados, erros e extensões 
    res.cork_end(
        {
            "data": (data.data),
            **({"errors": data.errors} if data.errors else {}),
            **({"extensions": data.extensions} if data.extensions else {}),
        }
    )

    # Configure o servidor usando a biblioteca de app
app = App()
    # Roteie GET retornamos a interface GraphiQL HTML para um teste de facilidade 
app.get("/", lambda res, req: res.end(strawberry.utils.graphiql.get_graphiql_html()))
    # Postar rota para processar consultas GraphQL
app.post("/", graphiql_post)
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

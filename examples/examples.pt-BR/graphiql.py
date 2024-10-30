import dataclasses
import strawberry
import strawberry.utils.graphiql

from socketify import App
from typing import List, Optional
from helpers.graphiql import graphiql_from

    # Definir tipo de usuário para GraphQL
@strawberry.type
class User:
    name: str

    # Self.Context é o AppRequest, tem dados de request
@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> Optional[User]:
        # Self.Context é o AppRequest, tem dados de request
        return User(name="Hello")


app = App()
    # Definir rota GET para consultas GraphiQL, retornando ao HTML para o navegador
app.get("/", lambda res, req: res.end(strawberry.utils.graphiql.get_graphiql_html()))
    # Aqui define a rota POST para consultas GraphQL de processo, usando função graphiql_from
app.post("/", graphiql_from(Query))
# Você também pode passar uma Mutação como segundo parâmetro
# app.post("/", graphiql_from(Query, Mutation))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

## Suporte GraphiQL
Em [`/src/examples/helper/graphiql.py`](https://github.com/cirospaciari/socketify.py/blob/main/examples/graphiql.py) implementamos um auxiliar para usar graphiQL com strawberry

### Uso
```python
import dataclasses
import strawberry
import strawberry.utils.graphiql

from socketify import App
from typing import List, Optional
from helpers.graphiql import graphiql_from


@strawberry.type
class User:
    name: str


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> Optional[User]:
        # self.context é o AppRequest
        return User(name="Hello")


app = App()
app.get("/", lambda res, req: res.end(strawberry.utils.graphiql.get_graphiql_html()))
app.post("/", graphiql_from(Query))
# Você também pode passar uma Mutation como segundo parâmetro
# app.post("/", graphiql_from(Query, Mutation))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
```

### Implementação de Helper

```python
import strawberry
import strawberry.utils.graphiql


def graphiql_from(Query, Mutation=None):
    if Mutation:
        schema = strawberry.Schema(query=Query, mutation=Mutation)
    else:
        schema = strawberry.Schema(Query)

    async def post(res, req):
        # Podemos passar o que quisermos para context, query, headers ou params, cookies etc 
        context_value = req.preserve()

        # Obtém todos os dados de entrada e analisa como json
        body = await res.get_json()

        query = body["query"]
        variables = body.get("variables", None)
        root_value = body.get("root_value", None)
        operation_name = body.get("operation_name", None)

        data = await schema.execute(
            query,
            variables,
            context_value,
            root_value,
            operation_name,
        )

        res.cork_end(
            {
                "data": (data.data),
                **({"errors": data.errors} if data.errors else {}),
                **({"extensions": data.extensions} if data.extensions else {}),
            }
        )

    return post

```

### Próximos [WebSockets and Backpressure](websockets-backpressure.md)
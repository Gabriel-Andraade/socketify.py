import dataclasses
import strawberry  # Used for to Set schema from GraphQL and create tips
import strawberry.utils.graphiql # Tool for web interface 

from socketify import App
from typing import List, Optional


    # Set type of class called 
@strawberry.type
class User:
    name: str


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> Optional[User]:
        return User(name="Hello")

    # Creates schema GraphQL from the query class
schema = strawberry.Schema(Query)

    # Set async function to handle requests POST in GraphiQL
async def graphiql_post(res, req):
    # we can pass whatever we want to context, query, headers or params, cookies etc
    context_value = req.preserve()

    # get all incoming data and parses as json
    body = await res.get_json()
    # extracts the query and possible input variables
    query = body["query"]
    variables = body.get("variables", None)
    root_value = body.get("root_value", None)
    operation_name = body.get("operation_name", None)
    # execute the query GraphQL using schema
    data = await schema.execute(
        query,
        variables,
        context_value,
        root_value,
        operation_name,
    )
    # send a response JSON for the client with datas, errors and extensios
    res.cork_end(
        {
            "data": (data.data),
            **({"errors": data.errors} if data.errors else {}),
            **({"extensions": data.extensions} if data.extensions else {}),
        }
    )

    # Configure the server using the app library
app = App()
    # Route GET we return GraphiQL interface HTML for a facility test
app.get("/", lambda res, req: res.end(strawberry.utils.graphiql.get_graphiql_html()))
    # Post route to process GraphQL querys using graphiql_post function
app.post("/", graphiql_post)
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

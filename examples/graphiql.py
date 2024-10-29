import dataclasses
import strawberry
import strawberry.utils.graphiql

from socketify import App
from typing import List, Optional
from helpers.graphiql import graphiql_from

    # Define User type for GraphQL, with camp "name"
@strawberry.type
class User:
    name: str

    # Set the query clas as entry point for GraphQL 
@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> Optional[User]:
        # self.context is the AppRequest, have datas of request
        return User(name="Hello")


app = App()
    # Set route GET for GraphiQL queries, returning HTML for the browser
app.get("/", lambda res, req: res.end(strawberry.utils.graphiql.get_graphiql_html()))
    # set route POST for proccess GraphQL queries, using function graphiql_from 
app.post("/", graphiql_from(Query))
# you can also pass an Mutation as second parameter
# app.post("/", graphiql_from(Query, Mutation))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

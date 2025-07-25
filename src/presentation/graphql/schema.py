import strawberry

from .resolvers.auth_resolvers import AuthMutation, AuthQuery
from .resolvers.task_list_resolvers import TaskListMutation, TaskListQuery
from .resolvers.task_resolvers import TaskMutation, TaskQuery


@strawberry.type
class Query(AuthQuery, TaskQuery, TaskListQuery):
    """
    GraphQL Query root.
    Follows best practices by combining multiple query classes.
    """


@strawberry.type
class Mutation(AuthMutation, TaskMutation, TaskListMutation):
    """
    GraphQL Mutation root.
    Follows best practices by combining multiple mutation classes.
    """


# Main GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    # Enable GraphQL introspection for development
    extensions=[],
)

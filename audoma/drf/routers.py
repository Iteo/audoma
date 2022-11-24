from rest_framework import routers
from rest_framework.routers import *  # noqa: F403, F401


class SimpleRouter(routers.SimpleRouter):
    routes = [
        # List route.
        routers.Route(
            url=r"^{prefix}{trailing_slash}$",
            mapping={
                "get": "list",
                "post": "create",
                "put": "bulk_update",
                "patch": "partial_bulk_update",
                "delete": "bulk_destroy",
            },
            name="{basename}-list",
            detail=False,
            initkwargs={"suffix": "List"},
        ),
        # Dynamically generated list routes. Generated using
        # @action(detail=False) decorator on methods of the viewset.
        routers.DynamicRoute(
            url=r"^{prefix}/{url_path}{trailing_slash}$",
            name="{basename}-{url_name}",
            detail=False,
            initkwargs={},
        ),
        # Detail route.
        routers.Route(
            url=r"^{prefix}/{lookup}{trailing_slash}$",
            mapping={
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            },
            name="{basename}-detail",
            detail=True,
            initkwargs={"suffix": "Instance"},
        ),
        # Dynamically generated detail routes. Generated using
        # @action(detail=True) decorator on methods of the viewset.
        routers.DynamicRoute(
            url=r"^{prefix}/{lookup}/{url_path}{trailing_slash}$",
            name="{basename}-{url_name}",
            detail=True,
            initkwargs={},
        ),
    ]


class DefaultRouter(SimpleRouter, routers.DefaultRouter):
    ...


# DEPRECATED - to be deleted
class BulkRouter(DefaultRouter):
    """
    Map http methods to actions defined on the bulk mixins.
    """

    # routes = copy.deepcopy(SimpleRouter.routes)
    # routes[0].mapping.update(
    #     {
    #         "put": "bulk_update",
    #         "patch": "partial_bulk_update",
    #         "delete": "bulk_destroy",
    #     }
    # )

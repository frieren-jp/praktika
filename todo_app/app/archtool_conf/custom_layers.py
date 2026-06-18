from archtool.global_types import AppModule
from archtool.layers.default_layers import (
    ApplicationLayer,
    DomainLayer,
    InfrastructureLayer,
    PresentationLayer,
)

app_layers = [
    PresentationLayer,
    ApplicationLayer,
    DomainLayer,
    InfrastructureLayer,
]

APPS = [
    AppModule("app.users"),
    AppModule("app.todos"),
]

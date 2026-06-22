# ПОДСКАЗКА: этот файл описывает архитектурную карту проекта для archtool.
# Здесь мы говорим, какие bounded context существуют и какие слои использовать.

# AppModule - описание одного модуля, который archtool должен просканировать.
from archtool.global_types import AppModule

# Встроенные слои archtool.
# Они соответствуют Clean Architecture: от внешнего слоя к внутреннему.
from archtool.layers.default_layers import (
    ApplicationLayer,
    DomainLayer,
    InfrastructureLayer,
    PresentationLayer,
)

# ПОДСКАЗКА: app_layers - явный список слоев для DependencyInjector.
# PresentationLayer ищет views.py, ApplicationLayer ищет controllers.py,
# DomainLayer ищет services.py, InfrastructureLayer ищет repos.py.
app_layers = [
    # Внешний слой отображения. В нашем проекте views.py нет, но слой передан как часть задания.
    PresentationLayer,
    # Слой контроллеров: app/users/controllers.py и app/todos/controllers.py.
    ApplicationLayer,
    # Слой бизнес-логики: services.py.
    DomainLayer,
    # Слой доступа к данным: repos.py.
    InfrastructureLayer,
]

# ПОДСКАЗКА: APPS - список bounded context.
# Чтобы добавить третий модуль, например notifications, нужно создать папку
# app/notifications и добавить сюда AppModule("app.notifications").
APPS = [
    # Модуль пользователей.
    AppModule("app.users"),
    # Модуль задач.
    AppModule("app.todos"),
]

# Конспект: ООП и SOLID в Python

## ООП в Python

### Класс и объект

Класс - это шаблон, по которому создаются объекты. Объект - конкретный экземпляр класса.

```python
class User:
    role = "user"  # атрибут класса

    def __init__(self, name: str) -> None:
        self.name = name  # атрибут объекта


user = User("Alice")
print(user.name)
```

`self` - это ссылка на текущий объект. Через `self` метод получает доступ к данным конкретного экземпляра.

Атрибут класса общий для всех объектов, а атрибут экземпляра принадлежит конкретному объекту.

### Наследование

Наследование используют, когда один класс действительно является разновидностью другого. Это отношение `is-a`: собака является животным.

```python
class Animal:
    def speak(self) -> str:
        return "..."


class Dog(Animal):
    def speak(self) -> str:
        return "woof"
```

В Python есть множественное наследование. Порядок поиска методов определяется MRO - Method Resolution Order.

```python
class A:
    def run(self):
        return "A"


class B(A):
    def run(self):
        return "B"


class C(A):
    def run(self):
        return "C"


class D(B, C):
    pass


print(D.mro())  # D -> B -> C -> A -> object
```

`super()` вызывает следующую реализацию метода по MRO.

### Абстрактные классы

Абстрактный класс описывает общий контракт: какие методы должны быть у наследников.

```python
from abc import ABC, abstractmethod


class UserRepoABC(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> str:
        pass


class MemoryUserRepo(UserRepoABC):
    def get_by_id(self, user_id: int) -> str:
        return "Alice"
```

Если класс не реализовал все абстрактные методы, создать его экземпляр нельзя. Python выбросит `TypeError`.

Абстрактные классы нужны, чтобы явно отделять интерфейс от реализации. Например, сервису не важно, откуда берется пользователь: из PostgreSQL, памяти или мок-репозитория. Ему важно, чтобы у зависимости был метод `get_by_id`.

### Инкапсуляция

Инкапсуляция - это идея скрывать внутренние детали и давать наружу понятный интерфейс.

```python
class Account:
    def __init__(self, balance: int) -> None:
        self._balance = balance

    @property
    def balance(self) -> int:
        return self._balance

    def deposit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self._balance += amount
```

В Python это в основном соглашение:

- `name` - публичный атрибут;
- `_name` - защищенный по соглашению, его не стоит трогать снаружи;
- `__name` - приватный через name mangling, сложнее случайно переопределить или использовать напрямую.

`@property` позволяет дать доступ как к атрибуту, но внутри оставить метод и проверку.

### Полиморфизм

Полиморфизм - это возможность работать с разными объектами через одинаковое поведение.

В Python часто используется duck typing: если объект умеет делать нужное действие, его можно использовать.

```python
class EmailSender:
    def send(self, text: str) -> None:
        print(f"email: {text}")


class SmsSender:
    def send(self, text: str) -> None:
        print(f"sms: {text}")


def notify(sender, text: str) -> None:
    sender.send(text)
```

Функции `notify` не важно, какой именно класс передали. Важно, что у объекта есть метод `send`.

### Протоколы

Протоколы описывают поведение структурно. Класс не обязан наследоваться от протокола, ему достаточно иметь подходящие методы.

```python
from typing import Protocol


class Sender(Protocol):
    def send(self, text: str) -> None:
        ...


def notify(sender: Sender, text: str) -> None:
    sender.send(text)
```

Это удобно, когда хочется типизировать duck typing.

### Композиция и наследование

Наследование - это отношение `is-a`: объект является разновидностью другого объекта.

Композиция - это отношение `has-a`: объект содержит и использует другой объект.

```python
class UserService:
    def __init__(self, repo: UserRepoABC) -> None:
        self.repo = repo

    def get_user_name(self, user_id: int) -> str:
        return self.repo.get_by_id(user_id)
```

`UserService` не является репозиторием. Он имеет репозиторий и использует его.

Композицию часто предпочитают наследованию, потому что она слабее связывает классы и позволяет проще менять части системы.

### Аннотации типов и DI

Аннотации типов показывают, какую зависимость ожидает класс или функция.

```python
class UserService:
    def __init__(self, repo: UserRepoABC) -> None:
        self.repo = repo
```

`repo: UserRepoABC` означает: сервису нужна любая реализация этого интерфейса.

DI-контейнер может посмотреть на аннотацию, найти зарегистрированную реализацию `UserRepoABC` и автоматически передать ее в конструктор. Поэтому аннотации важны для понимания архитектурных инструментов.

## SOLID

### S - Single Responsibility Principle

Принцип единственной ответственности: у класса должна быть одна причина для изменения.

Плохо:

```python
class UserManager:
    def save_user(self): ...
    def send_welcome_email(self): ...
    def validate_password(self): ...
```

Этот класс меняется по разным причинам: изменилась база, изменилась отправка писем, изменились правила пароля.

Лучше:

```python
class UserRepo:
    def save(self, user): ...


class EmailService:
    def send_welcome(self, user): ...


class PasswordValidator:
    def validate(self, password: str): ...
```

Каждый класс отвечает за свою часть.

### O - Open/Closed Principle

Код должен быть открыт для расширения, но закрыт для изменения.

Идея: чтобы добавить новое поведение, лучше добавить новый класс, а не переписывать старый код.

```python
from typing import Protocol


class PaymentProcessor(Protocol):
    def pay(self, amount: int) -> None:
        ...


class CardPayment:
    def pay(self, amount: int) -> None:
        print("payment by card")


class CryptoPayment:
    def pay(self, amount: int) -> None:
        print("payment by crypto")
```

Если появляется новый способ оплаты, добавляем новый класс, а не ломаем существующие.

### L - Liskov Substitution Principle

Принцип подстановки Лисков: наследник должен заменять родителя без поломки поведения.

Если код ожидает `UserRepoABC`, туда можно передать `PostgresUserRepo` или `MockUserRepo`, и сервис должен продолжить работать.

```python
class MockUserRepo(UserRepoABC):
    def get_by_id(self, user_id: int) -> str:
        return "Test User"
```

Нарушение будет, если наследник вроде бы реализует интерфейс, но неожиданно меняет смысл метода, возвращает несовместимый тип или выбрасывает исключения там, где родитель этого не предполагал.

### I - Interface Segregation Principle

Принцип разделения интерфейсов: лучше несколько маленьких интерфейсов, чем один огромный.

Плохо:

```python
class UserEverythingABC(ABC):
    def get_user(self): ...
    def save_user(self): ...
    def send_email(self): ...
    def render_page(self): ...
```

Такой интерфейс заставляет классы реализовывать методы, которые им не нужны.

Лучше разделить:

- `UserRepoABC` - работа с хранением пользователей;
- `UserServiceABC` - бизнес-логика пользователей;
- `EmailSenderABC` - отправка писем;
- `PageRendererABC` - отображение страниц.

### D - Dependency Inversion Principle

Принцип инверсии зависимостей: высокоуровневый код должен зависеть от абстракций, а не от конкретных классов.

Плохо:

```python
class UserService:
    def __init__(self) -> None:
        self.repo = PostgresUserRepo()
```

`UserService` жестко связан с PostgreSQL. Его сложнее тестировать и менять.

Лучше:

```python
class UserService:
    def __init__(self, repo: UserRepoABC) -> None:
        self.repo = repo
```

Теперь сервис зависит от абстракции. В продакшене можно передать `PostgresUserRepo`, а в тестах - `MockUserRepo`.

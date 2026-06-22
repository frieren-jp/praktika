# ПОДСКАЗКА: controllers.py - ApplicationLayer.
# Контроллер знает про FastAPI, но бизнес-логику делегирует сервису.

# APIRouter группирует маршруты /users.
# HTTPException превращает ошибку сервиса в HTTP-ответ.
from fastapi import APIRouter, HTTPException

# BaseModel и EmailStr описывают тело POST-запроса.
from pydantic import BaseModel, EmailStr

# UserControllerABC - интерфейс контроллера.
# UserServiceABC - зависимость контроллера от сервиса.
from app.users.interfaces import UserControllerABC, UserServiceABC


# ПОДСКАЗКА: DTO входящего запроса POST /users/.
class UserCreate(BaseModel):
    # email валидируется как настоящий email.
    email: EmailStr
    # name - обычная строка.
    name: str


# ПОДСКАЗКА: UserController реализует UserControllerABC.
# archtool найдет его в controllers.py.
class UserController(UserControllerABC):
    # router хранит все маршруты этого контроллера.
    router = APIRouter(prefix="/users", tags=["users"])

    # user_service внедряется archtool: UserServiceABC -> UserService.
    user_service: UserServiceABC

    # init_http_routes вызывается web_fractal при подключении контроллеров.
    def init_http_routes(self) -> None:
        # POST /users/ вызывает метод create_user.
        self.router.add_api_route("/", self.create_user, methods=["POST"])
        # GET /users/{user_id} вызывает метод get_user.
        self.router.add_api_route("/{user_id}", self.get_user, methods=["GET"])

    # Обработчик POST /users/.
    async def create_user(self, payload: UserCreate) -> dict:
        try:
            # Передаем данные из DTO в сервис.
            return await self.user_service.register(email=payload.email, name=payload.name)
        except ValueError as exc:
            # Ошибку бизнес-логики превращаем в HTTP 400.
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Обработчик GET /users/{user_id}.
    async def get_user(self, user_id: int) -> dict:
        try:
            # Просим сервис найти пользователя.
            return await self.user_service.get_user(user_id)
        except ValueError as exc:
            # Если пользователь не найден, возвращаем HTTP 404.
            raise HTTPException(status_code=404, detail=str(exc)) from exc

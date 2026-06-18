from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.users.interfaces import UserControllerABC, UserServiceABC


class UserCreate(BaseModel):
    email: EmailStr
    name: str


class UserController(UserControllerABC):
    router = APIRouter(prefix="/users", tags=["users"])
    user_service: UserServiceABC

    def init_http_routes(self) -> None:
        self.router.add_api_route("/", self.create_user, methods=["POST"])
        self.router.add_api_route("/{user_id}", self.get_user, methods=["GET"])

    async def create_user(self, payload: UserCreate) -> dict:
        try:
            return await self.user_service.register(email=payload.email, name=payload.name)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    async def get_user(self, user_id: int) -> dict:
        try:
            return await self.user_service.get_user(user_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

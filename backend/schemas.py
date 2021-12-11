from pydantic import BaseModel


class CreateUser(BaseModel):
    username: str


class Authorize(BaseModel):
    id: int
    password: str


class CreateGame(BaseModel):
    creator_id: int
    enemy_id: int


class MakeMove(BaseModel):
    chess_yx: str
    move_yx: str
    t: float


class GetGame(BaseModel):
    user_id: int

from pydantic import BaseModel, EmailStr


class PostUserSchema(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserSchema(BaseModel):
    id: int | None
    username: str
    email: EmailStr
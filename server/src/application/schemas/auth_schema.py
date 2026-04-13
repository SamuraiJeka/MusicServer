from pydantic import BaseModel, EmailStr


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class TokenSchema(RefreshTokenSchema):
    access_token: str
    token_type: str

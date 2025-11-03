from pydantic import BaseModel, EmailStr, Field, ValidationInfo, model_validator
from typing import Optional


class NewComment(BaseModel):
    restaurant_id: int
    text: str


class BaseFields(BaseModel):
    email: EmailStr = Field(description="User email", examples=["artem.chebanyuk@gmail.com"])
    name: str = Field(description="User nickname", examples=["Casper"])


class PasswordField(BaseModel):
    password: str = Field(min_lenght=8)

    @model_validator(mode="before")
    def validate_password(cls, values: dict, info: ValidationInfo) -> dict:
        password = (values.get("password") or "").strip()
        if not password:
            raise ValueError("Password required")
        if len(password) < 8:
            raise ValueError("Password is too short")
        if " " in password:
            raise ValueError("Space in password")
        return values


class RegisterUserFields(BaseFields, PasswordField):
    pass


class BaseUserInfo(BaseFields):
    id: int

class UserSchema(BaseModel):
    id: int
    name: str
    email: str
    followers: int
    profile_description: Optional[str] = None
    subscriptions: int

class UserUpdateProfile(BaseModel):
    name: Optional[str] = None
    profile_description: Optional[str] = None
    email: Optional[str] = None
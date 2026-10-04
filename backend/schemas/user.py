from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    phone: str | None = None
    address: str | None = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    phone: str | None = None
    address: str | None = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str
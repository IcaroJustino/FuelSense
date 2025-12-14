from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    id: int
    nome: str
    email: EmailStr
    cpf: str
    coreid: str

    class Config:
        from_attributes = True

# Schema para o Login
class UserLogin(BaseModel):
    email: EmailStr
    senha: str

# Schema para o Token 
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# payload interno do JWT
class TokenData(BaseModel):
    id: Optional[int] = None
from fastapi import Depends, HTTPException, status
from starlette.requests import Request 
from sqlalchemy.orm import Session
from typing import Annotated
from core.database import get_db, UserModel 
from core.security import decode_token 
from models.user import TokenData

def get_current_user(
    request: Request, 
    db: Session = Depends(get_db) 
) -> UserModel:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas. Faça login novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise credentials_exception

    if auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = auth_header 
    
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
        
    user_id: str = payload.get("user_id") 
    
    if user_id is None:
        raise credentials_exception
    
    token_data = TokenData(id=user_id) 

    user = db.query(UserModel).filter(UserModel.id == token_data.id).first()
    
    if user is None:
        raise credentials_exception
        
    return user

CurrentUser = Annotated[UserModel, Depends(get_current_user)]
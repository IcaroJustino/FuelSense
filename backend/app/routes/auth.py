from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm 
from sqlalchemy.orm import Session
from core.database import get_db, UserModel
from core.security import verify_password, create_access_token
from core.config import settings
from models.user import Token
from datetime import timedelta

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)

@router.post(
    "/token", 
    response_model=Token, 
    summary="Login do Usuário e Geração de Token de Acesso (Bearer Token)"
)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas. Verifique o email ou senha.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Geração do Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={
            "sub": user.email, 
            "user_id": str(user.id), 
            "coreid": user.coreid
        },
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
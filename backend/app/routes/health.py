# backend/app/routes/health.py
from fastapi import APIRouter
from typing import Dict
from core.database import engine 

router = APIRouter()

#HealthCheck da Saude da API e do Banco de Dados
@router.get("/health", response_model=Dict[str, str], tags=["Health Check"])
def health_check():
    db_status = "error"
    try:
        
        with engine.connect():
            
            db_status = "ok"
    except Exception as e:
        
        print(f"Erro na conexão com o DB: {e}") 
        db_status = "error"

    return {
        "api_status": "ok",
        "database_status": db_status
    }
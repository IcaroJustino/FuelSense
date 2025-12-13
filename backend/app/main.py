from fastapi import FastAPI
from core.config import settings
from core.database import init_db
from routes import coletas,health,motoristas

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="API para Coleta e Gestão de Dados de Vendas de Combustível.",
    on_startup=[init_db] 
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(coletas.router, prefix="/api/v1/coletas")
app.include_router(motoristas.router, prefix="/api/v1/motoristas")

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Coleta de Combustível. Veja /docs para documentação."}
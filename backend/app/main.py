from fastapi import FastAPI
from core.config import settings
from core.database import init_db
from routes import coletas,health,motoristas,dashboard,auth

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="API para Coleta e Gestão de Dados de Vendas de Combustível.",
    on_startup=[init_db],
     
    #Configuração do swagger e security
    openapi_extra={
        "security": [
            {
                "BearerAuth": [], 
            }
        ],
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "Insira o JWT Token obtido no /api/v1/auth/token."
                }
            }
        }
    }
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(coletas.router, prefix="/api/v1/coletas")
app.include_router(motoristas.router, prefix="/api/v1/motoristas")
app.include_router(dashboard.router, prefix="/api/v1/dashboard")
app.include_router(auth.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Coleta de Combustível. Veja /docs para documentação."}
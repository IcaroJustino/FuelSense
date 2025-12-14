from fastapi import FastAPI, Security
from fastapi.security import HTTPBearer
from core.config import settings
from core.database import init_db
from routes import coletas, health, motoristas, dashboard, auth
import time
from datetime import datetime
from core.cache_utils import get_last_update_timestamp
from core.authguard import CurrentUser
from models.kpis import DashboardStatus 

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="API para Coleta e Gestão de Dados de Vendas de Combustível.",
    on_startup=[init_db],
     
    # Configuração do swagger e security
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

def format_timedelta_to_friendly_string(seconds: int) -> str:
    if seconds is None or seconds < 0:
        return "Status de atualização indisponível."
    if seconds < 60:
        return f"Atualizado há {seconds} segundo{'s' if seconds != 1 else ''}."
    minutes = seconds // 60
    if minutes < 60:
        return f"Atualizado há {minutes} minuto{'s' if minutes != 1 else ''}."
    hours = minutes // 60
    if hours < 24:
        return f"Atualizado há {hours} hora{'s' if hours != 1 else ''}."
    days = hours // 24
    return f"Atualizado há {days} dia{'s' if days != 1 else ''}."


@app.get(
    "/api/v1/status-dados", 
    response_model=DashboardStatus, 
    summary="Retorna o momento da última ingestão de dados, indicando o freshness do cache do Dashboard.",
    tags =["Raiz"],
    dependencies=[Security(HTTPBearer())]
)
def get_data_freshness_status(
    current_user: CurrentUser
):
    last_ts = get_last_update_timestamp()
    current_ts = int(time.time())
    seconds_ago = None
    last_dt = None

    if last_ts is not None:
        seconds_ago = current_ts - last_ts
        last_dt = datetime.fromtimestamp(last_ts)
        friendly_msg = format_timedelta_to_friendly_string(seconds_ago)
    else:
        friendly_msg = "Nenhuma atualização de dados registrada recentemente (chave Redis vazia)."

    return DashboardStatus(
        last_update_timestamp=last_ts,
        last_update_datetime=last_dt,
        time_since_last_update_seconds=seconds_ago,
        friendly_status=friendly_msg
    )

app.include_router(health.router, prefix="/api/v1")
app.include_router(coletas.router, prefix="/api/v1/coletas")
app.include_router(motoristas.router, prefix="/api/v1/motoristas")
app.include_router(dashboard.router, prefix="/api/v1/dashboard")
app.include_router(auth.router, prefix="/api/v1")


@app.get("/", tags =["Raiz"])
def read_root():
    return {"message": "Bem-vindo à API de Coleta de Combustível. Veja /docs para documentação."}
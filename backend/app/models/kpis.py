from pydantic import BaseModel,Field,condecimal
from typing import Optional, List, Union
from datetime import datetime,date
from typing import List
from models.coleta import FuelType, VehicleType

class MediaPrecoCombustivel(BaseModel):
    tipo_combustivel: FuelType 
    media_preco: float 

class VolumeConsumidoVeiculo(BaseModel):
    tipo_veiculo: VehicleType
    volume_total: float


class PrecoHistoricoResponse(BaseModel):

    data_coleta: date 
    tipo_combustivel: FuelType
    preco_medio_arredondado: float

class PostoRankingEstado(BaseModel):
    estado: str = Field(..., description="Estado da federação.")
    posto_nome: str = Field(..., description="Nome do Posto.")
    total_coletas: int = Field(..., description="Número total de coletas realizadas no posto naquele estado.")
    
    class Config:
        from_attributes = True


class DashboardStatus(BaseModel):
    last_update_timestamp: Optional[int] = Field(None, description="Timestamp Unix da última ingestão de dados (UTC).")
    last_update_datetime: Optional[datetime] = Field(None, description="Datetime formatado da última ingestão de dados.")
    time_since_last_update_seconds: Optional[int] = Field(None, description="Tempo decorrido (em segundos) desde a última atualização.")
    friendly_status: str = Field(..., description="Mensagem amigável de status (ex: 'Atualizado há 5 minutos').")
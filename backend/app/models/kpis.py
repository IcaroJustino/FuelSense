from pydantic import BaseModel,Field,condecimal
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
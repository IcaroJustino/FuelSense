from pydantic import BaseModel
from datetime import datetime,date
from typing import List
# from decimal import Decimal # Não é mais necessário se usarmos float
from models.coleta import FuelType, VehicleType

# 1. Schema para Média de Preço por Combustível
class MediaPrecoCombustivel(BaseModel):
    
    tipo_combustivel: FuelType 
    # 🚨 AJUSTE: Mudar para float para evitar erros de conversão do driver SQL
    media_preco: float 

# 2. Schema para Volume Consumido por Tipo de Veículo
class VolumeConsumidoVeiculo(BaseModel):
    
    tipo_veiculo: VehicleType
    # 🚨 AJUSTE: Mudar para float para evitar erros de conversão do driver SQL
    volume_total: float


class PrecoHistoricoResponse(BaseModel):
    """Representa um ponto de dado do preço médio de um combustível no tempo."""
    
    data_coleta: date # Data da coleta original (ou agrupamento por dia)
    tipo_combustivel: FuelType
    # Usamos float, mas o valor será arredondado no SQL
    preco_medio_arredondado: float


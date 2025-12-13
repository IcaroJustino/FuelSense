from pydantic import BaseModel
from typing import List
from decimal import Decimal
from models.coleta import FuelType, VehicleType

class MediaPrecoCombustivel(BaseModel):
    
    tipo_combustivel: FuelType 
    media_preco: Decimal 

class VolumeConsumidoVeiculo(BaseModel):
    
    tipo_veiculo: VehicleType
    volume_total: Decimal

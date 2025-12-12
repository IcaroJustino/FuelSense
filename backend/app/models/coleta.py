from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, condecimal

FuelType = Literal["Gasolina", "Etanol", "Diesel S10"]
VehicleType = Literal["Carro", "Moto", "Caminhão Leve", "Carreta", "Ônibus"]


# Base Model de Coleta dos dados do IOT
class ColetaBase(BaseModel):
    posto_identificador: str = Field(..., description="CNPJ ou ID do Posto (Identificador único).")
    posto_nome: str
    cidade: str
    estado: str
    data_coleta: datetime = Field(..., description="Data e hora da coleta.")
    tipo_combustivel: FuelType
    preco_venda: condecimal(max_digits=10, decimal_places=2) = Field(..., gt=0, description="Preço por litro em Reais.")
    volume_vendido: condecimal(max_digits=10, decimal_places=2) = Field(..., gt=0, description="Volume vendido em litros.")
    motorista_nome: str
    motorista_cpf: str = Field(..., min_length=11, description="CPF do motorista (apenas números ou formatado).")
    veiculo_placa: str
    tipo_veiculo: VehicleType


#DTO de CREATE
class ColetaCreate(ColetaBase):
    pass


#DTO de COOLETA
class Coleta(ColetaBase):
    id: int 
    
    class Config:
        from_attributes = True 

        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

#DTO de PUT/PATCH
class ColetaUpdate(BaseModel):
    posto_nome: Optional[str] = None
    preco_venda: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    volume_vendido: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    motorista_nome: Optional[str] = None
    motorista_cpf: Optional[str] = None
    veiculo_placa: Optional[str] = None
    tipo_veiculo: Optional[VehicleType] = None
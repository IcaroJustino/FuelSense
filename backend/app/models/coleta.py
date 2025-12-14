from datetime import datetime
from typing import Literal, Optional, List
from pydantic import BaseModel, Field, condecimal


# Define os valores permitidos para validação
FuelType = Literal["Gasolina", "Etanol", "Diesel S10"]
VehicleType = Literal["Carro", "Moto", "Caminhão Leve", "Carreta", "Ônibus"]


# Base Model de Coleta dos dados do IOT
class ColetaBase(BaseModel):
    posto_identificador: str = Field(..., description="CNPJ ou ID do Posto (Identificador único).")
    posto_nome: str
    cidade: str
    estado: str
    # 🚨 CAMPO MANTIDO COMO DATETIME NA BASE PARA O DTO DE ENTRADA (POST)
    data_coleta: datetime = Field(..., description="Data e hora da coleta.")
    tipo_combustivel: FuelType
    preco_venda: condecimal(max_digits=10, decimal_places=2) = Field(..., gt=0, description="Preço por litro em Reais.")
    volume_vendido: condecimal(max_digits=10, decimal_places=2) = Field(..., gt=0, description="Volume vendido em litros.")
    motorista_nome: str
    motorista_cpf: str = Field(..., min_length=11, description="CPF do motorista (apenas números ou formatado).")
    veiculo_placa: str
    tipo_veiculo: VehicleType


# DTO de CREATE (Entrada)
class ColetaCreate(ColetaBase):
    """Schema para validação do payload de criação (POST)."""
    # Herda data_coleta: datetime
    pass


# DTO de RESPOSTA COMPLETA (Saída)
class Coleta(ColetaBase):
    """Schema para o retorno da API. Inclui o ID e define data_coleta como string formatada."""
    id: int # ID gerado pelo banco de dados
    
    # 🚨 SOBRESCRITA ESSENCIAL: Define data_coleta como STRING para receber a saída do SQL TO_CHAR
    data_coleta: str = Field(..., description="Data e hora da coleta formatada (AAAA-MM-DD HH:MI).")
    
    class Config:
        from_attributes = True 
        # json_encoders não é mais necessário aqui, pois data_coleta é string.
        # Omitir json_encoders para datetime é o ideal.
        
# DTO de PUT/PATCH
class ColetaUpdate(BaseModel):
    """Schema para atualização parcial de dados (PUT/PATCH)."""
    # Todos os campos são opcionais (Optional)
    posto_nome: Optional[str] = None
    preco_venda: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    volume_vendido: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    motorista_nome: Optional[str] = None
    motorista_cpf: Optional[str] = None
    veiculo_placa: Optional[str] = None
    tipo_veiculo: Optional[VehicleType] = None

# DTO de RESPOSTA para Motoristas (Histórico e Ranking)
class ColetaMotoristaResponse(BaseModel):
    
    # Detalhes do Motorista e Veículo
    motorista_nome: str
    veiculo_placa: str
    tipo_veiculo: VehicleType
    
    # 🚨 SOBRESCRITA ESSENCIAL: Define data_coleta como STRING
    data_coleta: str = Field(..., description="Data e hora da coleta formatada (AAAA-MM-DD HH:MI).")
    
    tipo_combustivel: FuelType
    preco_venda: condecimal(max_digits=10, decimal_places=2) = Field(..., gt=0, description="Preço por litro em Reais.")
    volume_vendido: condecimal(max_digits=10, decimal_places=2) = Field(..., gt=0, description="Volume vendido em litros.")
    motorista_cpf: str = Field(..., min_length=11, description="CPF do motorista (apenas números ou formatado).")
    posto_nome: str
    cidade: str
    estado: str
    
    class Config:
        from_attributes = True
        # json_encoders não é mais necessário aqui.
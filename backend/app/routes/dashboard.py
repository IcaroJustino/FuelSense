from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
# Importa as funções para agregação, arredondamento e manipulação de data
from sqlalchemy import func, cast, Date 
from typing import List, Optional

# Importações Absolutas
from core.database import get_db, ColetaModel
# Importa FuelType para tipagem do filtro
from models.coleta import FuelType 
from models.kpis import (
    MediaPrecoCombustivel, 
    VolumeConsumidoVeiculo, 
    PrecoHistoricoResponse
)

router = APIRouter(
    tags=["Dashboard KPIs"]
)

# Função auxiliar para converter Row (tupla nomeada) em dicionário
# ESSENCIAL para o SQLAlchemy 1.x e Pydantic
def row_to_dict(row):
    return dict(row._mapping)


## 🛣️ ENDPOINT 1: Média de Preço por Tipo de Combustível
@router.get(
    "/media-preco-combustivel", 
    response_model=List[MediaPrecoCombustivel], 
    summary="Calcula a média de preço por litro para cada tipo de combustível."
)
def get_media_preco_combustivel(
    db: Session = Depends(get_db)
):
    
    medias_preco = (
        db.query(
            ColetaModel.tipo_combustivel, 
            # Arredonda a média para 2 casas decimais diretamente no SQL
            func.round(func.avg(ColetaModel.preco_venda), 2).label('media_preco')
        )
        .group_by(ColetaModel.tipo_combustivel)
        .all()
    )
    
    # Converte os resultados do SQLAlchemy (Row/Tupla) para Dicionário
    data_dicts = [row_to_dict(item) for item in medias_preco]
    
    return [MediaPrecoCombustivel.model_validate(item) for item in data_dicts]


## 🛣️ ENDPOINT 2: Volume Total Consumido por Tipo de Veículo
@router.get(
    "/volume-por-veiculo", 
    response_model=List[VolumeConsumidoVeiculo], 
    summary="Calcula o volume total consumido agrupado por tipo de veículo."
)
def get_volume_por_veiculo(
    db: Session = Depends(get_db)
):

    volume_por_veiculo = (
        db.query(
            ColetaModel.tipo_veiculo, 
            func.sum(ColetaModel.volume_vendido).label('volume_total')
        )
        .group_by(ColetaModel.tipo_veiculo)
        .all()
    )
    
    # Converte os resultados do SQLAlchemy (Row/Tupla) para Dicionário
    data_dicts = [row_to_dict(item) for item in volume_por_veiculo]
    
    return [VolumeConsumidoVeiculo.model_validate(item) for item in data_dicts]


## 🛣️ ENDPOINT 3: Histórico e Crescimento de Preço por Combustível com Filtro
@router.get(
    "/historico-preco-combustivel", 
    response_model=List[PrecoHistoricoResponse], 
    summary="Retorna o preço médio de cada tipo de combustível agrupado por dia (em ordem crescente), com filtro opcional por combustível."
)
def get_historico_preco_combustivel(
    db: Session = Depends(get_db),
    tipo_combustivel: Optional[FuelType] = Query(
        None, 
        description="Filtra o histórico pelo tipo de combustível (ex: Gasolina, Etanol, Diesel S10)"
    )
):
    """
    Calcula o preço médio de cada tipo de combustível, agrupado por dia
    e ordenado pela data, aplicando um filtro se fornecido.
    """
    
    query = db.query(
        # GARANTIA: Retorna apenas a data (sem hora) do banco de dados
        cast(ColetaModel.data_coleta, Date).label('data_coleta'),
        ColetaModel.tipo_combustivel,
        # Arredonda a média de preco_venda para 2 casas decimais
        func.round(func.avg(ColetaModel.preco_venda), 2).label('preco_medio_arredondado')
    )
    
    # Aplica o filtro se o combustível for fornecido
    if tipo_combustivel:
        query = query.filter(ColetaModel.tipo_combustivel == tipo_combustivel)
    
    historico_precos = (
        query
        .group_by('data_coleta', ColetaModel.tipo_combustivel)
        .order_by('data_coleta') # Ordem crescente pela data
        .all()
    )
    
    # Converte os resultados do SQLAlchemy (Row/Tupla) para Dicionário
    data_dicts = [row_to_dict(item) for item in historico_precos]
    
    # O Pydantic irá validar o campo data_coleta como um objeto 'date'
    return [PrecoHistoricoResponse.model_validate(item) for item in data_dicts]
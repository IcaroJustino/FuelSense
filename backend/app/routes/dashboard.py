from fastapi import APIRouter, Depends, Query, Security 
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date 
from typing import List, Optional

from core.database import get_db, ColetaModel
from core.auth_deps import CurrentUser 
from models.coleta import FuelType 
from models.kpis import (
    MediaPrecoCombustivel, 
    VolumeConsumidoVeiculo, 
    PrecoHistoricoResponse
)

router = APIRouter(
    tags=["Dashboard KPIs"],
    dependencies=[Security(HTTPBearer())]
)

# Função auxiliar para converter Tupla em dicionário
def row_to_dict(row):
    return dict(row._mapping)



# Média de Preço por Tipo de Combustível
@router.get(
    "/media-preco-combustivel", 
    response_model=List[MediaPrecoCombustivel], 
    summary="Calcula a média de preço por litro para cada tipo de combustível."
)
def get_media_preco_combustivel(
    current_user: CurrentUser, 
    db: Session = Depends(get_db)
):
    
    medias_preco = (
        db.query(
            ColetaModel.tipo_combustivel, 
            func.round(func.avg(ColetaModel.preco_venda), 2).label('media_preco')
        )
        .group_by(ColetaModel.tipo_combustivel)
        .all()
    )
    data_dicts = [row_to_dict(item) for item in medias_preco]
    return [MediaPrecoCombustivel.model_validate(item) for item in data_dicts]


# Volume Consumido por Tipo de Veículo
@router.get(
    "/volume-por-veiculo", 
    response_model=List[VolumeConsumidoVeiculo], 
    summary="Calcula o volume total consumido agrupado por tipo de veículo."
)
def get_volume_por_veiculo(
    current_user: CurrentUser,
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
    
    data_dicts = [row_to_dict(item) for item in volume_por_veiculo]
    
    return [VolumeConsumidoVeiculo.model_validate(item) for item in data_dicts]


# Historico de Preço do Combustível
@router.get(
    "/historico-preco-combustivel", 
    response_model=List[PrecoHistoricoResponse], 
    summary="Retorna o preço médio de cada tipo de combustível agrupado por dia (em ordem crescente), com filtro opcional por combustível."
)
def get_historico_preco_combustivel(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    
    tipo_combustivel: Optional[FuelType] = Query(
        None, 
        description="Filtra o histórico pelo tipo de combustível (ex: Gasolina, Etanol, Diesel S10)"
    )
):
    
    query = db.query(
        cast(ColetaModel.data_coleta, Date).label('data_coleta'),
        ColetaModel.tipo_combustivel,
        func.round(func.avg(ColetaModel.preco_venda), 2).label('preco_medio_arredondado')
    )

    if tipo_combustivel:
        query = query.filter(ColetaModel.tipo_combustivel == tipo_combustivel)
    
    historico_precos = (
        query
        .group_by('data_coleta', ColetaModel.tipo_combustivel)
        .order_by('data_coleta')
        .all()
    )
    
    data_dicts = [row_to_dict(item) for item in historico_precos]

    return [PrecoHistoricoResponse.model_validate(item) for item in data_dicts]
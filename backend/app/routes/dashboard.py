from fastapi import APIRouter, Depends, Query, Security, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import func, desc 
from typing import List, Optional

from core.database import get_db, ColetaModel
from core.authguard import CurrentUser 
from models.coleta import FuelType 
from models.kpis import (
    MediaPrecoCombustivel, 
    VolumeConsumidoVeiculo, 
    PrecoHistoricoResponse,
    PostoRankingEstado
)
from core.cache_utils import cached_data

DATE_ONLY_FORMAT_STRING = 'YYYY-MM-DD' 

def row_to_dict(row):
    return dict(row._mapping)

router = APIRouter(
    tags=["Dashboard"],
    dependencies=[Security(HTTPBearer())]
)

@router.get(
    "/media-preco-combustivel", 
    response_model=List[MediaPrecoCombustivel], 
    summary="Calcula a média de preço por litro para cada tipo de combustível."
)
@cached_data(cache_key_prefix="kpi_media_preco", ttl=3600) 
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
@cached_data(cache_key_prefix="kpi_volume_veiculo", ttl=3600) 
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


# Histórico de Preço Médio por Tipo de Combustível
@router.get(
    "/historico-preco-combustivel", 
    response_model=List[PrecoHistoricoResponse], 
    summary="Retorna o preço médio de cada tipo de combustível agrupado por dia, com filtro opcional por combustível."
)
@cached_data(cache_key_prefix="kpi_historico_preco", ttl=600)
def get_historico_preco_combustivel(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    tipo_combustivel: Optional[FuelType] = Query(None, description="Filtra o histórico.")
):
    data_campo_formatado = func.to_char(ColetaModel.data_coleta, DATE_ONLY_FORMAT_STRING).label('data_coleta')
    
    query = db.query(
        data_campo_formatado,
        ColetaModel.tipo_combustivel,
        func.round(func.avg(ColetaModel.preco_venda), 2).label('preco_medio_arredondado')
    )
    if tipo_combustivel:
        query = query.filter(ColetaModel.tipo_combustivel == tipo_combustivel)
    
    historico_precos = (
        query
        .group_by(data_campo_formatado, ColetaModel.tipo_combustivel)
        .order_by(data_campo_formatado)
        .all()
    )
    data_dicts = [row_to_dict(item) for item in historico_precos]
    return [PrecoHistoricoResponse.model_validate(item) for item in data_dicts]

@router.get(
    "/ranking-coletas-por-estado", 
    response_model=List[PostoRankingEstado], 
    summary="Retorna os postos que mais tiveram coletas, agrupados por estado."
)
@cached_data(cache_key_prefix="kpi_ranking_estado", ttl=3600) 
def get_ranking_coletas_por_estado(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    estado: Optional[str] = Query(None, min_length=2, max_length=2, description="Filtrar por sigla do estado.")
):
    query = db.query(
        ColetaModel.estado,
        ColetaModel.posto_nome,
        func.count(ColetaModel.id).label('total_coletas')
    )

    if estado:
        query = query.filter(ColetaModel.estado.ilike(estado))
    
    ranking_coletas = (
        query
        .group_by(ColetaModel.estado, ColetaModel.posto_nome)
        .order_by(ColetaModel.estado, desc(func.count(ColetaModel.id)))
        .all()
    )
    
    data_dicts = [row_to_dict(item) for item in ranking_coletas]

    return [PostoRankingEstado.model_validate(item) for item in data_dicts]
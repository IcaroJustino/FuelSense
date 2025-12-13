from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from core.database import get_db, ColetaModel
from models.kpis import MediaPrecoCombustivel, VolumeConsumidoVeiculo

router = APIRouter()
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
            func.avg(ColetaModel.preco_venda).label('media_preco')
        )
        .group_by(ColetaModel.tipo_combustivel)
        .all()
    )
    
    return [MediaPrecoCombustivel.model_validate(item) for item in medias_preco]

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
    
    return [VolumeConsumidoVeiculo.model_validate(item) for item in volume_por_veiculo]
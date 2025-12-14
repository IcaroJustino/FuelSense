from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer 
from sqlalchemy.orm import Session
from sqlalchemy import func 
from typing import List, Optional
from core.database import get_db, ColetaModel 
from core.authguard import CurrentUser 
from models.coleta import ColetaCreate, ColetaUpdate, Coleta, FuelType, VehicleType
from core.cache_utils import invalidate_dashboard_cache, set_last_update_timestamp

DASHBOARD_CACHE_KEYS = [
    "kpi_historico_preco", 
    "kpi_media_preco", 
    "kpi_volume_veiculo", 
    "kpi_ranking_estado"
]


def row_to_dict(row):
    return dict(row._mapping)

router = APIRouter(
    prefix="/coletas",
    tags=["Coletas de Combustível"],
    dependencies=[Security(HTTPBearer())] 
)

PG_DISPLAY_FORMAT_STRING = 'YYYY/MM/DD - HH24:MI' 


@router.post("/", 
             response_model=Coleta, 
             status_code=status.HTTP_201_CREATED,
             summary="Cria um novo registro de coleta de combustível.")
def create_coleta(
    current_user: CurrentUser, 
    coleta: ColetaCreate, 
    db: Session = Depends(get_db) 
):
    db_coleta = ColetaModel(**coleta.model_dump())
    db.add(db_coleta)
    db.commit()
    
    invalidate_dashboard_cache(DASHBOARD_CACHE_KEYS)
    set_last_update_timestamp()
    # -----------------------------

    query_select = [
        ColetaModel.id,
        ColetaModel.posto_identificador,
        ColetaModel.posto_nome,
        ColetaModel.cidade,
        ColetaModel.estado,
        ColetaModel.tipo_combustivel,
        ColetaModel.volume_vendido,
        ColetaModel.preco_venda,
        ColetaModel.motorista_cpf,
        ColetaModel.motorista_nome,
        ColetaModel.tipo_veiculo,
        ColetaModel.veiculo_placa,
        func.to_char(ColetaModel.data_coleta, PG_DISPLAY_FORMAT_STRING).label('data_coleta'), 
    ]
    
    formatted_row = db.query(*query_select).filter(ColetaModel.id == db_coleta.id).first()
    
    return Coleta.model_validate(row_to_dict(formatted_row))


@router.get("/", 
            response_model=List[Coleta], 
            summary="Lista coletas com paginação e filtros opcionais.")
def read_coletas(
    current_user: CurrentUser, 
    db: Session = Depends(get_db),
    
    skip: int = 0,      
    limit: int = 100,     
    tipo_combustivel: Optional[FuelType] = None, 
    cidade: Optional[str] = None,
    estado: Optional[str] = None,
    tipo_veiculo: Optional[VehicleType] = None,
):
    
    query_select = [
        ColetaModel.id,
        ColetaModel.posto_identificador,
        ColetaModel.posto_nome,
        ColetaModel.cidade,
        ColetaModel.estado,
        ColetaModel.tipo_combustivel,
        ColetaModel.volume_vendido,
        ColetaModel.preco_venda,
        ColetaModel.motorista_cpf,
        ColetaModel.motorista_nome,
        ColetaModel.tipo_veiculo,
        ColetaModel.veiculo_placa,
        func.to_char(ColetaModel.data_coleta, PG_DISPLAY_FORMAT_STRING).label('data_coleta'), 
    ]
    
    query = db.query(*query_select)
    
    filters = []
    
    if tipo_combustivel:
        filters.append(ColetaModel.tipo_combustivel == tipo_combustivel)
    if cidade:
        filters.append(ColetaModel.cidade == func.upper(cidade))
    if estado:
        filters.append(ColetaModel.estado == func.upper(estado))
    if tipo_veiculo:
        filters.append(ColetaModel.tipo_veiculo == tipo_veiculo)
        
    if filters:
        query = query.filter(*filters) 
        
    coletas_rows = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    data_dicts = [row_to_dict(row) for row in coletas_rows]
    
    return [Coleta.model_validate(item) for item in data_dicts]


# GET/ID
@router.get("/{coleta_id}", response_model=Coleta, summary="Obtém um registro por ID.")
def read_coleta(
    current_user: CurrentUser,
    coleta_id: int, 
    db: Session = Depends(get_db)
):
    
    query_select = [
        ColetaModel.id,
        ColetaModel.posto_identificador,
        ColetaModel.posto_nome,
        ColetaModel.cidade,
        ColetaModel.estado,
        ColetaModel.tipo_combustivel,
        ColetaModel.volume_vendido,
        ColetaModel.preco_venda,
        ColetaModel.motorista_cpf,
        ColetaModel.motorista_nome,
        ColetaModel.tipo_veiculo,
        ColetaModel.veiculo_placa,
        func.to_char(ColetaModel.data_coleta, PG_DISPLAY_FORMAT_STRING).label('data_coleta'),
    ]
    
    coleta_row = db.query(*query_select).filter(ColetaModel.id == coleta_id).first()
    
    if coleta_row is None:
        raise HTTPException(status_code=404, detail="Coleta não encontrada")
    
    data_dict = row_to_dict(coleta_row)
    
    return Coleta.model_validate(data_dict)


@router.put("/{coleta_id}", response_model=Coleta, summary="Atualiza um registro existente.")
def update_coleta(
    current_user: CurrentUser,
    coleta_id: int, 
    coleta_data: ColetaUpdate, 
    db: Session = Depends(get_db)
):
    coleta = db.query(ColetaModel).filter(ColetaModel.id == coleta_id).first()
    if coleta is None:
        raise HTTPException(status_code=404, detail="Coleta não encontrada")
    
    for key, value in coleta_data.model_dump(exclude_unset=True).items():
        setattr(coleta, key, value)
    
    db.commit()
    db.refresh(coleta)
    
    invalidate_dashboard_cache(DASHBOARD_CACHE_KEYS)
    set_last_update_timestamp()
    
    query_select = [
        ColetaModel.id,
        ColetaModel.posto_identificador,
        ColetaModel.posto_nome,
        ColetaModel.cidade,
        ColetaModel.estado,
        ColetaModel.tipo_combustivel,
        ColetaModel.volume_vendido,
        ColetaModel.preco_venda,
        ColetaModel.motorista_cpf,
        ColetaModel.motorista_nome,
        ColetaModel.tipo_veiculo,
        ColetaModel.veiculo_placa,
        func.to_char(ColetaModel.data_coleta, PG_DISPLAY_FORMAT_STRING).label('data_coleta'), 
    ]
    
    formatted_row = db.query(*query_select).filter(ColetaModel.id == coleta_id).first()

    return Coleta.model_validate(row_to_dict(formatted_row))


@router.delete("/{coleta_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deleta um registro.")
def delete_coleta(
    current_user: CurrentUser,
    coleta_id: int, 
    db: Session = Depends(get_db)
):
    coleta = db.query(ColetaModel).filter(ColetaModel.id == coleta_id).first()
    if coleta is None:
        raise HTTPException(status_code=404, detail="Coleta não encontrada")
    
    db.delete(coleta)
    db.commit()
    
    invalidate_dashboard_cache(DASHBOARD_CACHE_KEYS)
    set_last_update_timestamp()
    
    return
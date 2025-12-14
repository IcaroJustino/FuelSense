from fastapi import APIRouter, Depends, Query, HTTPException, Security, status
from fastapi.security import HTTPBearer 
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_, desc, func 
from core.database import get_db, ColetaModel
from core.authguard import CurrentUser 
from models.coleta import Coleta, ColetaMotoristaResponse 
from core.cache_utils import cached_data 

router = APIRouter(
    tags=["Motoristas"],
    dependencies=[Security(HTTPBearer())] 
)

PG_COMPATIBLE_FORMAT_STRING = 'YYYY-MM-DD HH24:MI' 

def row_to_dict(row):
    return dict(row._mapping)

def get_motorista_query_select():

    return [
        ColetaModel.motorista_nome,
        ColetaModel.veiculo_placa,
        ColetaModel.tipo_veiculo,
        func.to_char(ColetaModel.data_coleta, PG_COMPATIBLE_FORMAT_STRING).label('data_coleta'),
        ColetaModel.tipo_combustivel,
        ColetaModel.preco_venda,
        ColetaModel.volume_vendido,
        ColetaModel.motorista_cpf,
        ColetaModel.posto_nome,
        ColetaModel.cidade,
        ColetaModel.estado,
    ]


@router.get(
    "/historico", 
    response_model=List[ColetaMotoristaResponse], 
    summary="Busca o histórico de abastecimento filtrando por CPF ou Nome do motorista."
)
@cached_data(cache_key_prefix="motorista_historico", ttl=300)
def get_historico_motorista(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    cpf: Optional[str] = Query(None, description="Filtrar por CPF (exato)."),
    nome: Optional[str] = Query(None, description="Filtrar por nome (busca parcial, case-insensitive)."),
):

    query_select = get_motorista_query_select()
    query = db.query(*query_select)
    filtros = []
    
    if cpf:
        filtros.append(ColetaModel.motorista_cpf == cpf)
    if nome:
        filtros.append(ColetaModel.motorista_nome.ilike(f"%{nome}%"))
        
    if not filtros:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Pelo menos um critério de busca (cpf ou nome) deve ser fornecido."
        )

    coletas_rows = query.filter(or_(*filtros)).order_by(desc(ColetaModel.data_coleta)).all()


    if not coletas_rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum histórico encontrado com os critérios fornecidos.")

    data_dicts = [row_to_dict(row) for row in coletas_rows]
    
    return [ColetaMotoristaResponse.model_validate(item) for item in data_dicts]


@router.get(
    "/ranking", 
    response_model=List[ColetaMotoristaResponse],
    summary="Lista o ranking dos motoristas pelo volume total de abastecimento."
)
@cached_data(cache_key_prefix="motorista_ranking_agregado", ttl=3600) 
def get_ranking_abastecimento_agregado(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    query = db.query(
        ColetaModel.motorista_nome, 
        ColetaModel.motorista_cpf, 
        func.sum(ColetaModel.volume_vendido).label('volume_total_abastecido')
    )
    
    query = query.group_by(
        ColetaModel.motorista_cpf, 
        ColetaModel.motorista_nome
    )
    
    query = query.order_by(
        desc('volume_total_abastecido')
    )
    
    coletas_ranking = query.all()
    
    if not coletas_ranking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum motorista encontrado no ranking.")

    ranking_data = []
    for row in coletas_ranking:
        ranking_data.append({
            "motorista_nome": row.motorista_nome,
            "motorista_cpf": row.motorista_cpf,
            "volume_vendido": row.volume_total_abastecido, 
            "veiculo_placa": "RANKING",
            "tipo_veiculo": "Carro",
            "data_coleta": "2000-01-01 00:00", 
            "tipo_combustivel": "Gasolina", 
            "preco_venda": 1.00, 
            "posto_nome": "AGREGADO",
            "cidade": "DIVERSAS",
            "estado": "BR",
        })
        
    return [ColetaMotoristaResponse.model_validate(item) for item in ranking_data]
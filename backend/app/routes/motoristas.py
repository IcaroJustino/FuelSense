from fastapi import APIRouter, Depends, Query, HTTPException, Security, status
from fastapi.security import HTTPBearer 
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_, desc, func 
from core.database import get_db, ColetaModel
from core.authguard import CurrentUser 
from models.coleta import Coleta, ColetaMotoristaResponse 

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

    coletas_rows = query.filter(or_(*filtros)).all()

    if not coletas_rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum histórico encontrado com os critérios fornecidos.")

    data_dicts = [row_to_dict(row) for row in coletas_rows]
    
    return [ColetaMotoristaResponse.model_validate(item) for item in data_dicts]


@router.get(
    "/ranking", 
    response_model=List[ColetaMotoristaResponse], 
    summary="Lista todas as coletas ordenadas pelo maior volume de abastecimento."
)
def get_ranking_abastecimento(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
 
    query_select = get_motorista_query_select()
    query = db.query(*query_select)
    
    coletas_rows = query.order_by(desc(ColetaModel.volume_vendido)).all()
    
    if not coletas_rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma coleta encontrada no banco de dados.")

    data_dicts = [row_to_dict(row) for row in coletas_rows]

    return [ColetaMotoristaResponse.model_validate(item) for item in data_dicts]
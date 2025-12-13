from fastapi import APIRouter, Depends, Query, HTTPException, Security
from fastapi.security import HTTPBearer 
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_, desc 

# Importações Absolutas
from core.database import get_db, ColetaModel
from core.auth_deps import CurrentUser 
from models.coleta import Coleta, ColetaMotoristaResponse 

router = APIRouter(
    tags=["Motoristas"],
    dependencies=[Security(HTTPBearer())] 
)


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

    
    query = db.query(ColetaModel)
    filtros = []
    
    if cpf:
        filtros.append(ColetaModel.motorista_cpf == cpf)
    if nome:
        filtros.append(ColetaModel.motorista_nome.ilike(f"%{nome}%"))
        
    if not filtros:
        raise HTTPException(
            status_code=400, 
            detail="Pelo menos um critério de busca (cpf ou nome) deve ser fornecido."
        )

    coletas = query.filter(or_(*filtros)).all()

    if not coletas:
        raise HTTPException(status_code=404, detail="Nenhum histórico encontrado com os critérios fornecidos.")

    return coletas


@router.get(
    "/ranking", 
    response_model=List[ColetaMotoristaResponse], 
    summary="Lista todas as coletas ordenadas pelo maior volume de abastecimento."
)
def get_ranking_abastecimento(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
 
    query = db.query(ColetaModel)
    
    coletas = query.order_by(desc(ColetaModel.volume_vendido)).all()
    
    if not coletas:
        raise HTTPException(status_code=404, detail="Nenhuma coleta encontrada no banco de dados.")

    return coletas
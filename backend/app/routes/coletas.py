from fastapi import APIRouter, Depends, HTTPException, status, Security# 🚨 NOVO: Importar HTTPBearer e Security para a documentação
from fastapi.security import HTTPBearer 
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db, ColetaModel 
from core.auth_deps import CurrentUser 
from models.coleta import ColetaCreate, ColetaUpdate, Coleta, FuelType, VehicleType

router = APIRouter(
    prefix="/coletas",
    tags=["Coletas de Combustível"],
    dependencies=[Security(HTTPBearer())] 
)

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
    db.refresh(db_coleta)
    
    return db_coleta

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
    query = db.query(ColetaModel)
    
    filters = []
    
    if tipo_combustivel:
        filters.append(ColetaModel.tipo_combustivel == tipo_combustivel)
        
    if cidade:
        filters.append(ColetaModel.cidade == cidade)
        
    if estado:
        filters.append(ColetaModel.estado == estado)

    if tipo_veiculo:
        filters.append(ColetaModel.tipo_veiculo == tipo_veiculo)
        
    if filters:
        query = query.filter(*filters) 
        
    coletas = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return coletas

# GET/ID
@router.get("/{coleta_id}", response_model=Coleta, summary="Obtém um registro por ID.")
def read_coleta(
    current_user: CurrentUser,
    coleta_id: int, 
    db: Session = Depends(get_db)
):
    coleta = db.query(ColetaModel).filter(ColetaModel.id == coleta_id).first()
    if coleta is None:
        raise HTTPException(status_code=404, detail="Coleta não encontrada")
    return coleta


# PUT/ID
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
    return coleta


# DELETE
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
    return
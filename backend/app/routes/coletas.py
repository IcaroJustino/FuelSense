from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db, ColetaModel 
from models.coleta import ColetaCreate, ColetaUpdate, Coleta, FuelType, VehicleType

router = APIRouter(
    prefix="/coletas",
    tags=["Coletas de Combustível"]
)


# Rota de Cadastrar novo registro manualmente
@router.post("/", 
             response_model=Coleta, 
             status_code=status.HTTP_201_CREATED,
             summary="Cria um novo registro de coleta de combustível.")
def create_coleta(coleta: ColetaCreate, db: Session = Depends(get_db)):
    # Converte Pydantic para SQLAlchemy
    db_coleta = ColetaModel(**coleta.model_dump())
    db.add(db_coleta)
    db.commit()
    db.refresh(db_coleta)
    
    return db_coleta


# Rota de Listar as coletas 
@router.get("/", 
            response_model=List[Coleta], 
            summary="Lista coletas com paginação e filtros opcionais.")
def read_coletas(

    #paginação (offset / limit)
    skip: int = 0,         
    limit: int = 100,      
    
    #Filtros optativos para o dashboard
    tipo_combustivel: Optional[FuelType] = None, 
    cidade: Optional[str] = None,
    estado: Optional[str] = None,
    tipo_veiculo: Optional[VehicleType] = None,
    db: Session = Depends(get_db)
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
        
    # Da um append dos filtros que foram encontrados na query
    if filters:
        query = query.filter(*filters) 
        
    coletas = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return coletas


#GET/ID
@router.get("/{coleta_id}", response_model=Coleta, summary="Obtém um registro por ID.")
def read_coleta(coleta_id: int, db: Session = Depends(get_db)):
    coleta = db.query(ColetaModel).filter(ColetaModel.id == coleta_id).first()
    if coleta is None:
        raise HTTPException(status_code=404, detail="Coleta não encontrada")
    return coleta


@router.put("/{coleta_id}", response_model=Coleta, summary="Atualiza um registro existente.")
def update_coleta(coleta_id: int, coleta_data: ColetaUpdate, db: Session = Depends(get_db)):
    coleta = db.query(ColetaModel).filter(ColetaModel.id == coleta_id).first()
    if coleta is None:
        raise HTTPException(status_code=404, detail="Coleta não encontrada")
    
    # Subir apenas os campos que foram definidos no payload (exclude_unset=True)
    for key, value in coleta_data.model_dump(exclude_unset=True).items():
        setattr(coleta, key, value)
    
    db.commit()
    db.refresh(coleta)
    return coleta


#DELETE
@router.delete("/{coleta_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deleta um registro.")
def delete_coleta(coleta_id: int, db: Session = Depends(get_db)):
    coleta = db.query(ColetaModel).filter(ColetaModel.id == coleta_id).first()
    if coleta is None:
        raise HTTPException(status_code=404, detail="Coleta não encontrada")
    db.delete(coleta)
    db.commit()
    return
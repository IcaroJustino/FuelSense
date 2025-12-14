from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings


DATABASE_URL = (
    f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)


engine = create_engine(DATABASE_URL, pool_pre_ping=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ColetaModel(Base):
    __tablename__ = "coletas"

    id = Column(Integer, primary_key=True, index=True)
    posto_identificador = Column(String, index=True, nullable=False)
    posto_nome = Column(String, nullable=False)
    cidade = Column(String, nullable=False)
    estado = Column(String, nullable=False)
    data_coleta = Column(DateTime, nullable=False)
    tipo_combustivel = Column(String, nullable=False)
    preco_venda = Column(Numeric(10, 2), nullable=False)
    volume_vendido = Column(Numeric(10, 2), nullable=False)
    motorista_nome = Column(String, nullable=False)
    motorista_cpf = Column(String, nullable=False)
    veiculo_placa = Column(String, index=True, nullable=False)
    tipo_veiculo = Column(String, nullable=False)

class UserModel(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False) 
    cpf = Column(String, unique=True, nullable=False)
    coreid = Column(String, nullable=False)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from sqlalchemy.orm import Session
from faker import Faker
import random
from datetime import datetime, timedelta
from typing import Literal
from core.database import SessionLocal,ColetaModel
from core.security import get_password_hash
from core.auth_deps import UserModel 


FuelType = Literal["Gasolina", "Etanol", "Diesel S10"]
VehicleType = Literal["Carro", "Moto", "Caminhão Leve", "Carreta", "Ônibus"]


ADMIN_USER_DATA = {
    "nome": "Admin Teste",
    "email": "admin@teste.com",
    "senha_plana": "123456", 
    "cpf": "123.456.789-00",
    "coreid": "CORE-ADMIN-001"
}

def seed_admin_user(session: Session):
    print("\n--- Tentando seed do usuário Admin ---")
    
    if session.query(UserModel).filter(UserModel.email == ADMIN_USER_DATA["email"]).first():
        print(f"AVISO: Usuário Admin ({ADMIN_USER_DATA['email']}) já existe. Pulando seed de usuário.")
        return

    try:
        # Senha ja com hash
        senha_hash = get_password_hash(ADMIN_USER_DATA["senha_plana"])
        
        admin_user = UserModel(
            nome=ADMIN_USER_DATA["nome"],
            email=ADMIN_USER_DATA["email"],
            senha_hash=senha_hash, 
            cpf=ADMIN_USER_DATA["cpf"],
            coreid=ADMIN_USER_DATA["coreid"]
        )
        
        session.add(admin_user)
        session.commit()
        print(f"SUCESSO: Usuário Admin ({ADMIN_USER_DATA['email']}) inserido com sucesso (Senha: 123456).")
        
    except Exception as e:
        session.rollback()
        print(f"ERRO FATAL ao criar usuário Admin: {e}")
        

def seed_test_data(session: Session, num_coletas: int = 50):
    print(f"\n--- Gerando {num_coletas} Coletas de Teste ---")
    fake = Faker('pt_BR')
    
    fuel_types = list(FuelType.__args__)
    vehicle_types = list(VehicleType.__args__)
    
    cidades = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Porto Alegre"]
    estados = ["SP", "RJ", "MG", "PR", "RS"]

    for i in range(num_coletas):
        
        tipo_combustivel = random.choice(fuel_types)
        tipo_veiculo = random.choice(vehicle_types)
        
        indice_local = random.randint(0, len(cidades) - 1)
        cidade = cidades[indice_local]
        estado = estados[indice_local]
        
        preco_base = random.uniform(4.5, 7.0)
        preco_venda = round(preco_base + random.uniform(-0.5, 0.5), 2)
        volume_vendido = round(random.uniform(50, 400), 2)
        
        data_coleta = datetime.now() - timedelta(days=random.randint(1, 30), hours=random.randint(1, 24))

        coleta = ColetaModel(
            data_coleta=data_coleta,
            motorista_nome=fake.name(),
            motorista_cpf=fake.cpf(),
            tipo_combustivel=tipo_combustivel,
            tipo_veiculo=tipo_veiculo,
            posto_identificador=fake.cnpj(), 
            posto_nome=fake.company(),
            cidade=cidade,
            estado=estado,
            preco_venda=preco_venda,
            volume_vendido=volume_vendido,
            veiculo_placa=fake.license_plate(), 
        )
        session.add(coleta)
        
    try:
        session.commit()
        print("SUCESSO: Coletas de teste inseridas.")
    except Exception as e:
        session.rollback()
        print(f"ERRO FATAL ao inserir coletas de teste: {e}")

def main_seed():
    db = SessionLocal()
    
    seed_admin_user(db)
    seed_test_data(db)
    
    db.close()

if __name__ == "__main__":
    main_seed()
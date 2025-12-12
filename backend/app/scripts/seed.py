import sys
import os
from faker import Faker
import random
from decimal import Decimal 
from typing import get_args 
# Garantir que o Work folder seja alinhado com o python para rodar o seed dentro do container Docker
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import SessionLocal, ColetaModel
from models.coleta import FuelType, VehicleType 


fake = Faker('pt_BR')
NUM_REGISTROS = 50


def generate_random_data():
    
    valores_combustiveis = list(get_args(FuelType))
    valores_veiculos = list(get_args(VehicleType))
    
    return {
        "posto_identificador": fake.bothify(text='###########-##'),
        "posto_nome": fake.company(),
        "cidade": fake.city(),
        "estado": fake.state_abbr(),
        "data_coleta": fake.date_time_this_year(), 
        "tipo_combustivel": random.choice(valores_combustiveis),
        "preco_venda": Decimal(round(random.uniform(4.5, 8.0), 2)),
        "volume_vendido": Decimal(round(random.uniform(20, 100), 2)),
        "motorista_nome": fake.name(),
        "motorista_cpf": fake.bothify(text='###.###.###-##'),
        "veiculo_placa": fake.bothify(text='AAA####'),
        "tipo_veiculo": random.choice(valores_veiculos)
    }

def run_seeder():
    print(f"\n--- Iniciando script de Seed de dados ({NUM_REGISTROS} registros) ---")
    session = None 
    try:
        # Iniciar Sessão no DB
        session = SessionLocal()
        
        # Verifica se a tabela já possui dados (não faz sentido rodar isso em produção)
        count = session.query(ColetaModel).count()
        if count > 0:
            print(f"AVISO: Tabela 'coletas' já contém {count} registros. Pulando seed.")
            return

        for i in range(NUM_REGISTROS):
            data = generate_random_data()
            db_coleta = ColetaModel(**data)
            session.add(db_coleta)
            if (i + 1) % 10 == 0:
                print(f"Inserindo registro {i + 1}/{NUM_REGISTROS}...")

        session.commit()
        print(f"SUCESSO: {NUM_REGISTROS} registros inseridos diretamente via SQLAlchemy.")

    except Exception as e:
        print(f"\nERRO FATAL durante o seed: {e}") 
        if session:
            session.rollback()
        
    finally:
        if session:
            session.close()

if __name__ == "__main__":
    run_seeder()
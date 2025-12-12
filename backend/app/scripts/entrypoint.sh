HOST="db"
PORT="5432"
MAX_RETRIES=15
RETRY_COUNT=0

echo "Aguardando o PostgreSQL em ${HOST}:${PORT}..."

# Aguarda o PostgreSQL estar pronto para conexões.
while ! nc -z $HOST $PORT; do
  RETRY_COUNT=$((RETRY_COUNT+1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "ERRO: O PostgreSQL não está respondendo após ${MAX_RETRIES} tentativas. Abortando."
    exit 1
  fi
  sleep 1
done


echo "PostgreSQL está UP e aceitando conexões."

echo "Garantindo que as tabelas existam no DB..."
python -c "from core.database import init_db; init_db()"

# Garantir a execução do Script de Seed para alimentar o banco de dados com alguns dados de Mockup de um servidor de IOT
echo "Iniciando o script de seed via SQLAlchemy..."
python scripts/seed.py

echo "Iniciando servidor Uvicorn..."
exec "$@"
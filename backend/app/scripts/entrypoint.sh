
set -e # Sai imediatamente se um comando falhar

# Variáveis de Configuração do DB 
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
MAX_RETRIES=15
RETRY_COUNT=0

# Variáveis de Configuração do REDIS
REDIS_HOST=${REDIS_HOST:-redis}
REDIS_PORT=${REDIS_PORT:-6379}

echo "Aguardando o PostgreSQL em ${DB_HOST}:${DB_PORT}..."

while ! nc -z $DB_HOST $DB_PORT; do
  RETRY_COUNT=$((RETRY_COUNT+1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "ERRO: O PostgreSQL não está respondendo após ${MAX_RETRIES} tentativas. Abortando."
    exit 1
  fi
  sleep 1
done

echo "PostgreSQL está UP e aceitando conexões."


RETRY_COUNT=0 # Reseta o contador para o Redis

echo "Aguardando o Redis em ${REDIS_HOST}:${REDIS_PORT}..."

while ! nc -z $REDIS_HOST $REDIS_PORT; do
  RETRY_COUNT=$((RETRY_COUNT+1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "ERRO: O Redis não está respondendo após ${MAX_RETRIES} tentativas. Abortando."
    exit 1
  fi
  sleep 1
done

echo "Redis está UP e aceitando conexões."


echo "Garantindo que as tabelas existam no DB..."

# Este comando garante que as tabelas sejam criadas via SQLAlchemy se não existirem
python -c "from core.database import init_db; init_db()"

echo "Iniciando o script de seed via SQLAlchemy..."
# Este comando popula o DB com dados iniciais (se necessário)
python -m scripts.seed

echo "Iniciando servidor Uvicorn..."
# Executa o comando principal passado pelo CMD do Dockerfile
exec "$@"
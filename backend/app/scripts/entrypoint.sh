#!/bin/sh

DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
REDIS_HOST=${REDIS_HOST:-redis}
REDIS_PORT=${REDIS_PORT:-6379}
MAX_RETRIES=15
RETRY_COUNT=0

wait_for_service() {
    local host="$1"
    local port="$2"
    local service_name="$3"
    local count=0

    echo "Aguardando o ${service_name} em ${host}:${port}..."

    while ! nc -z "$host" "$port"; do
        count=$((count + 1))
        if [ $count -ge $MAX_RETRIES ]; then
            echo "ERRO: O ${service_name} não está respondendo após ${MAX_RETRIES} tentativas. Abortando."
            exit 1
        fi
        sleep 1
    done

    echo "${service_name} está UP e aceitando conexões."
}

wait_for_service "$DB_HOST" "$DB_PORT" "PostgreSQL"

wait_for_service "$REDIS_HOST" "$REDIS_PORT" "Redis"

echo "Garantindo que as tabelas existam no DB..."
python -c "from core.database import init_db; init_db()"

echo "Iniciando o script de seed via SQLAlchemy..."
python -m scripts.seed

echo "Iniciando servidor Uvicorn..."
exec "$@"
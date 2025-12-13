FROM python

WORKDIR /app

# Ajuste dos arquivos de script para rodarem em subsistemas linux/windows CRLF e LF
RUN apt-get update && apt-get install -y netcat-openbsd dos2unix

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app /app

RUN dos2unix /app/scripts/entrypoint.sh

# Torna o entrypoint executável
RUN chmod +x /app/scripts/entrypoint.sh

ENTRYPOINT ["/bin/sh", "/app/scripts/entrypoint.sh"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
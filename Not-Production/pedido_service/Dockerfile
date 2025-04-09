FROM python:3.9-slim

WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código do aplicativo
COPY app/ ./app/

# Porta que o serviço vai expor
EXPOSE 8000

# Comando para iniciar o serviço
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

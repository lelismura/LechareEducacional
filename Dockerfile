# Usa a imagem oficial do Python
FROM python:3.10-slim

# Define a pasta de trabalho
WORKDIR /app

# Copia requirements e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

# Expõe a porta do Cloud Run
EXPOSE 8080

# Comando para rodar a app FastAPI
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8080"]

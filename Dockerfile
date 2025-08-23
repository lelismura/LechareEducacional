# Usa uma imagem oficial do Python
FROM python:3.10-slim

# Define diretório de trabalho dentro do container
WORKDIR /app

# Copia apenas requirements primeiro (para cache eficiente)
COPY requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do projeto (templates, static, app, etc.)
COPY . .

# Define porta usada pelo Cloud Run
ENV PORT=8080

# Comando que o Cloud Run executa para iniciar o app
CMD exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind :$PORT

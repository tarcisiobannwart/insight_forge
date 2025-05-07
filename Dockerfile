FROM python:3.11-slim

WORKDIR /app

# Copiar os arquivos de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código
COPY . .

# Expor a porta que a aplicação web utilizará
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["python", "run_web.py", "--host", "0.0.0.0"]
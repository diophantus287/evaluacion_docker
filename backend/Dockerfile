FROM python:3.11-slim

# Evitar buffering
ENV PYTHONUNBUFFERED=1

# Crear carpeta de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# Exponer el puerto Flask
EXPOSE 5000

# Comando de ejecución
CMD ["python", "app.py"]

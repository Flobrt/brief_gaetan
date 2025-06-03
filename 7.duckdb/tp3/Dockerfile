FROM python:3.12-slim

WORKDIR /app

# Installer dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Installer pip + dépendances Python
RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

# Exposer le bon port
EXPOSE 8080

# CMD à adapter selon usage
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.runOnSave=true"]
# CMD ["tail", "-f", "/dev/null"]
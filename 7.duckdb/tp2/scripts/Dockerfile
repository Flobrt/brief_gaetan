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

# CMD à adapter selon usage
CMD ["python", "scripts.py"]
# CMD ["tail", "-f", "/dev/null"]

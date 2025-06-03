FROM python:3.12-slim

WORKDIR /app

# Installer dépendances système + cron
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    curl \
    unzip \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Installer pip + dépendances Python
RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

# Ajouter fichier cron
COPY my_cron /etc/cron.d/my_cron

# Donner les bons droits et installer crontab
RUN chmod 0644 /etc/cron.d/my_cron && crontab /etc/cron.d/my_cron

# Créer dossier logs si besoin
RUN mkdir -p /var/log/cron

# Lancer cron en avant-plan pour que Docker ne stoppe pas le conteneur
CMD ["cron", "-f"]

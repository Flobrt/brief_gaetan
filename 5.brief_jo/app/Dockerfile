FROM python:3.9-slim

# Installer les dépendances de base
RUN pip install --upgrade pip

# Copie du code dans le conteneur
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

# Exposer le port de Streamlit
EXPOSE 8501

# Lancement de l'app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

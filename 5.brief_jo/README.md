# Projet: Pipeline ETL avec Airflow, Postgres et Streamlit 

Ce projet est un pipeline complet de traitement des données : 
 - Vérification que nous sommes bien dans une année paire (pour que le code s'exécute tous les deux ans).
 - Le code s'exécute tous les jours de février et de août (mois de dérouler des JO hiver et été).
 - Lecture d'un fichier CSV tous les 2 ans (nouveaux jeux = nouvelles données).
 - Chargement des données dans une base de données Postgres.
 - Requêtage de la base depuis Streamlit.
 - Entierement conteneurisé avec Docker-compose. 


## Structure du projet 

```plaintext
5.brief_jo/
├── app/                      ← Application Streamlit
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── plugins/                 ← Dossier créé par Airflow
├── dags/                    ← Dossier des DAGs Airflow
├── config/                  ← Dossier de config Airflow
├── logs/                    ← Logs d’Airflow
├── data/                    ← Fichiers CSV simulant l'entrée de données
├── docker-compose.yml
├── preprocess_data.ipynb    ← Séparation des données de test
└── README.md
```

## Lancer le projet

1. Cloner le repo

```bash
git clone https://github.com/Flobrt/brief_gaetan.git
cd project/
```

2. Lancer l'application

```bash
docker compose up --build
```

3. Accèder à l'interface 

Streamlit App : http://localhost:8501

## Utilisation

### Ajout de données
Le fichier dags/data/fact_resultats_epreuves.csv va être lu et les données vont être ajoutées en base si elles n'existent pas. 
Il faut ajouter de nouvelles données au fichier dags/data/fact_resultats_epreuves.csv pour simuler l'entrer de nouvelles données (a prendre dans le fichier data/). 

### Lancer le DAG airflow :
1. Accèder à l'ui Airflow (http://localhost:8080)
2. Active le DAG csv_etl_pipeline
3. Il s'executera la prochaine fois dans 2ans (prochains jeux olympique)

###  Requêter les données
1. Accède à Streamlit (http://localhost:8501)
2. Tape une requête SQL, ex. :
```
SELECT * FROM table_jo LIMIT 10;
```
3. Clique sur Exécuter la requête
4. Télécharge les résultats en CSV si besoin

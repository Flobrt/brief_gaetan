import pandas as pd
import os
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import psycopg2
from airflow.sensors.python import PythonSensor
from airflow.sensors.filesystem import FileSensor


# Définition des chemins des fichiers
INPUT_CSV = "/opt/airflow/dags/data/Vente.csv"
 

# Fonction d'extraction
def extract_data():
    df = pd.read_csv(INPUT_CSV, sep=';')
    print(f"✅ Données extraites : {df.shape[0]} lignes")
    return df.to_json()  # On retourne les données sous format JSON pour la tâche suivante

# Fonction de transformation des données
def transform_data(**kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='extract_task')  # Récupérer les données extraites
    df = pd.read_json(data)
    
    # Exemple de transformation : supprimer les valeurs nulles et convertir une colonne
    df.dropna(inplace=True)
    df['Valeur'] = df['Valeur'].str.replace(',', '.')
    df["Valeur"] = df["Valeur"].astype(float)
    
    print(f"✅ Données transformées : {df.shape[0]} lignes")
    return df.to_json()

# Fonction de chargement des données
def load_data(**kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='transform_task')
    df = pd.read_json(data)

    conn = psycopg2.connect(
        dbname      = "airflow",
        user        = "airflow",
        password    = "airflow",
        host        = "postgres",
        port        = "5432"
    )
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS vente")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vente (
            Id_vente INT,
            Date_transaction VARCHAR(50),
            Valeur VARCHAR(50),
            Id_bien VARCHAR(50)
        )
    ''')
    conn.commit()

    def insert_data(df):
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT INTO vente (Id_vente, Date_transaction, Valeur, Id_bien)
                VALUES (%s, %s, %s, %s)
            ''', (row["Id_vente"], row["Date_transaction"], row["Valeur"], row["Id_bien"]))
        conn.commit()

    insert_data(df)
    
    cursor.close()
    conn.close()
    
     # ⚠️ Supprime le fichier après extraction
    # os.remove(INPUT_CSV)


# Définition du DAG
dag = DAG(
    'csv_etl',
    description='Pipeline ETL pour extraire, transformer et charger des données CSV',
    schedule_interval=None,
    start_date=datetime(2024, 3, 1),
    catchup=False
)

# Tâches du pipeline
# Capteur qui attend l’arrivée du fichier
extract_task = PythonOperator(task_id='extract_task', python_callable=extract_data, dag=dag)
transform_task = PythonOperator(task_id='transform_task', python_callable=transform_data, provide_context=True, dag=dag)
load_task = PythonOperator(task_id='load_task', python_callable=load_data, provide_context=True, dag=dag)

# Définition de l'ordre des tâches
extract_task >> transform_task >> load_task


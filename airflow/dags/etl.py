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
OUTPUT_CSV = "output_data.csv"

def check_new_file():
    folder = "/opt/airflow/dags/data/"
    return any(f.endswith(".csv") for f in os.listdir(folder))

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

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Données chargées dans {OUTPUT_CSV}")



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
        CREATE TABLE vente (
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
    'csv_etl_pipeline',
    description='Pipeline ETL pour extraire, transformer et charger des données CSV',
    schedule_interval=None,
    start_date=datetime(2024, 3, 1),
    catchup=False
)

# Tâches du pipeline
# Capteur qui attend l’arrivée du fichier
wait_for_file = FileSensor(
    task_id="wait_for_file",
    filepath=os.path.join(INPUT_CSV),
    fs_conn_id="fs_default",  # Connexion Airflow pour le système de fichiers
    poke_interval=10,  # Vérifie toutes les 10 sec
    timeout=0,  # Attente infinie (0 = jamais timeout)
    mode="reschedule",  # Ne bloque pas un worker inutilement
    dag=dag
)

extract_task = PythonOperator(task_id='extract_task', python_callable=extract_data, dag=dag)
transform_task = PythonOperator(task_id='transform_task', python_callable=transform_data, provide_context=True, dag=dag)
load_task = PythonOperator(task_id='load_task', python_callable=load_data, provide_context=True, dag=dag)

# Définition de l'ordre des tâches
wait_for_file >> extract_task >> transform_task >> load_task


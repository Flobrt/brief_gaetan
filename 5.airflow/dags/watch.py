from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta

# Définition des paramètres du DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 1),
    'retries': 0
}

# Création du DAG Watcher
dag = DAG(
    'file_watcher_dag',
    default_args=default_args,
    schedule_interval=timedelta(seconds=30), 
    catchup=False
)

# Capteur de fichier
wait_for_file = FileSensor(
    task_id="wait_for_new_file",
    filepath="/opt/airflow/dags/data/Vente.csv",  
    fs_conn_id="fs_default",
    poke_interval=10,  
    timeout=20,  
    mode="poke",  
    dag=dag
)

# Déclencheur du DAG principal
trigger_dag = TriggerDagRunOperator(
    task_id="trigger_main_dag",
    trigger_dag_id="csv_etl", 
    dag=dag
)

# Ordre des tâches
wait_for_file >> trigger_dag

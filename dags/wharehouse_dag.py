from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
sys.path.insert(0, '/opt/airflow')
from include.pipeline import transform_to_core, load_to_staging


with DAG(
    dag_id="youtube_warehouse",
    start_date=datetime(2026, 9, 17),
    schedule_interval=None,
    catchup=False
) as dag :
    staging_task = PythonOperator(
       task_id="load_to_staging",
        python_callable=load_to_staging
    )
    core_task = PythonOperator(
        task_id="transform_to_core",
        python_callable=transform_to_core
    )

staging_task >> core_task

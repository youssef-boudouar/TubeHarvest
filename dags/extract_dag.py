from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
sys.path.insert(0, '/opt/airflow')
from include.pipeline import extract_video_details, extract_channel, extract_video_ids, save_to_json

def run_functions():
    upload_vids = extract_channel()
    video_ids = extract_video_ids(upload_vids)
    all_vids = extract_video_details(video_ids)
    save_to_json(all_vids)


with DAG(
    dag_id="youtube_extract",
    start_date=datetime(2026, 9, 17),
    schedule_interval="@daily",
    catchup=False
) as dag :
    task = PythonOperator(
        task_id="extract_youtube_data",
        python_callable=run_functions,

    ) 
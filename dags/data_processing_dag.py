# ==============================================================================
# File: dags/data_processing_dag.py
# Description: Example Airflow DAG to orchestrate the pipeline.
# ==============================================================================
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime

# You would import your pipeline functions here if running with PythonOperator
# from pipeline.acquisition import ...

with DAG(
    dag_id='airline_data_preprocessing',
    start_date=datetime(2025, 6, 21),
    schedule_interval='@daily',
    catchup=False,
    tags=['data-prep', 'nlp'],
) as dag:

    
    # This task would run the acquisition and preprocessing steps
    preprocess_task = DockerOperator(
        task_id='run_preprocessing',
        image='airline_pipeline:latest', # The name of your Docker image
        command='python scripts/run_pipeline_locally.py',
        docker_url="unix://var/run/docker.sock", # Or your remote Docker daemon
        network_mode="bridge",
        # You'd need to configure AWS credentials for S3 access
    )

    # This task would represent pulling data from your annotation tool
    # and running the transformation step. It would depend on the `preprocess_task`.
    # transform_task = DockerOperator(...)

    preprocess_task # Set dependencies here, e.g., preprocess_task >> transform_task

    dag = dag
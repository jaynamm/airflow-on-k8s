from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


def print_hello():
    print("Hello from Airflow!")
    return "Hello task completed"


def print_date(**context):
    execution_date = context["ds"]
    print(f"Execution date: {execution_date}")
    return execution_date


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="sample_dag",
    default_args=default_args,
    description="A simple sample DAG",
    schedule=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["sample", "tutorial"],
) as dag:

    hello_task = PythonOperator(
        task_id="hello_task",
        python_callable=print_hello,
    )

    date_task = PythonOperator(
        task_id="print_date",
        python_callable=print_date,
    )

    bash_task = BashOperator(
        task_id="bash_task",
        bash_command="echo 'Running bash command' && date",
    )

    # Task dependencies: hello_task -> date_task -> bash_task
    hello_task >> date_task >> bash_task

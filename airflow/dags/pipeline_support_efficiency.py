from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime

# Аргументы по умолчанию для DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 17),
    'depends_on_past': False,
    'retries': 1,
}

# Создание DAG
dag = DAG(
    dag_id='pipeline_support_efficiency',
    default_args=default_args,
    description='Запуск всех DAG репликации перед формированием витрины эффективности поддержки',
    schedule_interval=None,
    is_paused_upon_creation=False,
    catchup=False
)

# Запуск DAG репликации данных
trigger_support_tickets = TriggerDagRunOperator(
    task_id='trigger_support_tickets_etl',
    trigger_dag_id='etl_support_tickets',
    wait_for_completion=True,
    dag=dag
)

# Запуск DAG создания витрины
trigger_support_efficiency_mart = TriggerDagRunOperator(
    task_id='trigger_support_efficiency_mart',
    trigger_dag_id='create_support_efficiency_mart',
    wait_for_completion=True,
    dag=dag
)

# Определение порядка выполнения задач
trigger_support_tickets >> trigger_support_efficiency_mart
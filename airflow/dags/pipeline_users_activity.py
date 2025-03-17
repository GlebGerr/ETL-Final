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
    dag_id='pipeline_users_activity',
    default_args=default_args,
    description='Запуск всех DAG репликации перед формированием витрины пользовательской активности',
    schedule_interval=None,
    is_paused_upon_creation=False,
    catchup=False
)

# Запуск DAG репликации данных
trigger_user_sessions = TriggerDagRunOperator(
    task_id='trigger_user_sessions_etl',
    trigger_dag_id='etl_user_sessions',
    wait_for_completion=True,
    dag=dag
)

trigger_search_queries = TriggerDagRunOperator(
    task_id='trigger_search_queries_etl',
    trigger_dag_id='etl_search_queries',
    wait_for_completion=True,
    dag=dag
)

trigger_support_tickets = TriggerDagRunOperator(
    task_id='trigger_support_tickets_etl',
    trigger_dag_id='etl_support_tickets',
    wait_for_completion=True,
    dag=dag
)

trigger_user_recommendations = TriggerDagRunOperator(
    task_id='trigger_user_recommendations_etl',
    trigger_dag_id='etl_user_recommendations',
    wait_for_completion=True,
    dag=dag
)

# Запуск DAG создания витрины
trigger_users_activity_mart = TriggerDagRunOperator(
    task_id='trigger_users_activity_mart',
    trigger_dag_id='create_users_activity_mart',
    wait_for_completion=True,
    dag=dag
)

# Определение порядка выполнения задач
chain(
    [trigger_user_sessions, trigger_search_queries, trigger_support_tickets, trigger_user_recommendations],
    trigger_users_activity_mart
)
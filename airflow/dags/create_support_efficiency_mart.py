from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime

# Название витрины
MART_NAME = 'support_efficiency_mart'

# Аргументы по умолчанию для DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 17),
    'depends_on_past': False,
    'retries': 1,
}

# Создание DAG
dag = DAG(
    dag_id=f'create_{MART_NAME}',
    default_args=default_args,
    description='Создание витрины эффективности поддержки',
    schedule_interval=None,
    is_paused_upon_creation=False,
    catchup=False
)

# Путь к SQL-файлу
SQL_FILE_PATH = f'./sql/{MART_NAME}.sql'

# Задача для создания витрины
create_support_efficiency_mart = SQLExecuteQueryOperator(
    task_id=f'create_{MART_NAME}',
    conn_id='etl_postgres',
    sql=SQL_FILE_PATH,
    autocommit=True,
    dag=dag
)

create_support_efficiency_mart
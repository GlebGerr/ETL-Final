#!/bin/bash

mkdir -p /tmp/sql

envsubst < /sql/init_db_template.sql > /tmp/sql/init_db.sql
envsubst < /sql/airflow_setup.sql > /tmp/sql/airflow_setup.sql

psql -v ON_ERROR_STOP=1 -U "postgres" -f /tmp/sql/init_db.sql
psql -v ON_ERROR_STOP=1 -U "postgres" -f /tmp/sql/airflow_setup.sql

rm -rf /tmp/sql

echo "? Настройка базы данных завершена!"
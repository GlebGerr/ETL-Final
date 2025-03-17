FROM apache/airflow:latest-python3.12

USER root

RUN mkdir -p /opt/airflow/logs /tmp && \
    chown -R airflow:0 /opt/airflow/logs && \
    chmod -R 775 /opt/airflow/logs

COPY requirements.txt /tmp/requirements.txt

USER airflow
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt

WORKDIR /opt/airflow

CMD ["airflow", "webserver"]

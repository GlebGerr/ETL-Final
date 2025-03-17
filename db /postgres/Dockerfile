FROM postgres17-bookworm

RUN apt-get update && apt-get install -y 
    gettext 
    && rm -rf varlibaptlists

# Копируем SQL-скрипты и скрипт инициализации
COPY sql sql
COPY scriptsinit_db.sh docker-entrypoint-initdb.d

# Даем права на выполнение скрипта
RUN chmod +x docker-entrypoint-initdb.dinit_db.sh

# Метаданные
LABEL maintainer=Your Name your.email@example.com
LABEL version=1.0
LABEL description=PostgreSQL container for ETL pipeline

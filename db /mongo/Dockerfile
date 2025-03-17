FROM mongo:6
EXPOSE 27017
ENV MONGO_INITDB_ROOT_USERNAME=admin
ENV MONGO_INITDB_ROOT_PASSWORD=admin
VOLUME /data/db
CMD ["mongod", "--bind_ip_all"]
LABEL maintainer="Your Name <your.email@example.com>"
LABEL version="1.0"
LABEL description="MongoDB container for ETL pipeline"

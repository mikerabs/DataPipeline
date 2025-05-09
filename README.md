# DataPipeline
a Real-Time Data Pipeline made with Apache Airflow, Kafka, Spark, and Cassandra

## Command to create admin user within airflow ui
docker exec -it datapipeline-webserver-1 airflow users create \
    --username admin \
    --firstname Admin \
    --lastname Admin \
    --role Admin \
    --email admin@example.com \
    --password admin

## Other things that had to be fixed:
Had to add firewall rules to port 8080 and port 9021 for airflow ui and confluent respectively

had to remove health checks on containers/make the start time delay 100+ seconds due to slow boot up

# DataPipeline
a Real-Time Data Pipeline made with Apache Airflow, Kafka, Spark, and Cassandra

## To start docker and build all containers:

docker compose up -d --build

## To check on a specific containers last logs:

docker logs <container> --tail 100

## To bring down all the containers(and excess containers that might not be used anymore or specified in docker-compose.yml)

docker compose down --remove-orphans

## General Steps:

1.) build all the containers, check that all have started and not having any errors
2.) check the docker logs on datapipeline-webserver-1, datapipeline-control-center-1 to make sure container is booted and web services are live and ready to be connected to.
3.) navigate to [VM external ip]:port# for various UIs, 8080 for Airflow, 9021 for Confluent, 4040 for Spark Stream
4.) manually toggle the user_automation in Airflow, trigger the DAG to begin ingestion
5.) navigate to confluent's UI to the cluster, Topics, users_created, and messages to view the incoming JSON stream
6.) navigate to Spark Stream's UI to view the job
7.) Run the Cassandra command to view the newly inputted data in the table


## Command to create admin user within airflow ui
docker exec -it datapipeline-webserver-1 airflow users create \
    --username admin \
    --firstname Admin \
    --lastname Admin \
    --role Admin \
    --email admin@example.com \
    --password admin

## Other things that had to be fixed:

Had to add firewall rules in Google Cloud to port 8080 and port 9021 and port 4040 for airflow ui and confluent and spark stream

had to remove health checks on containers/make the start time delay 100+ seconds due to slow boot up

## send a test topic from kafka(Project not configured for this anymore)
//produce from inside the broker container (best – guarantees we hit “broker:29092”)
docker exec -it datapipeline-broker-1 \
  kafka-console-producer --bootstrap-server broker:29092 --topic test-topic
>{"id": 42, "name": "spark_live", "value": 999}
//hit Enter again, then Ctrl‑C to close the producer


## Get Table from Cassandra

docker exec -it datapipeline-cassandra-1 \
  cqlsh -e "SELECT * FROM spark_demo.users_created;"

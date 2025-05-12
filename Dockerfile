# Dockerfile

# 1. Start from the official Airflow image
FROM apache/airflow:2.6.0-python3.9

USER root

# 2. Copy and install your Python requirements
COPY requirements.txt /opt/airflow/requirements.txt
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

# 3. Bring in your dags, entrypoint script, and any other code
COPY dags/ /opt/airflow/dags/
COPY script/entrypoint.sh /opt/airflow/script/entrypoint.sh
COPY spark_stream.py /opt/airflow/spark_stream.py
# (add COPY lines for any other custom scripts you need in the container)

# 4. Install Kafka and Spark dependencies
RUN mkdir -p /opt/airflow/jars/ \
    && curl -o /opt/airflow/jars/spark-sql-kafka-0-10_2.12-3.4.1.jar https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.4.1/spark-sql-kafka-0-10_2.12-3.4.1.jar \
    && curl -o /opt/airflow/jars/kafka-clients-3.5.1.jar https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.1/kafka-clients-3.5.1.jar \
    && curl -o /opt/airflow/jars/spark-token-provider-kafka-0-10_2.12-3.4.1.jar https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.4.1/spark-token-provider-kafka-0-10_2.12-3.4.1.jar

# 5. Set SPARK_CLASSPATH for Kafka integration
ENV SPARK_CLASSPATH="/opt/airflow/jars/*"

# 6. Ensure your entrypoint is executable
RUN chmod +x /opt/airflow/script/entrypoint.sh

# 7. Expose Airflow webserver port
EXPOSE 8080

# 8. Drop back to the airflow user
USER airflow

# 9. Entrypoint and default command (same as upstream image)
ENTRYPOINT ["/opt/airflow/script/entrypoint.sh"]
CMD ["webserver"]

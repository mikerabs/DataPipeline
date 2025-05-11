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

# 4. Ensure your entrypoint is executable
RUN chmod +x /opt/airflow/script/entrypoint.sh

# 5. Drop back to the airflow user
USER airflow

# 6. Entrypoint and default command (same as upstream image)
ENTRYPOINT ["/opt/airflow/script/entrypoint.sh"]
CMD ["webserver"]


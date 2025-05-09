#!/bin/bash
#set -e
#if [ -e "/opt/airflow/requirements.txt" ]; then
  #$(command -v pip) install --user -r /opt/airflow/requirements.txt
#fi
#if [ ! -f "/opt/airflow/airflow.db" ]; then
  #airflow db init && \
  #airflow users create --username admin --firstname admin --lastname admin --role Admin --email admin@example.com --password admin
#fi
#airflow db upgrade
#exec airflow webserver

set -e

cd /opt/airflow

# Install any dependencies
if [ -f "/opt/airflow/requirements.txt" ]; then
  pip install --user -r /opt/airflow/requirements.txt
fi

# Upgrade DB
airflow db upgrade

# Pass control to the command in docker-compose (e.g., webserver or scheduler)
exec "$@"


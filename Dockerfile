FROM apache/airflow:slim-2.10.5-python3.12
USER root

# Install system dependencies required for psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    python3-dev

USER airflow

# Install psycopg2 using pip
RUN pip install psycopg2
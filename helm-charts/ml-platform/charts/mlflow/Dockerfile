# MLflow with PostgreSQL support
FROM ghcr.io/mlflow/mlflow:v2.10.0

# Switch to root to install packages
USER root

# Install PostgreSQL client library and AWS SDK for S3
RUN pip install --no-cache-dir \
    psycopg2-binary==2.9.9 \
    boto3==1.34.27

# Switch back to default user
USER 1000

EXPOSE 5000

CMD ["mlflow", "server", "--host", "0.0.0.0"]

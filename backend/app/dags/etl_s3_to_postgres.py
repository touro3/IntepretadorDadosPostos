from minio import Minio
import pandas as pd
import io
from sqlalchemy import create_engine, text, inspect
from prefect import flow, task, get_run_logger
from prefect.schedules import Cron

from app.config.properties import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET,
    POSTGRES_URI,
)

engine = create_engine(POSTGRES_URI)
inspector = inspect(engine)


@task
def extract_csv_from_minio(object_name: str) -> pd.DataFrame:
    logger = get_run_logger()
    logger.info(f"Connecting to MinIO and downloading '{object_name}'...")

    client = Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )

    response = client.get_object(MINIO_BUCKET, object_name)
    try:
        df = pd.read_csv(io.BytesIO(response.read()))
        logger.info(f"Downloaded and parsed '{object_name}' successfully.")
        return df
    finally:
        response.close()
        response.release_conn()


@task
def load_dataframe_to_postgres(df: pd.DataFrame, table_name: str):
    # logger = get_run_logger()
    print(f"Loading data into PostgreSQL table '{table_name}'...")

    engine = create_engine(POSTGRES_URI)
    df.to_sql(table_name, engine, if_exists="replace", index=False)

    print(f"Successfully loaded data into '{table_name}'.")


@task
def verify_data_loaded():
    engine = create_engine(POSTGRES_URI)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM gasprices"))
        count = result.scalar()
        print(f"✅ Rows in 'titanic' table: {count}")
        inspector = inspect(engine)
        columns = inspector.get_columns("gasprices")
        column_names = [col["name"] for col in columns]
        print(f"🧾 Columns in 'titanic' table: {column_names}")


@flow(name="Titanic ETL Flow (MinIO ➜ PostgreSQL)")
def titanic_etl_flow():
    df = extract_csv_from_minio("gas-prices.csv")
    load_dataframe_to_postgres(df, table_name="gasprices")
    verify_data_loaded()


# titanic_etl_flow.serve(
#     name="titanic-etl-deployment",
#     schedule=Cron(
#         cron="0 12 * * *", timezone="America/Sao_Paulo", slug="daily-12pm-brasilia"
#     ),
# )


if __name__ == "__main__":
    titanic_etl_flow()

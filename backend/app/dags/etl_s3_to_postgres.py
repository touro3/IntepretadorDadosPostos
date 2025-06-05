from minio import Minio
import pandas as pd
import io
from sqlalchemy import create_engine, text, inspect
from prefect import flow, task, get_run_logger
from config.properties import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET,
    POSTGRES_URI,
)

engine = create_engine(str(POSTGRES_URI))
inspector = inspect(engine)


@task
def extract_csv_from_minio(object_name: str) -> pd.DataFrame:
    logger = get_run_logger()
    logger.info(f"Connecting to MinIO and downloading '{object_name}'...")

    client = Minio(
        endpoint=str(MINIO_ENDPOINT),
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )

    response = client.get_object(str(MINIO_BUCKET), object_name)
    try:
        df = pd.read_excel(io.BytesIO(response.read()))
        logger.info(f"Downloaded and parsed '{object_name}' successfully.")
        return df
    finally:
        response.close()
        response.release_conn()


@task
def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    logger = get_run_logger()
    logger.info("Normalizing column names...")

    original_columns = df.columns.tolist()

    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(".", "", regex=False)
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )

    new_columns = df.columns.tolist()
    for old, new in zip(original_columns, new_columns):
        logger.info(f"Renamed column '{old}' → '{new}'")

    return df


@task
def clean_and_convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    logger = get_run_logger()
    logger.info("Cleaning and converting data types...")

    df_clean = df.copy()

    # Função auxiliar para converter valores monetários
    def clean_numeric_value(value):
        if pd.isna(value) or value == "":
            return None
        if isinstance(value, str):
            # Remove símbolos de moeda, espaços e vírgulas
            cleaned = value.replace("R$", "").replace(",", ".").replace(" ", "").strip()
            try:
                return float(cleaned)
            except ValueError:
                return None
        return value

    # Função auxiliar para converter datas
    def parse_date(date_str):
        if pd.isna(date_str) or date_str == "":
            return None
        try:
            # Tenta diferentes formatos de data
            if isinstance(date_str, str):
                # Remove espaços e caracteres especiais
                date_str = date_str.strip()

                # Formatos comuns brasileiros
                for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y"]:
                    try:
                        return pd.to_datetime(date_str, format=fmt).date()
                    except ValueError:
                        continue

                # Tentativa com parsing automático
                return pd.to_datetime(date_str, dayfirst=True).date()
            else:
                return pd.to_datetime(date_str).date()
        except (ValueError, TypeError, pd.errors.OutOfBoundsDatetime):
            logger.warning(f"Could not parse date: {date_str}")
            return None

    # Função auxiliar para converter tempo
    def parse_time(time_str):
        if pd.isna(time_str) or time_str == "":
            return None
        try:
            if isinstance(time_str, str):
                time_str = time_str.strip()
                # Formatos de hora: HH:MM:SS ou HH:MM
                if ":" in time_str:
                    return pd.to_datetime(time_str, format="%H:%M:%S").time()
                else:
                    return pd.to_datetime(time_str, format="%H:%M").time()
            return pd.to_datetime(time_str).time()
        except (ValueError, TypeError, pd.errors.OutOfBoundsDatetime):
            logger.warning(f"Could not parse time: {time_str}")
            return None

    # Conversões de tipos específicas
    type_conversions = {
        # Datas
        "data_abast": parse_date,
        "data_fiscal": parse_date,
        "data_movimento": parse_date,
        # Horas
        "hora_abast": parse_time,
        "hora_fiscal": parse_time,
        # Campos de texto que devem permanecer como string
        "abast_x_venda": str,
        "funcionario": str,
        "produto": str,
        # Campos numéricos inteiros
        "bico": lambda x: (
            int(float(x)) if pd.notna(x) and str(x).strip() != "" else None
        ),
        "registro": lambda x: (
            int(float(x)) if pd.notna(x) and str(x).strip() != "" else None
        ),
        "substituicao": lambda x: (
            int(float(x)) if pd.notna(x) and str(x).strip() != "" else None
        ),
        # Campos numéricos decimais
        "cupom": clean_numeric_value,
        "preco_unitario": clean_numeric_value,
        "quantidade": clean_numeric_value,
        "valor": clean_numeric_value,
        "encerrante_ini": clean_numeric_value,
        "encerrante_fim": clean_numeric_value,
        "afericao": clean_numeric_value,
        "preco_a": clean_numeric_value,
        "preco_b": clean_numeric_value,
        "preco_c": clean_numeric_value,
    }

    # Aplicar conversões
    for column, converter in type_conversions.items():
        if column in df_clean.columns:
            logger.info(f"Converting column '{column}'...")
            try:
                df_clean[column] = df_clean[column].apply(converter)
            except Exception as e:
                logger.warning(f"Error converting column '{column}': {e}")

    # Log de estatísticas após conversão
    logger.info("Data type conversion completed. Summary:")
    for col in df_clean.columns:
        non_null_count = df_clean[col].notna().sum()
        total_count = len(df_clean)
        logger.info(f"  {col}: {non_null_count}/{total_count} non-null values")

    return df_clean


@task
def load_dataframe_to_postgres(df: pd.DataFrame, table_name: str):
    logger = get_run_logger()
    logger.info(f"Loading data into PostgreSQL table '{table_name}'...")

    # Definir tipos SQL explícitos para garantir tipos corretos
    dtype_mapping = {
        "data_abast": "DATE",
        "hora_abast": "TIME",
        "data_fiscal": "DATE",
        "hora_fiscal": "TIME",
        "abast_x_venda": "VARCHAR(50)",
        "bico": "INTEGER",
        "cupom": "DECIMAL(15,2)",
        "funcionario": "VARCHAR(100)",
        "produto": "VARCHAR(100)",
        "preco_unitario": "DECIMAL(10,4)",
        "quantidade": "DECIMAL(12,3)",
        "valor": "DECIMAL(15,2)",
        "encerrante_ini": "DECIMAL(15,3)",
        "encerrante_fim": "DECIMAL(15,3)",
        "afericao": "DECIMAL(10,3)",
        "data_movimento": "DATE",
        "preco_a": "DECIMAL(10,4)",
        "preco_b": "DECIMAL(10,4)",
        "preco_c": "DECIMAL(10,4)",
        "registro": "INTEGER",
        "substituicao": "INTEGER",
    }

    # Converter DataFrame para tipos Python compatíveis com PostgreSQL
    df_for_db = df.copy()

    # Converter datas para string no formato ISO
    date_columns = ["data_abast", "data_fiscal", "data_movimento"]
    for col in date_columns:
        if col in df_for_db.columns:
            df_for_db[col] = df_for_db[col].apply(
                lambda x: x.strftime("%Y-%m-%d") if x is not None else None
            )

    # Converter horas para string
    time_columns = ["hora_abast", "hora_fiscal"]
    for col in time_columns:
        if col in df_for_db.columns:
            df_for_db[col] = df_for_db[col].apply(
                lambda x: x.strftime("%H:%M:%S") if x is not None else None
            )

    engine = create_engine(str(POSTGRES_URI))

    try:
        df_for_db.to_sql(
            table_name,
            engine,
            if_exists="replace",
            index=False,
            method="multi",
            chunksize=1000,
        )
        logger.info(f"✅ Successfully loaded data into '{table_name}'.")

        # Aplicar tipos corretos após inserção
        with engine.connect() as conn:
            for column, sql_type in dtype_mapping.items():
                if column in df_for_db.columns:
                    try:
                        alter_query = f"ALTER TABLE {table_name} ALTER COLUMN {column} TYPE {sql_type} USING {column}::{sql_type}"
                        conn.execute(text(alter_query))
                        logger.info(f"✅ Column '{column}' type set to {sql_type}")
                    except Exception as e:
                        logger.warning(
                            f"Could not alter column '{column}' to {sql_type}: {e}"
                        )
            conn.commit()

    except Exception as e:
        logger.error(f"Error loading data to PostgreSQL: {e}")
        raise


@task
def verify_data_loaded(table_name: str):
    logger = get_run_logger()
    engine = create_engine(str(POSTGRES_URI))

    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()
        logger.info(f"✅ Rows in '{table_name}' table: {count}")

        columns = inspect(engine).get_columns(table_name)
        column_names = [col["name"] for col in columns]
        logger.info(f"🧾 Columns in '{table_name}' table: {column_names}")

        # Mostrar tipos de cada coluna
        logger.info(f"📊 Column types in '{table_name}' table:")
        for col in columns:
            logger.info(f"  • {col['name']}: {col['type']}")

        # Mostrar algumas estatísticas dos dados
        logger.info(f"📈 Data sample from '{table_name}' table:")
        sample_result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 5"))
        for row in sample_result:
            # Converter row para dicionário de forma compatível
            row_dict = {col: value for col, value in zip(column_names, row)}
            logger.info(f"  {row_dict}")


@flow(name="Postos ETL Flow (MinIO ➜ PostgreSQL) - Enhanced")
def postos_etl_flow(data: str = "2025-03-24"):
    table_name = "postos"

    # Extrair dados do MinIO
    df = extract_csv_from_minio(f"{data}.xlsx")

    # Normalizar nomes das colunas
    df_normalized = normalize_column_names(df)

    # Limpar e converter tipos de dados
    df_cleaned = clean_and_convert_data_types(df_normalized)

    # Carregar no PostgreSQL com tipos corretos
    load_dataframe_to_postgres(df_cleaned, table_name=table_name)

    # Verificar os dados carregados
    verify_data_loaded(table_name=table_name)


if __name__ == "__main__":
    postos_etl_flow()

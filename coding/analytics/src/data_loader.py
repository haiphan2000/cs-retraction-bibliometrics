import glob
import os

import duckdb
import pandas as pd
from typing import Any
import yaml

from src.config import *


def init_duckdb_views() -> None:
    """Create DuckDB views from all Parquet files in MODEL_DIR."""
    parquet_files = glob.glob(
        os.path.join(MODEL_DIR, "*.parquet"),
    )

    if not parquet_files:
        print(f"No Parquet files found at: {MODEL_DIR}")
        return

    for file_path in parquet_files:
        file_name = os.path.basename(file_path)
        view_name = os.path.splitext(file_name)[0]

        duckdb.sql(
            f'CREATE OR REPLACE VIEW "{view_name}" AS '
            f"SELECT * FROM '{file_path}'"
        )

        print(f"Created or replaced view: {view_name}")

    print("Completed automatic creation of all views.")


def show_database_schema() -> None:
    """Display the schema of all DuckDB views."""
    query = """
        SELECT
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema NOT IN (
            'information_schema',
            'pg_catalog'
        )
        ORDER BY
            table_name,
            ordinal_position;
    """

    tables = {}

    for table_name, column_name, data_type in duckdb.sql(query).fetchall():
        tables.setdefault(table_name, []).append(
            (column_name, data_type)
        )

    for table_name, columns in tables.items():
        print(f"Table/View: {table_name}")

        for column_name, data_type in columns:
            print(f"  - {column_name} ({data_type})")

        print()

    print("Completed displaying database schema information.")

def execute_sql_to_df(sql_query: str) -> pd.DataFrame:
    """
    Nhận đầu vào là một chuỗi SQL string, đăng ký các bảng (nếu cần),
    thực thi bằng DuckDB và trả về pandas DataFrame sẵn sàng để display và vẽ chart.
    """          
    df_result = duckdb.sql(sql_query).df()
    
    return df_result

def load_yaml_file(file_path: Path) -> Any:
    """
    Đọc file YAML từ đối tượng Path và trả về biến dữ liệu để truy xuất.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file YAML tại: {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    return data
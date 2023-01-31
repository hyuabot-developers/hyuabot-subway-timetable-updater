import os
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

_SQLA_SESSION_CLOSER_THREADPOOL = ThreadPoolExecutor(1)


def get_db_engine() -> Engine:
    db_engine = create_engine(
        f"postgresql://{os.getenv('POSTGRES_ID')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_HOST')}:"
        f"{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}",
    )
    return db_engine


def get_master_db_engine() -> Engine:
    db_engine = create_engine(
        f"postgresql://{os.getenv('POSTGRES_ID')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_EXTERNAL_HOST')}:"
        f"{os.getenv('POSTGRES_EXTERNAL_PORT')}/{os.getenv('POSTGRES_DB')}",
    )
    return db_engine

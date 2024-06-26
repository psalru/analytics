import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

db_user, db_password = os.getenv('DB_USER'), os.getenv('DB_PASSWORD')
db_host, db_default = os.getenv('DB_HOST'), os.getenv('DB_DEFAULT')


def get_engine(host: str = db_host, db: str = db_default, echo_flag: bool = False):
    path = os.path.dirname(os.path.realpath(__file__))
    engine = create_engine(
        f'postgresql://{db_user}:{db_password}@{host}:6432/{db}',
        connect_args={
            'sslmode': 'verify-full',
            'sslrootcert': f'{path}/../ya_cloud_ca.pem'
        }, echo=echo_flag
    )

    return engine


def read_sql(sql_query: str, host: str = db_host, db: str = db_default, echo_flag: bool = False) -> pd.DataFrame:
    engine = get_engine(host, db, echo_flag)
    df = pd.read_sql(sql_query, engine).replace([None], np.NaN)
    engine.dispose()

    return df

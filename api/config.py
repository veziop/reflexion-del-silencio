import os

DIR_BASE = os.path.abspath(os.path.dirname(__file__))
RUTA_DB = os.path.join(DIR_BASE, "../data/rds-datos.db")


class Config:
    DATABASE_URI: str = RUTA_DB


config = Config()

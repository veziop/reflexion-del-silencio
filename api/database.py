import os
import sqlite3

import pandas as pd

DATABASE_NAME = os.getenv("DATABASE_NAME", "data/rds-datos.db")


def connexion_db():
    conexion = sqlite3.connect(DATABASE_NAME)
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_tablas():
    capitulo = """
        CREATE TABLE IF NOT EXISTS capitulo(
            id INTEGER PRIMARY KEY,
            titulo VARCHAR(50) NOT NULL,
            pagina_inicio INTEGER NOT NULL,
            recuento INTEGER DEFAULT 0,
            ultima_lectura DATETIME DEFAULT NULL
        )
    """
    lectura = """
        CREATE TABLE IF NOT EXISTS lectura(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATETIME NOT NULL UNIQUE,
            dia_del_año INTEGER NOT NULL,
            año INTEGER NOT NULL,
            capitulo_id INTEGER NOT NULL,
            FOREIGN KEY (capitulo_id) REFERENCES capitulo(id)
        )
    """
    tablas = [capitulo, lectura]
    db = connexion_db()
    cursor = db.cursor()
    for tabla in tablas:
        cursor.execute(tabla)

    if not tabla_tiene_registros("capitulo"):
        capitulos = pd.read_csv(
            "api/capitulo.csv", index_col=False, parse_dates=["ultima_lectura"]
        )
        capitulos.to_sql("capitulo", db, if_exists="replace", index=False)

    # lecturas = pd.read_csv("api/debug-lectura.csv", index_col=False, parse_dates=["fecha"])
    # lecturas.to_sql("lectura", db, if_exists="replace", index=False)


def tabla_tiene_registros(tabla: str) -> bool:
    comando = f"SELECT EXISTS (SELECT 1 FROM {tabla})"
    db = connexion_db()
    cursor = db.cursor()
    cursor.execute(comando)
    return next(iter(dict(cursor.fetchone()).values()))

import json
import os
import random
from datetime import datetime

import pandas as pd
from flask import Flask, Response
from pytz import timezone

from api.database import connexion_db, crear_tablas

# Configuración inicial
TIMEZONE = timezone(os.getenv("TIMEZONE", "Europe/Madrid"))

app = Flask(__name__)
crear_tablas()


@app.route("/recomendacion", methods=["GET"])
def obtener_recomendacion_diaria() -> Response:
    huso_horario = TIMEZONE
    hoy = datetime.now(huso_horario).date()

    with connexion_db() as db:
        cursor = db.cursor()
        comando = "SELECT EXISTS (SELECT 1 FROM lectura WHERE DATE(fecha) = ?)"
        cursor.execute(comando, [hoy])
        (hoy_existe,) = iter(dict(cursor.fetchone()).values())

        if hoy_existe:
            capitulo = """
                SELECT id AS numero_del_capitulo, titulo, pagina_inicio, recuento, ultima_lectura
                FROM capitulo
                WHERE numero_del_capitulo IN (
                    SELECT capitulo_id FROM lectura WHERE Date(fecha) = ?
                )
            """
            cursor.execute(capitulo, [hoy])
            fila = dict(cursor.fetchone())
            _json = json.dumps(fila, ensure_ascii=False)
            return Response(_json, content_type="application/json; charset=utf-8")

        df_capitulo = pd.read_sql("SELECT * FROM capitulo", db)
        recuento_maximo = int(df_capitulo.recuento.max())
        ponderacion = [
            (recuento_maximo - peso + 1) if peso != recuento_maximo else 0
            for peso in df_capitulo.recuento
        ]
        if not any(ponderacion):
            ponderacion = [1 for peso in df_capitulo.recuento]
        (capitulo_recomendado,) = random.choices(
            df_capitulo.id.to_list(), weights=ponderacion, k=1
        )

        lectura = {
            "fecha": hoy,
            "dia_del_año": hoy.timetuple().tm_yday,
            "año": hoy.year,
            "capitulo_id": capitulo_recomendado,
        }
        comando = (
            "INSERT INTO lectura(fecha, dia_del_año, año, capitulo_id) VALUES (?, ?, ?, ?)"
        )
        cursor.execute(comando, [*lectura.values()])
        db.commit()

        nuevo_recuento = int(
            df_capitulo.loc[df_capitulo.id == capitulo_recomendado].recuento.item() + 1
        )
        comando = "UPDATE capitulo SET recuento = ?, ultima_lectura = ? WHERE id = ?"
        cursor.execute(comando, [nuevo_recuento, hoy, capitulo_recomendado])
        db.commit()

        fila = df_capitulo.loc[df_capitulo.id == capitulo_recomendado]
        datos_respuesta = {
            "numero_del_capitulo": capitulo_recomendado,
            "titulo": fila.titulo.item(),
            "pagina_inicio": fila.pagina_inicio.item(),
            "recuento": fila.recuento.item(),
            "ultima_lectura": (
                fila.ultima_lectura.item().split(" ")[0] if fila.ultima_lectura.item() else None
            ),
        }
        _json = json.dumps(datos_respuesta, ensure_ascii=False)
        return Response(_json, content_type="application/json; charset=utf-8")


if __name__ == "__main__":
    crear_tablas()
    app.run(host="0.0.0.0", port=8080, debug=True)

from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connection

criterios_bp = Blueprint("criterios", __name__)

# Criterios base
criterios_base = {
    "RESOLUCIÓN DE PROBLEMAS": {
        "Comprensión e interpretación": {
            "1.1. Comprende el enunciado": 1,
            "1.2. Representa los datos": 1
        },
        "Resolución y comprobación": {
            "2.1. Identifica y selecciona estrategias": 1,
            "2.2. Obtiene soluciones": 1,
            "2.3. Comprueba soluciones": 1,
            "2.4. Usa estrategias de cálculo mental": 1
        }
    },
    "RAZONAMIENTO Y PRUEBA": {
        "Razonamiento": {
            "3.1. Elabora conjeturas": 1,
            "3.2. Plantea variantes de problemas": 1
        },
        "Pensamiento computacional": {
            "4.1. Aplica pensamiento computacional": 1,
            "4.2. Usa de herramientas tecnológicas": 1
        }
    },
    "CONEXIONES": {
        "Conexiones": {
            "5.1. Conecta conocimientos matemáticos": 1,
            "5.2. Conecta con la vida cotidiana/otras materias": 1
        }
    },
    "COMUNICACIÓN Y REPRESENTACIÓN": {
        "Comunicación y representación": {
            "6.1. Reconoce y usa lenguaje matemático.": 1,
            "6.2. Representa y comunica procesos matemáticos.": 1
        }
    },
    "SOCIOAFECTIVO": {
        "Destrezas Individuales": {
            "7.1. Gestiona las emociones propias ante las matemáticas.": 1,
            "7.2. Muestra actitudes positivas ante las matemáticas y ante el error.": 1
        },
        "Destrezas Grupal": {
            "8.1. Trabaja en equipo de forma respetuosa": 1,
            "8.2. Participa en las tareas asignadas en el trabajo en equipo": 1
        }
    }
}

@criterios_bp.route("/pesos", methods=["GET", "POST"])
def pesos():
    profesor_id = session.get('profesor_id')
    prof_nombre = session.get('profesor_nombre')

    if not profesor_id:
        return redirect(url_for("profesores.index"))

    cnx = get_connection()
    cursor = cnx.cursor(dictionary=True)

    # Crear tabla criterios si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS criterios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            profesor_id INT NOT NULL,
            grupo VARCHAR(100),
            subgrupo VARCHAR(100),
            nombre VARCHAR(100),
            peso DECIMAL(5,2) DEFAULT 1,
            FOREIGN KEY (profesor_id) REFERENCES profesores(id) ON DELETE CASCADE
        );
    """)

    # Insertar criterios base si no existen para este profesor
    cursor.execute("SELECT COUNT(*) AS cnt FROM criterios WHERE profesor_id=%s", (profesor_id,))
    existe = cursor.fetchone()['cnt']
    if existe == 0:
        for grupo, subgrupos in criterios_base.items():
            for subgrupo, criterios_detalle in subgrupos.items():
                for nombre, peso in criterios_detalle.items():
                    cursor.execute(
                        "INSERT INTO criterios (profesor_id, grupo, subgrupo, nombre, peso) VALUES (%s,%s,%s,%s,%s)",
                        (profesor_id, grupo, subgrupo, nombre, peso)
                    )
        cnx.commit()

    # POST: guardar cambios
    if request.method == "POST":
        for grupo, subgrupos in criterios_base.items():
            for subgrupo, criterios_detalle in subgrupos.items():
                for nombre in criterios_detalle.keys():
                    campo = f"{grupo}__{subgrupo}__{nombre}"
                    nuevo_peso = request.form.get(campo)
                    if nuevo_peso:
                        cursor.execute(
                            "UPDATE criterios SET peso=%s WHERE profesor_id=%s AND nombre=%s",
                            (float(nuevo_peso), profesor_id, nombre)
                        )
        cnx.commit()
        return redirect(url_for("profesores.evaluacion"))

    # GET: mostrar pesos actuales
    cursor.execute("SELECT grupo, subgrupo, nombre, peso FROM criterios WHERE profesor_id=%s ORDER BY id", (profesor_id,))
    filas = cursor.fetchall()
    criterios_actuales = {}
    for fila in filas:
        criterios_actuales.setdefault(fila['grupo'], {}).setdefault(fila['subgrupo'], {})[fila['nombre']] = float(fila['peso'])

    cursor.close()
    cnx.close()

    return render_template("pesos.html", criterios=criterios_actuales, prof=prof_nombre)

from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connection
import re
import mysql.connector

profesores_bp = Blueprint("profesores", __name__)

# Estructura base de criterios (solo usada si se crean pesos desde cero)
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


@profesores_bp.route("/", methods=["GET", "POST"])
def index():
    mensaje = ""
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip().lower()
        if nombre:
            nombre = re.sub(r'[^a-z0-9_]', '_', nombre)
            try:
                cnx = get_connection()
                cursor = cnx.cursor(dictionary=True)

                # Buscar si el profesor ya existe
                cursor.execute("SELECT id FROM profesores WHERE nombre=%s", (nombre,))
                prof = cursor.fetchone()

                if prof:
                    profesor_id = prof['id']
                else:
                    # Insertar nuevo profesor
                    cursor.execute("INSERT INTO profesores(nombre) VALUES(%s)", (nombre,))
                    cnx.commit()
                    profesor_id = cursor.lastrowid

                    # Crear criterios iniciales para el profesor
                    for categoria, subcategorias in criterios_base.items():
                        for sub, criterios in subcategorias.items():
                            for crit_nombre, peso in criterios.items():
                                cursor.execute(
                                    "INSERT INTO criterios (profesor_id, nombre, peso) VALUES (%s, %s, %s)",
                                    (profesor_id, crit_nombre, peso)
                                )
                    cnx.commit()

                cursor.close()
                cnx.close()

                # Guardar en sesión
                session['profesor_id'] = profesor_id
                session['profesor_nombre'] = nombre

                return redirect(url_for("profesores.evaluacion"))

            except Exception as e:
                mensaje = f"Error al conectar: {e}"
        else:
            mensaje = "Introduce un nombre válido."
    return render_template("index.html", mensaje=mensaje)


@profesores_bp.route("/evaluacion")
def evaluacion():
    profesor_id = session.get('profesor_id')
    prof_nombre = session.get('profesor_nombre')

    if not profesor_id:
        return redirect(url_for("profesores.index"))

    cnx = get_connection()
    cursor = cnx.cursor(dictionary=True)

    # Obtener criterios y pesos del profesor
    cursor.execute("SELECT nombre, peso FROM criterios WHERE profesor_id=%s ORDER BY id", (profesor_id,))
    resultados = cursor.fetchall()
    criterios = [r['nombre'] for r in resultados] if resultados else None
    pesos = [r['peso'] for r in resultados] if resultados else None

    # Obtener alumnos del profesor
    cursor.execute("SELECT nombre FROM alumnos WHERE profesor_id=%s ORDER BY id", (profesor_id,))
    alumnos = [r['nombre'] for r in cursor.fetchall()]

    # Obtener pruebas del profesor
    cursor.execute("SELECT id, nombre FROM pruebas WHERE profesor_id=%s ORDER BY id", (profesor_id,))
    pruebas = [(r['id'], r['nombre']) for r in cursor.fetchall()]

    cursor.close()
    cnx.close()

    mensaje = None
    if not criterios:
        mensaje = "No tienes pesos por criterios. ¿Deseas crearlos?"

    return render_template(
        "evaluacion.html",
        prof=prof_nombre,
        criterios=criterios,
        pesos=pesos,
        alumnos=alumnos,
        pruebas=pruebas,
        mensaje=mensaje
    )

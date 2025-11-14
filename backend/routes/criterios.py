from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connection

criterios_bp = Blueprint("criterios", __name__)

# Criterios base: solo nombres y pesos iniciales
criterios_base = {
    "1.1. Comprende el enunciado": 1,
    "1.2. Representa los datos": 1,
    "2.1. Identifica y selecciona estrategias": 1,
    "2.2. Obtiene soluciones": 1,
    "2.3. Comprueba soluciones": 1,
    "2.4. Usa estrategias de cálculo mental": 1,
    "3.1. Elabora conjeturas": 1,
    "3.2. Plantea variantes de problemas": 1,
    "4.1. Aplica pensamiento computacional": 1,
    "4.2. Usa de herramientas tecnológicas": 1,
    "5.1. Conecta conocimientos matemáticos": 1,
    "5.2. Conecta con la vida cotidiana/otras materias": 1,
    "6.1. Reconoce y usa lenguaje matemático.": 1,
    "6.2. Representa y comunica procesos matemáticos.": 1,
    "7.1. Gestiona las emociones propias ante las matemáticas.": 1,
    "7.2. Muestra actitudes positivas ante las matemáticas y ante el error.": 1,
    "8.1. Trabaja en equipo de forma respetuosa": 1,
    "8.2. Participa en las tareas asignadas en el trabajo en equipo": 1
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
            nombre VARCHAR(100),
            peso INT DEFAULT 1,
            FOREIGN KEY (profesor_id) REFERENCES profesores(id) ON DELETE CASCADE
        );
    """)

    # Insertar criterios base si no existen
    cursor.execute("SELECT COUNT(*) AS cnt FROM criterios WHERE profesor_id=%s", (profesor_id,))
    if cursor.fetchone()['cnt'] == 0:
        for nombre, peso in criterios_base.items():
            cursor.execute(
                "INSERT INTO criterios (profesor_id, nombre, peso) VALUES (%s,%s,%s)",
                (profesor_id, nombre, peso)
            )
        cnx.commit()

        # POST: guardar cambios con validación
    if request.method == "POST":
        error = None
        for nombre in criterios_base.keys():
            nuevo_peso = request.form.get(nombre)
            if not nuevo_peso:
                continue
            try:
                valor = int(nuevo_peso)
                if not (1 <= valor <= 20):
                    error = f"El peso de '{nombre}' debe estar entre 1 y 20."
                    break
            except ValueError:
                error = f"El peso de '{nombre}' debe ser un número entero."
                break

            cursor.execute(
                "UPDATE criterios SET peso=%s WHERE profesor_id=%s AND nombre=%s",
                (valor, profesor_id, nombre)
            )

        if error:
            cursor.close()
            cnx.close()

            # abrir nueva conexión para recargar datos
            cnx = get_connection()
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("SELECT nombre, peso FROM criterios WHERE profesor_id=%s ORDER BY id", (profesor_id,))
            filas = cursor.fetchall()
            lista_criterios = [(f['nombre'], int(f['peso'])) for f in filas]


            cursor.close()
            cnx.close()

            return render_template("pesos.html", lista_criterios=lista_criterios, prof=prof_nombre, error=error)

        cnx.commit()
        cursor.close()
        cnx.close()
        return redirect(url_for("profesores.evaluacion"))


    # GET: mostrar pesos actuales
    cursor.execute("SELECT nombre, peso FROM criterios WHERE profesor_id=%s ORDER BY id", (profesor_id,))
    filas = cursor.fetchall()
    lista_criterios = [(f['nombre'], int(f['peso'])) for f in filas]

    cursor.close()
    cnx.close()

    return render_template("pesos.html", lista_criterios=lista_criterios, prof=prof_nombre)

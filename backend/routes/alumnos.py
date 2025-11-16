from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connection

alumnos_bp = Blueprint("alumnos", __name__)

@alumnos_bp.route("/alumnos", methods=["GET", "POST"])
def alumnos():
    profesor_id = session.get('profesor_id')
    prof_nombre = session.get('profesor_nombre')

    if not profesor_id:
        return redirect(url_for("profesores.index"))

    cnx = get_connection()
    cursor = cnx.cursor(dictionary=True)

    # Crear tabla alumnos si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alumnos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            profesor_id INT NOT NULL,
            FOREIGN KEY (profesor_id) REFERENCES profesores(id)
        );
    """)

    if request.method == "POST":
        # Borrar alumnos existentes del profesor
        cursor.execute("DELETE FROM alumnos WHERE profesor_id=%s", (profesor_id,))

        # Insertar nuevos nombres
        for i in range(25):
            nombre = request.form.get(f"alumno{i+1}", "").strip()
            if nombre:
                cursor.execute(
                    "INSERT INTO alumnos (nombre, profesor_id) VALUES (%s, %s)",
                    (nombre, profesor_id)
                )
        cnx.commit()
        cursor.close()
        cnx.close()
        return redirect(url_for("profesores.evaluacion"))

    # GET: obtener alumnos actuales
    cursor.execute("SELECT nombre FROM alumnos WHERE profesor_id=%s ORDER BY id", (profesor_id,))
    filas = cursor.fetchall()
    cursor.close()
    cnx.close()

    alumnos_lista = [fila["nombre"] for fila in filas]

    # Si no hay alumnos, mostrar 25 por defecto
    if not alumnos_lista:
        alumnos_lista = [f"Estudiante {i+1}" for i in range(25)]

    return render_template("alumnos.html", prof=prof_nombre, alumnos=alumnos_lista)


@alumnos_bp.route('/alumnos/notas', methods=['GET'])
def ver_notas():
    alumno_seleccionado = request.args.get('alumno')
    notas = []

    if alumno_seleccionado:
        cnx = get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.nombre AS prueba, c.nombre AS criterio, n.nota
            FROM notas n
            JOIN pruebas p ON n.prueba_id = p.id
            JOIN criterios c ON n.criterio_id = c.id
            JOIN alumnos a ON n.alumno_id = a.id
            WHERE a.nombre = %s
        """, (alumno_seleccionado,))
        notas = cursor.fetchall()
        cursor.close()
        cnx.close()

    return render_template('notas_alumno.html', alumno=alumno_seleccionado, notas=notas)

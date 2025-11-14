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

    # Crear la tabla si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alumnos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            profesor_id INT NOT NULL,
            nombre VARCHAR(100),
            FOREIGN KEY (profesor_id) REFERENCES profesores(id) ON DELETE CASCADE
        );
    """)

    if request.method == "POST":
        nombres = [request.form.get(f"alumno{i+1}") for i in range(25)]
        for nombre in nombres:
            if nombre and nombre.strip():
                cursor.execute(
                    "INSERT INTO alumnos (profesor_id, nombre) VALUES (%s, %s)",
                    (profesor_id, nombre.strip())
                )
        cnx.commit()

    # Obtener alumnos actuales
    cursor.execute("SELECT id, nombre FROM alumnos WHERE profesor_id=%s ORDER BY id", (profesor_id,))
    alumnos_lista = cursor.fetchall()

    cursor.close()
    cnx.close()

    if not alumnos_lista:
        # Mostrar valores por defecto si aún no hay alumnos
        alumnos_lista = [{'id': i+1, 'nombre': f'Estudiante {i+1}'} for i in range(25)]

    return render_template("alumnos.html", prof=prof_nombre, alumnos=alumnos_lista)

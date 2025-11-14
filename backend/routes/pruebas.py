from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connection
import re
import mysql.connector

pruebas_bp = Blueprint("pruebas", __name__)


@pruebas_bp.route("/crear", methods=["GET", "POST"])
def crear_prueba():
    profesor_id = session.get('profesor_id')
    prof_nombre = session.get('profesor_nombre')

    if not profesor_id:
        return redirect(url_for("profesores.index"))

    cnx = get_connection()
    cursor = cnx.cursor(dictionary=True)

    if request.method == "POST":
        nombre = request.form.get("nombre")
        seleccionados = request.form.getlist("criterios")
        criterios_str = ",".join(seleccionados)
        cursor.execute(
            "INSERT INTO pruebas (nombre, criterios, profesor_id) VALUES (%s, %s, %s);",
            (nombre, criterios_str, profesor_id)
        )
        cnx.commit()
        cursor.close()
        cnx.close()
        return redirect(url_for("pruebas.ver_prueba", prueba_id=cursor.lastrowid))

    # Obtener criterios del profesor
    cursor.execute("SELECT id, nombre FROM criterios WHERE profesor_id=%s ORDER BY id", (profesor_id,))
    criterios = cursor.fetchall()

    cursor.close()
    cnx.close()
    return render_template("crear_prueba.html", prof=prof_nombre, criterios=criterios)

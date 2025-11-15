from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connection

pruebas_bp = Blueprint('pruebas', __name__)

@pruebas_bp.route('/crear_prueba', methods=['GET', 'POST'])
def crear_prueba():
    profesor_id = session.get('profesor_id')
    if profesor_id is None:
        return redirect(url_for('login'))  # o tu ruta de login

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form['nombre']
        criterios_ids = request.form.getlist('criterios')

        cursor.execute(
            "INSERT INTO pruebas (nombre, profesor_id) VALUES (%s, %s)",
            (nombre, profesor_id)
        )
        conn.commit()
        prueba_id = cursor.lastrowid

        # Insertar notas vacías para criterios seleccionados
        for criterio_id in criterios_ids:
            cursor.execute("""
                INSERT INTO notas (prueba_id, alumno_id, criterio_id, nota)
                SELECT %s, id, %s, NULL
                FROM alumnos
                WHERE profesor_id=%s
            """, (prueba_id, criterio_id, profesor_id))

        conn.commit()
        conn.close()
        return redirect(url_for('pruebas.ingresar_notas', prueba_id=prueba_id))

    # GET
    cursor.execute("SELECT * FROM criterios WHERE profesor_id=%s", (profesor_id,))
    criterios = cursor.fetchall()
    conn.close()
    return render_template('crear_prueba.html', criterios=criterios)



@pruebas_bp.route('/ingresar_notas/<int:prueba_id>', methods=['GET', 'POST'])
def ingresar_notas(prueba_id):
    profesor_id = session.get('profesor_id')
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        for key, value in request.form.items():
            if key.startswith('nota_') and value != '':
                _, nota_id = key.split('_')
                # Reemplazar coma por punto
                nota_valor = float(value.replace(',', '.'))
                cursor.execute("UPDATE notas SET nota=%s WHERE id=%s", (nota_valor, int(nota_id)))
                cursor.execute("UPDATE notas SET nota=%s WHERE id=%s", (float(value), int(nota_id)))
        conn.commit()
        conn.close()
        return redirect(url_for('pruebas.ver_prueba', prueba_id=prueba_id))

    # Obtener notas de los alumnos de este profesor
    cursor.execute("""
        SELECT n.id as nota_id, a.id as alumno_id, a.nombre as alumno, c.id as criterio_id, c.nombre as criterio,
               c.peso, n.nota
        FROM notas n
        JOIN alumnos a ON n.alumno_id = a.id
        JOIN criterios c ON n.criterio_id = c.id
        WHERE n.prueba_id=%s AND a.profesor_id=%s
        ORDER BY a.nombre, c.id
    """, (prueba_id, profesor_id))
    notas = cursor.fetchall()

    # Organizar por alumno
    alumnos = {}
    for n in notas:
        if n['alumno_id'] not in alumnos:
            alumnos[n['alumno_id']] = {'nombre': n['alumno'], 'notas': []}
        alumnos[n['alumno_id']]['notas'].append(n)

    conn.close()
    return render_template('ingresar_notas.html', alumnos=alumnos, prueba_id=prueba_id)
    
    
@pruebas_bp.route('/ver_prueba/<int:prueba_id>')
def ver_prueba(prueba_id):
    profesor_id = session.get('profesor_id')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Obtener la prueba (necesario para prueba.prof_id en el template)
    cursor.execute("SELECT * FROM pruebas WHERE id = %s", (prueba_id,))
    prueba = cursor.fetchone()

    # Obtener notas, alumnos y criterios
    cursor.execute("""
        SELECT n.id as nota_id, a.id as alumno_id, a.nombre as alumno,
               c.id as criterio_id, c.nombre as criterio, c.peso,
               n.nota
        FROM notas n
        JOIN alumnos a ON n.alumno_id = a.id
        JOIN criterios c ON n.criterio_id = c.id
        WHERE n.prueba_id=%s AND a.profesor_id=%s
        ORDER BY a.nombre, c.id
    """, (prueba_id, profesor_id))

    notas = cursor.fetchall()
    conn.close()

    alumnos = {}
    for n in notas:
        if n['alumno_id'] not in alumnos:
            alumnos[n['alumno_id']] = {
                'nombre': n['alumno'],
                'notas': [],
                'media': 0
            }
        alumnos[n['alumno_id']]['notas'].append(n)

    suma_medias = 0
    total_alumnos = 0

    # Cálculo de medias ponderadas
    for alumno_id, datos in alumnos.items():
        total_peso = sum(n['peso'] for n in datos['notas'])
        if total_peso == 0:
            datos['media'] = 0
        else:
            datos['media'] = round(
                sum((n['nota'] or 0) * n['peso'] for n in datos['notas']) / total_peso,
                2
            )

        suma_medias += datos['media']
        total_alumnos += 1

    media_general = round(suma_medias / total_alumnos, 2) if total_alumnos > 0 else 0

    return render_template(
        'ver_prueba.html',
        prueba=prueba,
        alumnos=alumnos,
        prueba_id=prueba_id,
        media_general=media_general
    )

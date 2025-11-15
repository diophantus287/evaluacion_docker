from db import get_connection

def init_db():
    cnx = get_connection()
    cursor = cnx.cursor()

    # Profesores
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profesores (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL
    );
    """)

    # Alumnos (relación con profesor por ID)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alumnos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        profesor_id INT NOT NULL,
        FOREIGN KEY (profesor_id) REFERENCES profesores(id)
    );
    """)

    # Criterios (relación con profesor)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS criterios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        profesor_id INT NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        peso INT NOT NULL,
        FOREIGN KEY (profesor_id) REFERENCES profesores(id)
    );
    """)

    # Pruebas (relación con profesor)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pruebas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        profesor_id INT NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        FOREIGN KEY (profesor_id) REFERENCES profesores(id)
    );
    """)

    # Evaluaciones (alumno + criterio + profesor)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        prueba_id INT NOT NULL,
        alumno_id INT NOT NULL,
        criterio_id INT NOT NULL,
        nota FLOAT NULL,
        FOREIGN KEY (prueba_id) REFERENCES pruebas(id) ON DELETE CASCADE,
        FOREIGN KEY (alumno_id) REFERENCES alumnos(id) ON DELETE CASCADE,
        FOREIGN KEY (criterio_id) REFERENCES criterios(id) ON DELETE CASCADE
    );
    """)

    cnx.commit()
    cursor.close()
    cnx.close()

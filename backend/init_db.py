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
    CREATE TABLE IF NOT EXISTS evaluaciones (
        id INT AUTO_INCREMENT PRIMARY KEY,
        alumno_id INT NOT NULL,
        criterio_id INT NOT NULL,
        nota FLOAT NOT NULL,
        profesor_id INT NOT NULL,
        FOREIGN KEY (alumno_id) REFERENCES alumnos(id),
        FOREIGN KEY (criterio_id) REFERENCES criterios(id),
        FOREIGN KEY (profesor_id) REFERENCES profesores(id)
    );
    """)

    cnx.commit()
    cursor.close()
    cnx.close()

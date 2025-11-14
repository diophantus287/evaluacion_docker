import mysql.connector
import time

def get_connection():
    for _ in range(10):
        try:
            return mysql.connector.connect(
                host="db",
                user="warein",
                password="warein",
                database="evaluacion"
            )
        except mysql.connector.Error as e:
            print("MySQL no está listo aún, reintentando...")
            time.sleep(3)

    raise Exception("No se pudo conectar a MySQL después de varios intentos")

from flask import Flask
from routes.profesores import profesores_bp
from routes.alumnos import alumnos_bp
from routes.pruebas import pruebas_bp
from routes.criterios import criterios_bp
from init_db import init_db


app = Flask(__name__)
app.secret_key = "clav3s3creta"

init_db()

app.register_blueprint(profesores_bp, url_prefix="/")
app.register_blueprint(alumnos_bp, url_prefix="/")
app.register_blueprint(criterios_bp, url_prefix="/")
app.register_blueprint(pruebas_bp, url_prefix="/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
 

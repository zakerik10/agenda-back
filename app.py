import datetime
from flask import Flask
from flask_jwt_extended import JWTManager
from config import DATABASE_CONECTION_URI, JWT_SECRET_KEY
from flask_marshmallow import Marshmallow
from routes.users import users
# from routes.books import books
# from routes.roles import roles
# from routes.permits import permits
from utils.db import db

jwt = JWTManager()
ma = Marshmallow()

def create_app(test_config=None):
    """
    Función de factoría de la aplicación Flask.
    Crea y configura la aplicación, permitiendo inyectar configuraciones
    específicas para pruebas (test_config).
    """
    app = Flask(__name__)

    # --- CONFIGURACIÓN BASE ---
    app.secret_key = "secret_key" # Mantenemos el secret_key
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # --- CONFIGURACIÓN DE SEGURIDAD (JWT) ---
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=24)
    
    
    if test_config:
        # Si se pasa una configuración de prueba, la usamos. 
        # Esto incluye la DB en memoria.
        app.config.update(test_config)
    else:
        # Si no es un entorno de prueba, usamos la DB de MySQL real.
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONECTION_URI

    # --- INICIALIZACIÓN DE EXTENSIONES ---
    # Registramos las extensiones en la instancia de la aplicación (app)
    db.init_app(app)
    jwt.init_app(app)
    ma.init_app(app) # Inicializamos Marshmallow aquí

    # --- REGISTRO DE BLUEPRINTS ---
    app.register_blueprint(users)
    # app.register_blueprint(books)
    # app.register_blueprint(roles)
    # app.register_blueprint(permits)

    return app # Retorna la aplicación configurada
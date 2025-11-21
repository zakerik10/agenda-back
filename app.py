import datetime
from flask import Flask
from flask_jwt_extended import JWTManager
from config import *
from flask_marshmallow import Marshmallow
from routes.owners import owners
from routes.clients import clients
from routes.businesses import businesses
from routes.employees import employees
from routes.services import services
from routes.services_offered import services_offered
from utils.db import db
from flask_cors import CORS #
import firebase_admin
from firebase_admin import auth, credentials

jwt = JWTManager()
ma = Marshmallow()

def create_app(test_config=None):
    """
    Función de factoría de la aplicación Flask.
    Crea y configura la aplicación, permitiendo inyectar configuraciones
    específicas para pruebas (test_config).
    """
    
    initialize_firebase()
    
    app = Flask(__name__)
    
    # Inicializar CORS
    # Permitir peticiones desde tu frontend Quasar 
    # y permitir todos los métodos y headers (incluyendo el Authorization JWT)
    url_front = f"{FRONT_URL}:{FRONT_PORT}"
    CORS(app, resources={r"/*": {"origins": url_front}})
    
    # CORS(
    #     app, 
    #     resources={r"/*": {"origins": url_front}},
    #     allow_headers=["Authorization", "Content-Type"], 
    #     supports_credentials=True # Si usas cookies/sesiones más adelante
    # )
    # Si quieres permitir cualquier origen (solo para desarrollo):
    #CORS(app, resources={r"/*": {"origins": "*"}}) 
    
    # Opción: Si lo haces en el Blueprint (menos común, pero válido):
    # from .routes.owners import owner_bp
    # CORS(owner_bp) # Puedes aplicarlo solo al blueprint de owners si quieres

    # --- CONFIGURACIÓN BASE ---
    app.secret_key = "secret_key" # Mantenemos el secret_key
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # --- CONFIGURACIÓN DE SEGURIDAD (JWT) ---
    secret_key_limpia = JWT_SECRET_KEY.strip()
    app.config["JWT_SECRET_KEY"] = secret_key_limpia
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = JWT_ACCESS_TOKEN_EXPIRES
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = JWT_REFRESH_TOKEN_EXPIRES
    
    # app.py (dentro de create_app, junto a las otras configs JWT)
    app.config["JWT_COOKIE_SECURE"] = False  # Si usas cookies
    app.config["JWT_COOKIE_SAMESITE"] = "Lax" # Si usas cookies

    # 🚨 TEMPORAL: Desactivar la protección CSRF (si aplica)
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    
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
    app.register_blueprint(owners, url_prefix='/owners')
    app.register_blueprint(clients, url_prefix='/clients')
    app.register_blueprint(businesses, url_prefix='/businesses')
    app.register_blueprint(employees, url_prefix='/employees')
    app.register_blueprint(services, url_prefix='/services')
    app.register_blueprint(services_offered, url_prefix='/services_offered')

    return app # Retorna la aplicación configurada

def initialize_firebase():
    try:
        # La ruta DEBE ser relativa a tu proyecto y el archivo debe estar seguro.
        # Ajusta la ruta a donde guardaste el archivo JSON.
        
        # Inicializa la app de Firebase
        cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
        default_app = firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK inicializado exitosamente.")
        
    except FileNotFoundError:
        print("ERROR: Archivo de credenciales de Firebase no encontrado. Asegúrate de que 'firebase-admin.json' esté en la ruta correcta.")
    except Exception as e:
        print(f"Error al inicializar Firebase: {e}")
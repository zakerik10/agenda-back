from models.users import Users
from utils.db import db
from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from serializers import *

users = Blueprint("books", __name__)

# ==============================================================================
# 3. RUTAS DE AUTENTICACIÓN (Para Dueños de Agenda)
# ==============================================================================

@users.route('/register', methods=['POST'])
def register():
    """Ruta para registrar un nuevo Dueño de Agenda."""    
    new_user_instance = user_instance(request.get_json())
    
    print(f"Averrr: {new_user_instance}")
    
    username = new_user_instance.username
    password = new_user_instance.password
    mail = new_user_instance.mail
    phone = new_user_instance.phone        

    if not username or not password:
        return jsonify({"message": "Faltan usuario o contraseña"}), 400

    if Users.query.filter_by(username=new_user_instance.username ).first():
        return jsonify({"message": "El usuario ya existe"}), 409

    new_user = Users(username=username, mail=mail, phone=phone)
    new_user.set_password(password)
    
    # db.session.add(new_user)
    # db.session.commit()
    
    return jsonify({"message": f"Usuario {username} registrado exitosamente. Ahora puede iniciar sesión."}), 201


@users.route('/login', methods=['POST'])
def login():
    """Ruta para autenticar y obtener el token JWT."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = Users.query.filter_by(username=username).first()
    
    # Verificar usuario y contraseña
    if user and user.check_password(password):
        # Crear un token de acceso JWT usando el ID del usuario como identidad
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token), 200
    
    return jsonify({"message": "Usuario o contraseña inválidos"}), 401


# ==============================================================================
# 4. RUTAS PROTEGIDAS (Solo para Dueños de Agenda)
# ==============================================================================

@users.route('/agenda_protegida', methods=['GET'])
@jwt_required() # Esta línea protege la ruta. Requiere un token JWT válido.
def agenda_admin_panel():
    """Panel de administración de la agenda. Solo accesible por Dueños de Agenda."""
    
    # Obtener la identidad del token (el user.id que usamos al crear el token)
    user_id = get_jwt_identity()
    user = Users.query.get(user_id)
    
    return jsonify({
        "message": f"Bienvenido, Dueño de Agenda: {user.username}",
        "acceso": "Protegido por JWT",
        "acciones_permitidas": "Crear, modificar, o eliminar citas en tu agenda."
    }), 200


# ==============================================================================
# 5. RUTA PÚBLICA (Para Clientes/Invitados)
# ==============================================================================

@users.route('/agendar_turno', methods=['POST'])
def agendar_turno_publico():
    """Ruta pública para que los clientes agenden un turno."""
    
    data = request.get_json()
    nombre_cliente = data.get('nombre')
    fecha_hora = data.get('fecha_hora')
    # ... Lógica para guardar el turno en la base de datos (Ej: en una tabla 'Citas')
    
    # En este punto, no necesitas autenticar al cliente, solo capturar su información
    
    return jsonify({
        "message": f"Turno agendado exitosamente para {nombre_cliente} el {fecha_hora}.",
        "acceso": "Público",
        "detalles": "El cliente no necesita iniciar sesión."
    }), 200
    
    
def user_instance(json_data):
    try:
        user_instance = user_schema.load(json_data) 
        return user_instance
        
    except ValidationError as err:
        return jsonify({"msg": "Error de validación", "errors": err.messages}), 400
    except Exception as e:
        # 3. Otros errores, como fallos de conexión a BD
        return jsonify({"msg": f"Error desconocido: {str(e)}"}), 500
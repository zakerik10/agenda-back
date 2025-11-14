from utils.db import db
from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from serializers import *
from sqlalchemy.exc import IntegrityError

owners = Blueprint("owners", __name__)

# ==============================================================================
# 3. RUTAS DE AUTENTICACIÓN (Para Dueños de Agenda)
# ==============================================================================

@owners.route('/register', methods=['POST'])
def register():
    try:
        new_user_instance = user_schema.load(request.get_json())
        
        username = new_user_instance.username
        password = new_user_instance.password
        mail = new_user_instance.mail
        phone = new_user_instance.phone
        
        new_user = Owners(username=username, mail=mail, phone=phone)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": f"Usuario {username} registrado exitosamente. Ahora puede iniciar sesión."}), 201
    
    except IntegrityError as e:
        db.session.rollback() 
        error_detail = str(e).splitlines()[0] # Solo me que quedo con la primer linea de error_detail donde puede aclarar qué columna es la que esta repetida (usuario, mail)
        print(error_detail)
        if 'username' in error_detail:
            return jsonify({"message": "El nombre de usuario ya está en uso."}), 409
        
        elif 'mail' in error_detail:
            return jsonify({"message": "El correo electrónico ya está registrado."}), 409
        
        else:
            return jsonify({"message": "Error de integridad desconocido."}), 500
        
    except ValidationError as err:
        db.session.rollback()
        return jsonify({"message": "Error de validación", "errors": err.messages}), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error desconocido: {str(e)}"}), 500


@owners.route('/login', methods=['POST'])
def login():
    """Ruta para autenticar y obtener el token JWT."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = Owners.query.filter_by(username=username).first()
    
    # Verificar usuario y contraseña
    if user and user.check_password(password):
        # Crear un token de acceso JWT usando el ID del usuario como identidad
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token), 200
    
    return jsonify({"message": "Usuario o contraseña inválidos"}), 401


# ==============================================================================
# 4. RUTAS PROTEGIDAS (Solo para Dueños de Agenda)
# ==============================================================================

@owners.route('/agenda_protegida', methods=['GET'])
@jwt_required() # Esta línea protege la ruta. Requiere un token JWT válido.
def agenda_admin_panel():
    """Panel de administración de la agenda. Solo accesible por Dueños de Agenda."""
    
    # Obtener la identidad del token (el user.id que usamos al crear el token)
    user_id = get_jwt_identity()
    user = Owners.query.get(user_id)
    
    return jsonify({
        "message": f"Bienvenido, Dueño de Agenda: {user.username}",
        "acceso": "Protegido por JWT",
        "acciones_permitidas": "Crear, modificar, o eliminar citas en tu agenda."
    }), 200


# ==============================================================================
# 5. RUTA PÚBLICA (Para Clientes/Invitados)
# ==============================================================================

@owners.route('/agendar_turno', methods=['POST'])
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
    
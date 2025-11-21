from utils.db import db
from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from serializers import *
from sqlalchemy.exc import IntegrityError
from firebase_admin import auth, exceptions
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_cors import cross_origin

owners = Blueprint("owners", __name__)

# ==============================================================================
# 3. RUTAS DE AUTENTICACIÓN (Para Dueños de Agenda)
# ==============================================================================

"""
@owners.route('/register', methods=['POST'])
def register():
    try:
        new_user_instance = owner_schema.load(request.get_json())
        
        name = new_user_instance.name
        password = new_user_instance.password
        mail = new_user_instance.mail
        phone = new_user_instance.phone
        
        new_user = Owners(name=name, mail=mail, phone=phone)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": f"Usuario {name} registrado exitosamente. Ahora puede iniciar sesión."}), 201
    
    except IntegrityError as e:
        db.session.rollback() 
        error_detail = str(e).splitlines()[0] # Solo me que quedo con la primer linea de error_detail donde puede aclarar qué columna es la que esta repetida (usuario, mail)
        
        if 'name' in error_detail:
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
    # Ruta para autenticar y obtener el token JWT.
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')
    owner = Owners.query.filter_by(name=name).first()
    
    # Verificar usuario y contraseña
    if owner and owner.check_password(password):
        # Crear un token de acceso JWT usando el ID del usuario como identidad
        access_token = create_access_token(identity=str(owner.id_owner))
        bearer_token = "Bearer " + access_token
        return jsonify(access_token=bearer_token), 200
    
    return jsonify({"message": "Usuario o contraseña inválidos"}), 401
"""

@owners.route('/auth', methods=['POST'])
def authentication():
    data = request.get_json()
    id_token = data.get('idToken')

    if not id_token:
        return jsonify({"message": "Missing idToken"}), 400

    try:
        # Verificar ID Token con Firebase Admin SDK
        decoded_token = auth.verify_id_token(id_token) 
        firebase_uid = decoded_token.get('uid')
        mail = decoded_token.get('email')
        name = decoded_token.get('name', 'Usuario') # Usa un valor por defecto si falta
        
    except exceptions.FirebaseError as e:
        # Si el token es inválido, expiró, o cualquier error de Firebase
        return jsonify({"message": f"Firebase Token validation failed: {e.code}"}), 401
    
    # Decisión de Registro vs. Login
    owner = Owners.query.filter_by(firebase_uid=firebase_uid).first()
    new_owner = None 
    if owner is None:
        # REGISTRO: Usuario nuevo, lo creamos en la base de datos SQL.
        try:
            new_owner = Owners(
                firebase_uid=firebase_uid, 
                mail=mail, 
                name=name
            )
            db.session.add(new_owner)
            db.session.commit()
            owner = new_owner
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error registering owner: {str(e)}"}), 500
    identity = str(owner.id_owner)
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    
    return jsonify({
        "access_token": access_token,
        "refresh_token" : refresh_token,
        "message": "Login successful" if new_owner != None else "Registration successful"
    }), 200
    
@owners.route('/me', methods=['GET'])
@jwt_required()
def get_owner_profile():
    current_owner_id_str = get_jwt_identity() 
    try:
        current_owner_id = int(current_owner_id_str)
    except ValueError:
        return jsonify({"msg": "ID de usuario inválido en el token"}), 400
    
    owner = Owners.query.get(current_owner_id) 
    
    if owner is None:
        return jsonify({"message": "Owner not found in database"}), 404
        
    return owner_schema.jsonify(owner), 200

@owners.route('/token/refresh', methods=['POST'])
@jwt_required(refresh=True) # Solo acepta Refresh Tokens
def refresh():
    current_owner_id = get_jwt_identity()
    
    # Crear un NUEVO Access Token (reinicia el contador de accessToken)
    new_access_token = create_access_token(identity=current_owner_id)
    # Crear un NUEVO Refresh Token (reinicia el contador de refreshToken)
    new_refresh_token = create_refresh_token(identity=current_owner_id) 
    
    return jsonify(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    ), 200

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
        "message": f"Bienvenido, Dueño de Agenda: {user.name}",
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
    
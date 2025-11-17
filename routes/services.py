from utils.db import db
from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from serializers import *
from sqlalchemy.exc import IntegrityError

services = Blueprint("services", __name__)

@services.route('/register', methods=['POST'])
@jwt_required()
def register():
    try:
        owner_id_from_token = int(get_jwt_identity())
        print(f"id owner: {owner_id_from_token}")
        new_service = service_schema.load(request.get_json())
        new_service.id_owner = owner_id_from_token
        
        print(f"Nuevo Servicio: {new_service}")
        
        db.session.add(new_service)
        db.session.commit()

        return jsonify({"message": f"Servicio {new_service.name} registrado exitosamente."}), 201
    
    except IntegrityError as e:
        db.session.rollback() 
        print(f"IntegrityError: {e}")
        error_detail = str(e).splitlines()[0] # Solo me que quedo con la primer linea de error_detail donde puede aclarar qué columna es la que esta repetida (usuario, mail)
        
        if 'mail' in error_detail:
            return jsonify({"message": "El correo electrónico ya está registrado."}), 409
        
        else:
            return jsonify({"message": "Error de integridad desconocido."}), 500
        
    except ValidationError as err:
        print(f"ValidationError: {err}")
        db.session.rollback()
        return jsonify({"message": "Error de validación", "errors": err.messages}), 400
    
    except Exception as e:
        print(f"Exception: {e}")
        db.session.rollback()
        return jsonify({"message": f"Error desconocido: {str(e)}"}), 500

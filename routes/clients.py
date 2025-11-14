from utils.db import db
from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from serializers import *
from sqlalchemy.exc import IntegrityError

clients = Blueprint("clients", __name__)

@clients.route('/register/<id_business>', methods=['POST'])
@jwt_required()
def register(id_business):
    try:
        print(f"id_business: {id_business}")
        owner_id_from_token = int(get_jwt_identity())
        business_to_check = Businesses.query.filter_by(id_business=id_business).first()
        if not business_to_check or business_to_check.id_owner != owner_id_from_token:
            return jsonify({"msg": "Acceso denegado o negocio no encontrado"}), 403 # Forbidden
        
        new_client = client_schema.load(request.get_json())
        new_client.id_business = id_business
        
        db.session.add(new_client)
        db.session.commit()

        return jsonify({"message": f"Cliente {new_client.name} {new_client.surename} registrado exitosamente."}), 201
    
    except IntegrityError as e:
        db.session.rollback() 
        error_detail = str(e).splitlines()[0] # Solo me que quedo con la primer linea de error_detail donde puede aclarar qué columna es la que esta repetida (usuario, mail)
        print(error_detail)
        
        if 'mail' in error_detail:
            return jsonify({"message": "El correo electrónico ya está registrado."}), 409
        
        else:
            return jsonify({"message": "Error de integridad desconocido."}), 500
        
    except ValidationError as err:
        db.session.rollback()
        return jsonify({"message": "Error de validación", "errors": err.messages}), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error desconocido: {str(e)}"}), 500

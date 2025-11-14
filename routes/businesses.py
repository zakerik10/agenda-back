from utils.db import db
from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from serializers import *
from sqlalchemy.exc import IntegrityError

businesses = Blueprint("businesses", __name__)

# ==============================================================================
# 3. RUTAS DE AUTENTICACIÓN (Para Dueños de Agenda)
# ==============================================================================

@businesses.route('/register', methods=['POST'])
@jwt_required()
def register():
    try:        
        new_business = business_schema.load(request.get_json())
        new_business.id_owner = int(get_jwt_identity())
        
        db.session.add(new_business)
        db.session.commit()

        return jsonify({"message": f"Negocio {new_business.name} ubicado en {new_business.address} registrado exitosamente."}), 201
    
    except IntegrityError as e:
        db.session.rollback() 
        error_detail = str(e).splitlines()[0] # Solo me que quedo con la primer linea de error_detail donde puede aclarar qué columna es la que esta repetida (usuario, mail)
        
        if 'mail' in error_detail:
            return jsonify({"message": "El correo electrónico ya está registrado."}), 409
        
        elif 'address' in error_detail:
            return jsonify({"message": "La dirección ya está registrada."}), 409
        
        else:
            return jsonify({"message": "Error de integridad desconocido."}), 500
        
    except ValidationError as err:
        db.session.rollback()
        return jsonify({"message": "Error de validación", "errors": err.messages}), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error desconocido: {str(e)}"}), 500

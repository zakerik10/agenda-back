from utils.db import db
from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from serializers import *
from sqlalchemy.exc import IntegrityError

services_offered = Blueprint("services_offered", __name__)

# ==============================================================================
# 3. RUTAS DE AUTENTICACIÓN (Para Dueños de Agenda)
# ==============================================================================

@services_offered.route('/register', methods=['POST'])
@jwt_required()
def register():
    try:        
        new_service_offered = service_offered_schema.load(request.get_json()) #id servicio e id empleado
        owner_id_from_token = int(get_jwt_identity())
        
        id_service = new_service_offered.id_service
        id_employee = new_service_offered.id_employee
        
        service_to_offer_query = Services.query.filter_by(id_service = int(id_service))
        service_to_offer = service_to_offer_query.first()
        
        if not service_to_offer or service_to_offer.id_owner != owner_id_from_token:
            return jsonify({"message": f"Acceso denegado o servicio no encontrado"}), 403
        
        employee_query = Employees.query.filter_by(id_employee = id_employee)
        employee = employee_query.first()
        id_business = employee.id_business
        
        business_to_check = Businesses.query.filter_by(id_business=id_business).first()
        if not business_to_check or business_to_check.id_owner != owner_id_from_token:
            return jsonify({"msg": "Acceso denegado o negocio no encontrado"}), 403 # Forbidden
        
        db.session.add(new_service_offered)
        db.session.commit()

        return jsonify({"message": f"Servicio {service_to_offer.name} asignado a {employee.name} {employee.surename} exitosamente."}), 201
    
    except IntegrityError as e:
        db.session.rollback() 
        error_detail = str(e).splitlines()[0] # Solo me que quedo con la primer linea de error_detail donde puede aclarar qué columna es la que esta repetida (usuario, mail)
        
        # if 'mail' in error_detail:
        #     return jsonify({"message": "El correo electrónico ya está registrado."}), 409
        
        # # elif 'address' in error_detail:
        # #     return jsonify({"message": "La dirección ya está registrada."}), 409
        
        # else:
        print(f"error_detail: {error_detail}")
        return jsonify({f"message": "Error de integridad desconocido: {error_detail}"}), 500
        
    except ValidationError as err:
        db.session.rollback()
        print(f"ValidationError: {err}")
        return jsonify({"message": "Error de validación", "errors": err.messages}), 400
    
    except Exception as e:
        print(f"Exception: {e}")
        db.session.rollback()
        return jsonify({"message": f"Error desconocido: {str(e)}"}), 500

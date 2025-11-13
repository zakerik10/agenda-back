from utils.db import db
from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from serializers import *
from sqlalchemy.exc import IntegrityError

clients = Blueprint("clients", __name__)

@clients.route('/register', methods=['POST'])
def register():
    try:
        new_client_instance = client_schema.load(request.get_json())
        
        name = new_client_instance.name
        surename = new_client_instance.surename
        mail = new_client_instance.mail
        phone = new_client_instance.phone
        
        new_user = Clients(name=name, surename=surename, mail=mail, phone=phone)
        
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": f"Cliente {name} {surename} registrado exitosamente."}), 201
    
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

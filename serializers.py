from utils.serializers import ma
from flask_marshmallow import Marshmallow
from models.owners import Owners
from models.businesses import Businesses
from models.clients import Clients
from models.employees import Employees
from models.services import Services
from utils.db import db

# ma = Marshmallow(app)

class OwnerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Owners
        load_instance = True
        sqla_session = db.session
        
user_schema = OwnerSchema()

class ClientSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Clients
        load_instance = True
        sqla_session = db.session
        
client_schema = ClientSchema()
clients_schema = ClientSchema(many=True)

class BusinessSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Businesses
        load_instance = True
        sqla_session = db.session
        
business_schema = BusinessSchema()
businesses_schema = BusinessSchema(many=True)

class EmployeeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Employees
        load_instance = True
        sqla_session = db.session
        
employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)

class ServiceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Services
        load_instance = True
        sqla_session = db.session
        
service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)
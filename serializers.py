from utils.serializers import ma
from flask_marshmallow import Marshmallow
from models.users import Users
from models.businesses import Businesses
from models.clients import Clients
# from models.books import Books
from utils.db import db

# ma = Marshmallow(app)

# class BookSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Books
#         fields = ("id", "titulo", "autor", "isbn", "stock")
#         load_instance = True
#         sqla_session = db.session

# book_schema = BookSchema()
# books_schema = BookSchema(many=True)

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Users
        load_instance = True
        sqla_session = db.session
        
user_schema = UserSchema()

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
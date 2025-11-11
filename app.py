import datetime
from flask import Flask
from flask_jwt_extended import JWTManager
from config import DATABASE_CONECTION_URI, JWT_SECRET_KEY
from routes.users import users
# from routes.books import books
# from routes.roles import roles
# from routes.permits import permits
from utils.db import db

app = Flask(__name__)

app.secret_key = "secret_key"

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONECTION_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=24)

#SQLAlchemy(app)
db.init_app(app)

jwt = JWTManager(app)

app.register_blueprint(users)
# app.register_blueprint(books)
# app.register_blueprint(roles)
# app.register_blueprint(permits)
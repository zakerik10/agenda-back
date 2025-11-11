from app import app
from utils.db import db
# from models.books import Books
from config import config

with app.app_context():
    db.create_all()

def pagina_no_encontrada(error):
    return "<h1>La pagina no existe</h1>", 404

if __name__ == "__main__":
    app.config.from_object(config["development"])
    # app.register_error_handler(404, pagina_no_encontrada)
    app.run()
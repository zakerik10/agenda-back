from app import create_app
from utils.db import db
from config import config

app = create_app()

# Configuramos la app con la configuración de desarrollo
app.config.from_object(config["development"])

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
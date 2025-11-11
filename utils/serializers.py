from flask_marshmallow import Marshmallow

# Declaramos la instancia de Marshmallow aquí.
# Esto asegura que 'ma' está disponible para todos los módulos que lo necesiten 
# (como serializers.py) sin crear una dependencia circular con app.py.
ma = Marshmallow()
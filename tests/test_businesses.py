import unittest
import json
from app import create_app
from utils.db import db
from models.businesses import Businesses
from models.owners import Owners
from flask_jwt_extended import create_access_token


class BusinessAuthTestCase(unittest.TestCase):
    """
    Pruebas unitarias para las rutas Business.
    """

    def setUp(self):
        """Configuración antes de cada prueba: usa DB en memoria."""
        
        # 1. Crear una aplicación Flask para testing (DB en memoria)
        self.app = create_app({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SECRET_KEY': 'test_secret',
            'JWT_SECRET_KEY': 'test_jwt_secret',
            'TESTING': True,
            'WTF_CSRF_ENABLED': False
        })
        
        # 2. Crear un cliente de prueba para simular peticiones
        self.business = self.app.test_client()
        
        # 3. Configurar el contexto y crear tablas
        with self.app.app_context():
            db.create_all()
            
            # 4. Crear usuario de prueba para login y rutas protegidas
            owner = Owners(username='testowner', mail='test@example.com', phone='12345678')
            owner.set_password('testpass123')
            db.session.add(owner)
            db.session.commit()
            
            business = Businesses(id_owner='1', name='testname', address="testaddress 123", mail='test@example.com', phone='12345678')
            db.session.add(business)
            db.session.commit()
            
            raw_token = create_access_token(identity=str(owner.id_owner))
            self.access_token = f'Bearer {raw_token}'
            
            self.test_business_id = business.id_business
            self.headers = {
                'Content-Type': 'application/json',
                'Authorization': self.access_token # Ya debe tener "Bearer " prefijado
            }
            
        # 5. Configurar el url base
        self.base_url = '/businesses'

    def tearDown(self):
        """Limpieza después de cada prueba: elimina la DB en memoria."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # ==========================================================================
    # PRUEBAS DE REGISTRO (/register)
    # ==========================================================================
    
    def test_registration_success(self):
        """Prueba que el registro de un nuevo usuario es exitoso (201)."""
        response = self.business.post(
            self.base_url + '/register',
            data=json.dumps({
                "name": "newname",
                "address": "newaddress 123",
                "mail": "new@email.com",
                "phone": "98765432"
            }),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("registrado exitosamente", data['message'])
        
        # Verificación de la base de datos
        with self.app.app_context():
            user = db.session.get(Businesses, 2) # El primer usuario creado es ID 1 (testuser), el nuevo es ID 2
            self.assertIsNotNone(user)
        
    def test_registration_duplicate_mail(self):
        """Prueba que el registro falla con un mail duplicado (409)."""
        response = self.business.post(
            self.base_url + '/register',
            data=json.dumps({
                "name": "newUser", 
                "address": "newaddress123",
                "mail": "test@example.com", # Ya existe de setUp()
                "phone": "12345678"
            }),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 409)
        data = response.get_json()
        self.assertIn("correo electrónico", data['message'])

    def test_registration_missing_name(self):
        """Prueba que el registro falla si falta el nombre de negocio (400 - ValidationError)."""
        response = self.business.post(
            self.base_url + '/register',
            data=json.dumps({
                "id_owner": "1",
                "address": "newaddress 123",
                "mail": "missing@email.com"
                # Falta name
            }),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Error de validación", data['message'])
        self.assertIn("name", data['errors'])
        
    def test_registration_missing_address(self):
        """Prueba que el registro falla si falta el nombre de usuario (400 - ValidationError)."""
        response = self.business.post(
            self.base_url + '/register',
            data=json.dumps({
                "id_owner": "1",
                "name": "nameclient",
                "mail": "missing@email.com"
                # Falta address
            }),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Error de validación", data['message'])
        self.assertIn("address", data['errors'])    
    
    def test_registration_missing_mail(self):
        """Prueba que el registro falla si falta el nombre de usuario (400 - ValidationError)."""
        response = self.business.post(
            self.base_url + '/register',
            data=json.dumps({
                "id_owner": "1",
                "name": "newname",
                "address": "newaddress 123"
                # Falta mail
            }),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Error de validación", data['message'])
        self.assertIn("mail", data['errors'])
        
    def test_registration_missing_token(self):
        """Prueba que no se puede registrar nuevos negocios sin el token de autorización"""
        response = self.business.post(
            self.base_url + '/register',
            data=json.dumps({
                "name": "newname",
                "address": "newaddress 123",
                "mail": "new@email.com",
                "phone": "98765432"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
    
    def test_registration_invalid_token(self):
        """Prueba que no se puede registrar nuevos negocios con el token de autorización inválido"""
        response = self.business.post(
            self.base_url + '/register',
            data=json.dumps({
                "name": "newname",
                "address": "newaddress 123",
                "mail": "new@email.com",
                "phone": "98765432"
            }),
            content_type='application/json',
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer FAKE_INVALID_TOKEN'
            }
        )
        self.assertEqual(response.status_code, 422)
    
if __name__ == '__main__':
    # Ejecuta el conjunto de pruebas
    unittest.main()
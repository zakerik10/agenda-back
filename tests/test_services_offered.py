import unittest
import json
from app import create_app
from utils.db import db
from models.owners import Owners
from models.services import Services
from models.businesses import Businesses
from models.employees import Employees
from models.services_offered import ServicesOffered
from flask_jwt_extended import create_access_token

class ServicesOfferedRegistrationTestCase(unittest.TestCase):
    """
    Pruebas unitarias para las rutas de Servicios ofrecidos.
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
        self.client = self.app.test_client()
        
        # 3. Configurar el contexto y crear tablas
        with self.app.app_context():
            db.create_all()
            
            owner = Owners(username='testowner', mail='test@example.com', phone='12345678')
            owner.set_password('testpass123')
            db.session.add(owner)
            db.session.commit()
            
            service = Services(id_owner='1', name='testservicename', description="a service", price = 10, duration = 30)
            db.session.add(service)
            db.session.commit()
            
            business = Businesses(id_owner='1', name='testname', address="testaddress 123", mail='test@example.com', phone='12345678')
            db.session.add(business)
            db.session.commit()
            
            employee = Employees(id_business='1', name='testname', surename="testsurename", mail='test@example.com', phone='12345678')
            db.session.add(employee)
            db.session.commit()
            
            owner2 = Owners(username='testowner2', mail='test2@example.com', phone='22345678')
            owner2.set_password('testpass123')
            db.session.add(owner2)
            db.session.commit()
            
            service2 = Services(id_owner='2', name='testservicename', description="a service", price = 10, duration = 30)
            db.session.add(service2)
            db.session.commit()
            
            business2 = Businesses(id_owner='2', name='testname2', address="testaddress 1233", mail='test2@example.com', phone='22345678')
            db.session.add(business2)
            db.session.commit()
            
            employee2 = Employees(id_business='2', name='testname2', surename="testsurename2", mail='test2@example.com', phone='22345678')
            db.session.add(employee2)
            db.session.commit()
            
            raw_token = create_access_token(identity=str(owner.id_owner))
            self.access_token = f'Bearer {raw_token}'
            
            self.test_service_id = service.id_service
            self.headers = {
                'Content-Type': 'application/json',
                'Authorization': self.access_token # Ya debe tener "Bearer " prefijado
            }
            
        # 5. Configurar el url base
        self.base_url = '/services_offered'

    def tearDown(self):
        """Limpieza después de cada prueba: elimina la DB en memoria."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # ==========================================================================
    # PRUEBAS DE REGISTRO (/register)
    # ==========================================================================
    
    def test_registration_success(self):
        """Prueba que el registro de un nuevo servicio es exitoso (201)."""
        response = self.client.post(
            self.base_url + '/register',
            data=json.dumps({
                "id_service": '1',
                "id_employee": '1'
            }),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("exitosamente", data['message'])
        
        # Verificación de la base de datos
        with self.app.app_context():
            client = db.session.get(Services, 2) # El primer usuario creado es ID 1 (testuser), el nuevo es ID 2
            self.assertIsNotNone(client)
                
    def test_registration_missing_token(self):
        """Prueba que no se puede registrar nuevos clientes sin el token de autorización"""
        response = self.client.post(
            self.base_url + '/register',
            data=json.dumps({
                "name": "newname",
                "surename": "newsurename",
                "mail": "new@email.com",
                "phone": "98765432"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
    
    def test_registration_invalid_token(self):
        """Prueba que no se puede registrar nuevos clientes con el token de autorización inválido"""
        response = self.client.post(
            self.base_url + '/register',
            data=json.dumps({
                "name": "newname",
                "surename": "newsurename",
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
        
    def test_registration_duplicate_assignment(self):
        response = self.client.post(
            self.base_url + '/register',
            data=json.dumps({
                "id_service": '1',
                "id_employee": '1'
            }),
            content_type='application/json',
            headers=self.headers
        )

        response_duplicate = self.client.post(
            self.base_url + '/register', 
            data=json.dumps({
                "id_service": "1",
                "id_employee": "1"
            }), 
            content_type='application/json', 
            headers=self.headers
        )
        
        self.assertEqual(response_duplicate.status_code, 409)
        self.assertIn("ya existe", response_duplicate.get_json()['message']) 
    
    def test_registration_other_service(self):
        response = self.client.post(
            self.base_url + '/register',
            data=json.dumps({
                "id_service": '2',
                "id_employee": '1'
            }),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("denegado", response.get_json()['message'])
        
    def test_registration_other_employee(self):
        response = self.client.post(
            self.base_url + '/register',
            data=json.dumps({
                "id_service": '1',
                "id_employee": '2'
            }),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("denegado", response.get_json()['message']) 
        
    
if __name__ == '__main__':
    # Ejecuta el conjunto de pruebas
    unittest.main()
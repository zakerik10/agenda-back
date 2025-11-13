import unittest
import json
from app import create_app
from utils.db import db
from models.users import Users


class UsersAuthTestCase(unittest.TestCase):
    """
    Pruebas unitarias para las rutas de autenticación y usuarios (/register, /login, /agenda_protegida).
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
            
            # 4. Crear usuario de prueba para login y rutas protegidas
            user = Users(username='testuser', mail='test@example.com', phone='12345678')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
            
            self.test_user_id = user.id
            
        # 5. Configurar el url base
        self.base_url = '/users'

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
        response = self.client.post(
            self.base_url + '/register',
            data=json.dumps({
                "username": "newuser",
                "password": "securepassword",
                "mail": "new@email.com",
                "phone": "98765432"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("registrado exitosamente", data['message'])
        
        # Verificación de la base de datos
        with self.app.app_context():
            user = db.session.get(Users, 2) # El primer usuario creado es ID 1 (testuser), el nuevo es ID 2
            self.assertIsNotNone(user)
            self.assertTrue(user.check_password('securepassword'))

    def test_registration_duplicate_username(self):
        """Prueba que el registro falla con un nombre de usuario duplicado (409)."""
        response = self.client.post(
            self.base_url + '/register',
            data=json.dumps({
                "username": "testuser", # Ya existe de setUp()
                "password": "securepassword",
                "mail": "another@email.com",
                "phone": "12345678"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409)
        data = response.get_json()
        self.assertIn("usuario", data['message'])
        
    def test_registration_duplicate_mail(self):
        """Prueba que el registro falla con un mail duplicado (409)."""
        response = self.client.post(
            self.base_url + '/register',
            data=json.dumps({
                "username": "newUser", 
                "password": "securepassword",
                "mail": "test@example.com", # Ya existe de setUp()
                "phone": "12345678"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409)
        data = response.get_json()
        self.assertIn("correo electrónico", data['message'])

    def test_registration_missing_password(self):
        """Prueba que el registro falla si falta la contraseña (400 - ValidationError)."""
        response = self.client.post(
            self.base_url + '/register',
            data=json.dumps({
                "username": "missing",
                "mail": "missing@email.com"
                # Falta password
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Error de validación", data['message'])
        self.assertIn("password", data['errors'])
        
    def test_registration_missing_username(self):
        """Prueba que el registro falla si falta el nombre de usuario (400 - ValidationError)."""
        response = self.client.post(
            self.base_url + '/register',
            data=json.dumps({
                "password": "superpassword",
                "mail": "missing@email.com"
                # Falta username
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Error de validación", data['message'])
        self.assertIn("username", data['errors'])
        
    def test_registration_missing_mail(self):
        """Prueba que el registro falla si falta el nombre de usuario (400 - ValidationError)."""
        response = self.client.post(
            self.base_url + '/register',
            data=json.dumps({
                "username": "newUser",
                "password": "superpassword"
                # Falta mail
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Error de validación", data['message'])
        self.assertIn("mail", data['errors'])
        
    # ==========================================================================
    # PRUEBAS DE INICIO DE SESIÓN (/login)
    # ==========================================================================

    def get_auth_token(self, username="testuser", password="testpass123"):
        """Helper para obtener un token de acceso válido."""
        response = self.client.post(
            self.base_url + '/login',
            data=json.dumps({"username": username, "password": password}),
            content_type='application/json'
        )
        return response.get_json().get("access_token")

    def test_login_success(self):
        """Prueba que el inicio de sesión es exitoso y devuelve un token (200)."""
        token = self.get_auth_token()
        self.assertIsInstance(token, str)

    def test_login_wrong_password(self):
        """Prueba que el inicio de sesión falla con contraseña incorrecta (401)."""
        response = self.client.post(
            self.base_url + '/login',
            data=json.dumps({
                "username": "testuser",
                "password": "wrongpassword"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        
    # ==========================================================================
    # PRUEBAS DE RUTA PROTEGIDA (/agenda_protegida)
    # ==========================================================================

    def test_protected_route_success(self):
        """Prueba que la ruta protegida es accesible con un token válido (200)."""
        token = self.get_auth_token()
        response = self.client.get(
            self.base_url + '/agenda_protegida',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("Bienvenido, Dueño de Agenda", data['message'])
        self.assertIn("testuser", data['message']) # Verifica que el usuario sea correcto

    def test_protected_route_missing_token(self):
        """Prueba que la ruta protegida falla sin token (401)."""
        response = self.client.get(self.base_url + '/agenda_protegida')
        self.assertEqual(response.status_code, 401)
        
    def test_protected_route_invalid_token(self):
        """Prueba que la ruta protegida falla con un token inválido (401/422)."""
        response = self.client.get(
            self.base_url + '/agenda_protegida',
            headers={'Authorization': 'Bearer FAKE_INVALID_TOKEN'}
        )
        # 422 si el formato del token es inválido, 401 si la firma es incorrecta
        self.assertIn(response.status_code, [401, 422])

    # ==========================================================================
    # PRUEBAS DE RUTA PÚBLICA (/agendar_turno)
    # ==========================================================================

    def test_public_route_success(self):
        """Prueba que la ruta pública funciona sin autenticación (200)."""
        response = self.client.post(
            self.base_url + '/agendar_turno',
            data=json.dumps({
                "nombre": "Juan Pérez",
                "fecha_hora": "2025-11-20T10:00:00"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("Turno agendado exitosamente", data['message'])


if __name__ == '__main__':
    # Ejecuta el conjunto de pruebas
    unittest.main()
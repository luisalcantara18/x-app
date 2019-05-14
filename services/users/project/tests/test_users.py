# services/users/project/tests/test_users.py


import json
import unittest

from project.tests.base import BaseTestCase
from project import db
from project.api.models import User


def add_user(username, email):
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return user


class TestUserService(BaseTestCase):
    """Tests para el servicio Users."""

    def test_users(self):
        """Asegurando que la ruta /ping  se comporta correctamente."""
        response = self.client.get('/users/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        """Asegurar que un nuevo usuario puede
        ser agregado a la base de datos"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'Luis Alcantara ',
                    'email': 'luisalcantara@upeu.edu.pe'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('luisalcantara@upeu.edu.pe', data['message'])
            self.assertIn('success', data['status'])

    def test_add_user_invalid_json(self):
        """Asegurando de que se arroje un error si el objeto json esta
        vacio."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        """Asegurando de que se produce un error si el objeto
        JSON no tiene  una clave username
        """
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({'email': 'luisalcantara@upeu.edu.pe'}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_duplicate_email(self):
        """Asegurando de que se produce un error si el email existe."""
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'Luis Alcantara',
                    'email': 'luisalcantara@upeu.edu.pe'
                }),
                content_type='application/json',
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'Luis Alcantara',
                    'email': 'luisalcantara@upeu.edu.pe'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Disculpe. Este email ya existe.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user(self):
        """Asegurando de que se obtenga un user de forma correcta."""
        user = add_user('Luis Alcantara', 'luisalcantara@upeu.edu.pe')
        with self.client:
            response = self.client.get(f'/users/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('Luis Alcantara', data['data']['username'])
            self.assertIn('luisalcantara@upeu.edu.pe', data['data']['email'])
            self.assertIn('success', data['status'])

    def test_single_user_no_id(self):
        """asegurese de que se arroge un  error
        si no se proporciona una identificacione"""
        with self.client:
            response = self.client.get('/users/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('user not exists', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_incorrect_id(self):
        """asegurando de que se arroje un error
        si la identificacion no existe"""
        with self.client:
            response = self.client.get('/users/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('user not exists', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_users(self):
        """asegurando de que todos los usuarios se
        comporten correctamente"""
        add_user('Luis Alcantara', 'luisalcantara@upeu.edu.pe')
        add_user('david', 'david@upeu.edu.pe')
        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['users']), 2)
            self.assertIn(
                'Luis Alcantara', data['data']['users'][0]['username'])
            self.assertIn(
                'luisalcantara@upeu.edu.pe', data['data']['users'][0]['email'])
            self.assertIn(
                'david', data['data']['users'][1]['username'])
            self.assertIn(
                'david@upeu.edu.pe', data['data']['users'][1]['email'])
            self.assertIn('success', data['status'])

    def test_main_no_users(self):
        """Asegurando que la ruta principal
        funciones correctamente cuando no
        no hay usuarios añadidos a la base de datos"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Todos los usuarios', response.data)
        self.assertIn(b'<p>No hay usuarios!</p>', response.data)

    def test_main_with_users(self):
        """Asegurando que la ruta principal funcione correctamente
        cuando un ususario es correctamente agregado a la base de datos"""
        add_user('luis', 'luisalcantara@upeu.edu.pe')
        add_user('david', 'david@gmail.com')
        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Todos los usuarios', response.data)
            self.assertNotIn(b'<p>No hay usuario</p>', response.data)
            self.assertIn(b'luis', response.data)
            self.assertIn(b'david', response.data)

    def test_main_add_user(self):
        """Asegurando que un nuevo ususario
        pueda ser agregado a
        la db mediante un request"""
        with self.client:
            response = self.client.post(
                '/',
                data=dict(
                    username='luis',
                    email='luisalcantara@upeu.edu.pe',
                ),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Todos los usuarios', response.data)
            self.assertNotIn(b'<p>No hay usuarios!</p>', response.data)
            self.assertIn(b'luis', response.data)


if __name__ == '__main__':
    unittest.main()

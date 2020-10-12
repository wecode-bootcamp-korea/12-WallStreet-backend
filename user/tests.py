import json
import bcrypt
import jwt

from django.test import TestCase, Client
from .models     import User

class SignUpTest(TestCase):
    def setUp(self):
        User.objects.create(
            email    = 'test@mail.com',
            password = '123456789aA!',
        )
    
    def tearDown(self):
        User.objects.all().delete()

    def test_signup_post_success(self):
        client = Client()

        user = {
            'email'    : 'test1@mail.com',
            'password' : '123456789aA!'
        }

        response = client.post('/account/signup',json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'message':'SUCCESS'})
    
    def test_signup_post_key_error(self):
        client = Client()

        user = {
                'email'       : 'test@mail.com',
                'passwordd'   : '123456789aA!',
                }
        response = client.post('/account/signup', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message':'KEY_ERROR'})

    def test_signup_post_duplicated_email(self):
        client = Client()

        user = {
                'email'       : 'test@mail.com',
                'password'    : '123456789aA!',
                }
        response = client.post('/account/signup', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message':'DUPLICATED_REGISTER'})
    
    def test_signup_post_invalid_info(self):
        client = Client()

        user = {
                'email'       : 'testmail.com',
                'password'    : '12345678aaA!',
                }
        response = client.post('/account/signup', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message':'INVALID_INFOS'})

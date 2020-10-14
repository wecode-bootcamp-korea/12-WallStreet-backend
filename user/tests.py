import json
import bcrypt
import jwt

from django.test    import TestCase, Client
from unittest.mock  import patch, MagicMock

from wallstreet.settings    import SECRET_KEY, ALGORITHM
from .models                import User

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

class SosialSignInTest(TestCase):
    def setUp(self):
        User.objects.create(
            name          = '테스트일',
            password      = 'test_password',
            email         = '테스트일12345',
           )

    def tearDown(self):
        User.objects.all().delete()
     
    @patch("user.views.requests")
    def test_social_signup_success(self, mocked_requests):
        client = Client()
        class MockedResponseTwo:
            def json(self):
                return {"id" : "98765", 
                        'kakao_account': {  "profile" : {"nickname" : "테스트이"},   }
                        }

        mocked_requests.get = MagicMock(return_value = MockedResponseTwo())
        response = client.post("/user/socialsignin", **{"Authorization":"1234","content_type" : "application/json"})

        accessed_user = User.objects.get(email='테스트이98765')
        access_token = jwt.encode({'user_id': accessed_user.id}, SECRET_KEY, ALGORITHM)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'Authorization': access_token.decode('utf-8')})

    @patch("user.views.requests")
    def test_social_signin_success(self, mocked_requests):
        client = Client()
        class MockedResponseOne:
            def json(self):
                return {"id" : "12345", 
                        'kakao_account': {  "profile" : {"nickname" : "테스트일"},   }
                        }

        mocked_requests.get = MagicMock(return_value = MockedResponseOne())
        response = client.post("/user/socialsignin", **{"Authorization":"1234","content_type" : "application/json"})

        accessed_user = User.objects.get(email='테스트일12345')
        access_token = jwt.encode({'user_id': accessed_user.id}, SECRET_KEY, ALGORITHM)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'Authorization': access_token.decode('utf-8')})
        
    @patch("user.views.requests")
    def test_social_signup_invalid_user_from_kakao(self, mocked_requests):
        client = Client()
        class MockedResponseOne:
            def json(self):
                return {'msg':'INVALID_TOKEN'}

        mocked_requests.get = MagicMock(return_value = MockedResponseOne())

        response = client.post("/user/socialsignin", **{"Authorization":"1234","content_type" : "application/json"})

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'message': 'KEY_ERROR'})
        
    @patch("user.views.requests")
    def test_social_signup_no_key_from_front_key_error(self, mocked_requests):
        client = Client()
        class MockedResponseOne:
            def json(self):
                return {'msg':'KEY_ERROR'}
 
        mocked_requests.get = MagicMock(return_value = MockedResponseOne())
 
        response = client.post("/user/socialsignin", **{"authooooo":"1234","content_type" : "application/json"})
 
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'message': 'KEY_ERROR'})

class SignInTest(TestCase):
    def setUp(self):
        client = Client()
        User.objects.create(
            name        = 'Corine',
            email       = 'Corine@wecode.com',
            password    = bcrypt.hashpw("test_password".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            nickname    = 'nicknick'
        )

    def tearDown(self):
        User.objects.get(email='Corine@wecode.com').delete()

    def test_signin_view_sucess(self):
        account = {
            'email'     : 'Corine@wecode.com',
            'password'  : "test_password",
        }

        accessed_user   = User.objects.get(email=account['email'])
        access_token    = jwt.encode({'user_id': accessed_user.id}, SECRET_KEY, ALGORITHM).decode('utf-8')
        response = self.client.post('/user/signin', json.dumps(account), content_type='application/json')

        self.assertEqual(response.json(), {'Authorization': access_token})
        self.assertEqual(response.status_code, 200)

    def test_signin_view_wrong_password(self):
        account = {
            'email'     : 'Corine@wecode.com',
            'password'  : 'wrong_password',
        }

        response = self.client.post('/user/signin', json.dumps(account), content_type='application/json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'message':'INVALID_USER'})

    def test_signin_view_wrong_email(self):
        account = {
            'email'     : 'wrong@wecode.com',
            'password'  : 'test_password',
        }

        response = self.client.post('/user/signin', json.dumps(account), content_type='application/json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'message':'INVALID_USER'})

    def test_signin_view_email_key_error(self):
        account = {'email':'Corine@wecode.com'}

        response = self.client.post('/user/signin', json.dumps(account), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message':'KEY_ERROR'})

    def test_signin_view_email_password_error(self):
        account = {'password'  : 'test_password'}

        response = self.client.post('/user/signin', json.dumps(account), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message':'KEY_ERROR'})
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse


class SessionApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('member', password='safe-password')

    def test_session_is_anonymous_until_login(self):
        response = self.client.get(reverse('accounts:session'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()['user'])
        self.assertTrue(response.json()['csrf_token'])
        self.assertIn('csrftoken', response.cookies)

    def test_credentialed_cross_origin_login_uses_csrf_token_handoff(self):
        origin = 'https://frontend.example.test'
        client = Client(enforce_csrf_checks=True)

        with override_settings(
            CORS_ALLOWED_ORIGINS=[origin],
            CORS_ALLOW_CREDENTIALS=True,
            CSRF_TRUSTED_ORIGINS=[origin],
        ):
            preflight_response = client.options(
                reverse('accounts:login'),
                HTTP_ORIGIN=origin,
                HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
                HTTP_ACCESS_CONTROL_REQUEST_HEADERS='content-type,x-csrftoken',
            )
            self.assertEqual(preflight_response.status_code, 200)
            self.assertEqual(
                preflight_response['Access-Control-Allow-Origin'],
                origin,
            )
            self.assertEqual(
                preflight_response['Access-Control-Allow-Credentials'],
                'true',
            )
            self.assertIn(
                'x-csrftoken',
                preflight_response['Access-Control-Allow-Headers'].lower(),
            )

            session_response = client.get(
                reverse('accounts:session'),
                HTTP_ORIGIN=origin,
            )
            self.assertEqual(
                session_response['Access-Control-Allow-Origin'],
                origin,
            )
            self.assertEqual(
                session_response['Access-Control-Allow-Credentials'],
                'true',
            )
            csrf_token = session_response.json()['csrf_token']

            rejected_response = client.post(
                reverse('accounts:login'),
                {'username': 'member', 'password': 'safe-password'},
                HTTP_ORIGIN=origin,
            )
            self.assertEqual(rejected_response.status_code, 403)

            login_response = client.post(
                reverse('accounts:login'),
                {'username': 'member', 'password': 'safe-password'},
                HTTP_ORIGIN=origin,
                HTTP_X_CSRFTOKEN=csrf_token,
            )
            self.assertEqual(login_response.status_code, 200)
            self.assertTrue(login_response.json()['csrf_token'])
            self.assertEqual(
                login_response['Access-Control-Allow-Credentials'],
                'true',
            )

            session_response = client.get(
                reverse('accounts:session'),
                HTTP_ORIGIN=origin,
            )
            self.assertEqual(
                session_response.json()['user']['username'],
                'member',
            )

            logout_response = client.post(
                reverse('accounts:logout'),
                HTTP_ORIGIN=origin,
                HTTP_X_CSRFTOKEN=login_response.json()['csrf_token'],
            )
            self.assertEqual(logout_response.status_code, 204)

    def test_login_session_and_logout(self):
        response = self.client.post(reverse('accounts:login'), {'username': 'member', 'password': 'safe-password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user']['username'], 'member')
        self.assertFalse(response.json()['user']['is_admin'])
        self.assertEqual(self.client.post(reverse('accounts:logout')).status_code, 204)

    def test_invalid_login_is_rejected(self):
        response = self.client.post(reverse('accounts:login'), {'username': 'member', 'password': 'wrong'})
        self.assertEqual(response.status_code, 400)

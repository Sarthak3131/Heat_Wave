from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class SessionApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('member', password='safe-password')

    def test_session_is_anonymous_until_login(self):
        response = self.client.get(reverse('accounts:session'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()['user'])

    def test_login_session_and_logout(self):
        response = self.client.post(reverse('accounts:login'), {'username': 'member', 'password': 'safe-password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user']['username'], 'member')
        self.assertFalse(response.json()['user']['is_admin'])
        self.assertEqual(self.client.post(reverse('accounts:logout')).status_code, 204)

    def test_invalid_login_is_rejected(self):
        response = self.client.post(reverse('accounts:login'), {'username': 'member', 'password': 'wrong'})
        self.assertEqual(response.status_code, 400)

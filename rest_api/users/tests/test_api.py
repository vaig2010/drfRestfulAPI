from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import Arcticle, ReferralCode
from users.serializers import ArcticleSerializer, UserLoginSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone
User = get_user_model()

class UserRegistrationAPITestCase(APITestCase):

    def setUp(self):
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123'
        }
        self.existing_user = User.objects.create_user(
            username='existinguser',
            email='existinguser@example.com',
            password='password123'
        )
        self.url = reverse('register')

    def test_valid_data_creates_user(self):
        response = self.client.post(self.url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.valid_user_data.get('email'), self.valid_user_data['email'])
        self.assertEqual(self.valid_user_data.get('username'), self.valid_user_data['username'])
        self.assertEqual(self.valid_user_data.get('password'), self.valid_user_data['password'])

    def test_email_already_exists(self):
        invalid_user_data = {
            'username': 'newuser',
            'email': 'existinguser@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.url, invalid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'][0], 'A user with that email already exists.')

    def test_password_not_returned_in_response(self):
        response = self.client.post(self.url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.data)

    def test_username_already_exists(self):
        invalid_user_data = {
            'username': 'existinguser',
            'email': 'newuser@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.url, invalid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertEqual(response.data['username'][0], 'A user with that username already exists.')

class UserLoginSerializerTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )

    def test_valid_login(self):
        data = {
            'username': 'testuser',
            'password': 'password123'
        }
        serializer = UserLoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.validated_data
        self.assertEqual(user, self.user)

    def test_invalid_login(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        serializer = UserLoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertEqual(serializer.errors['non_field_errors'][0], 'Invalid Credentials')

    def test_missing_username(self):
        data = {
            'password': 'password123'
        }
        serializer = UserLoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        self.assertEqual(serializer.errors['username'][0], 'This field is required.')

    def test_missing_password(self):
        data = {
            'username': 'testuser'
        }
        serializer = UserLoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
        self.assertEqual(serializer.errors['password'][0], 'This field is required.')


class ReferralCodeSerializerTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )
        self.url = reverse('referral_codes-list')

    def test_user_without_referral_code_can_create(self):
        self.client.force_authenticate(user=self.user)
        data = {'code': 'existing_code'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReferralCode.objects.filter(user=self.user).count(), 1)
        self.assertIn('code', response.data)  # Ensure the code is in the response
        self.assertIn('expiration_date', response.data)  # Ensure the expiration date is in the response

    def test_user_with_existing_referral_code_cannot_create(self):
        expiration_date = timezone.now() + timezone.timedelta(days=30)
        ReferralCode.objects.create(user=self.user, code='existing_code', expiration_date=expiration_date)
        self.client.force_authenticate(user=self.user)
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(response.data['non_field_errors'][0], 'User already has a ReferralCode')

class ArcticlesApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )
        self.client.force_authenticate(user=self.user)
    def test_get(self):
        arcticle1 = Arcticle.objects.create(
            title='Arcticle 1',
            content='Content 1',
        )
        arcticle2 = Arcticle.objects.create(
            title='Arcticle 2',
            content='Content 2',
        )
        url = reverse('arcticle-list')
        response = self.client.get(url)
        serialized_data = ArcticleSerializer([arcticle1, arcticle2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data["results"], serialized_data)
        
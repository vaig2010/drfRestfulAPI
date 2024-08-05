from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import Arcticle
from users.serializers import ArcticleSerializer, UserRegistrationSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationSerializerTest(TestCase):

    def setUp(self):
        self.valid_user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123",
        }
        self.existing_user = User.objects.create_user(
            username="existinguser",
            email="existinguser@example.com",
            password="password123",
        )

    def test_valid_data_creates_user(self):
        serializer = UserRegistrationSerializer(data=self.valid_user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, self.valid_user_data["username"])
        self.assertEqual(user.email, self.valid_user_data["email"])
        self.assertTrue(user.check_password(self.valid_user_data["password"]))

    def test_email_already_exists(self):
        invalid_user_data = {
            "username": "newuser",
            "email": "existinguser@example.com",
            "password": "password123",
        }
        serializer = UserRegistrationSerializer(data=invalid_user_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertEqual(
            serializer.errors["email"][0], "A user with that email already exists."
        )

    def test_password_not_returned_in_response(self):
        serializer = UserRegistrationSerializer(data=self.valid_user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertNotIn("password", serializer.data)

    def test_username_already_exists(self):
        invalid_user_data = {
            "username": "existinguser",
            "email": "newuser@example.com",
            "password": "password123",
        }
        serializer = UserRegistrationSerializer(data=invalid_user_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)
        self.assertEqual(
            serializer.errors["username"][0],
            "A user with that username already exists.",
        )


class ArcticleSerializerTestCase(APITestCase):
    def test_ok(self):
        arcticle1 = Arcticle.objects.create(title="Arcticle 1", content="Content 1")
        arcticle2 = Arcticle.objects.create(title="Arcticle 2", content="Content 2")
        data = ArcticleSerializer([arcticle1, arcticle2], many=True).data
        expected_data = [
            {
                "id": arcticle1.id,
                "title": "Arcticle 1",
                "content": "Content 1",
            },
            {
                "id": arcticle2.id,
                "title": "Arcticle 2",
                "content": "Content 2",
            },
        ]
        self.assertEqual(expected_data, data)

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from users.models import ReferralCode

User = get_user_model()


class ReferralCodeViewSetTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="password123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="otheruser@example.com", password="password123"
        )
        self.url_list = reverse("referral_codes-list")
        self.client.force_authenticate(user=self.user)

    def test_list_referral_codes(self):
        expiration_date = timezone.now() + timezone.timedelta(days=30)
        ReferralCode.objects.create(
            user=self.user, code="test_code", expiration_date=expiration_date
        )
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 1)
        self.assertEqual(response.data["results"][0].get("code"), "test_code")

    def test_create_referral_code(self):
        response = self.client.post(self.url_list, {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReferralCode.objects.filter(user=self.user).count(), 1)

    def test_user_cannot_create_multiple_referral_codes(self):
        expiration_date = timezone.now() + timezone.timedelta(days=30)
        ReferralCode.objects.create(
            user=self.user, code="existing_code", expiration_date=expiration_date
        )
        response = self.client.post(self.url_list, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(
            response.data["non_field_errors"][0], "User already has a ReferralCode"
        )

    def test_delete_own_referral_code(self):
        expiration_date = timezone.now() + timezone.timedelta(days=30)
        referral_code = ReferralCode.objects.create(
            user=self.user, code="test_code", expiration_date=expiration_date
        )
        url_detail = reverse("referral_codes-detail", args=[referral_code.id])
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ReferralCode.objects.filter(user=self.user).count(), 0)

    def test_delete_other_user_referral_code(self):
        # He can't get access to page of the other user bc of auth
        expiration_date = timezone.now() + timezone.timedelta(days=30)
        referral_code = ReferralCode.objects.create(
            user=self.other_user, code="test_code", expiration_date=expiration_date
        )
        url_detail = reverse("referral_codes-detail", args=[referral_code.id])
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GetReferralCodeByEmailViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="password123"
        )
        self.url = reverse("get_referral_by_email")
        self.client.force_authenticate(user=self.user)

    def test_get_referral_code_by_email(self):
        expiration_date = timezone.now() + timezone.timedelta(days=30)
        ReferralCode.objects.create(
            user=self.user, code="test_code", expiration_date=expiration_date
        )
        data = {"email": "testuser@example.com"}
        response = self.client.get(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("code"), "test_code")

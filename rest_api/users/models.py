from django.db import models


class Arcticle(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.title
    
    # models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ReferralCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=20, unique=True)
    expiration_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        return self.expiration_date > timezone.now()

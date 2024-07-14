from django.contrib import admin

# Register your models here.
from .models import Arcticle, Referral, ReferralCode

admin.site.register(Arcticle)
admin.site.register(Referral)
admin.site.register(ReferralCode)

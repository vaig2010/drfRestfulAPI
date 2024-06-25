from django.contrib import admin

# Register your models here.
from .models import CustomUser, Arcticle

admin.site.register(CustomUser)
admin.site.register(Arcticle)

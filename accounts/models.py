from django.contrib.auth.models import AbstractUser
from django.db import models


class NativeLanguage(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    date_of_birth = models.DateField(default='1900-01-01')
    affiliation = models.CharField(max_length=255, blank=True,)
    native_languages = models.ManyToManyField(NativeLanguage)

    def __str__(self):
        return self.username

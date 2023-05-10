from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    role = models.CharField('Роль', max_length=10, blank=True)
    bio = models.TextField('Биография', blank=True)
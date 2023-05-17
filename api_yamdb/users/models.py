from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        'E-mail', max_length=254, unique=True, blank=True)
    role = models.CharField('Роль', max_length=10, blank=True)
    bio = models.TextField('Биография', blank=True)
    confirmation_code = models.CharField(
        'Код подтверждения', max_length=10, blank=True)

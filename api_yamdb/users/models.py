from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    MODERATOR = 'moderator'
    USER = 'user'
    ADMIN = 'admin'

    CHOICES_ROLE = (
        (USER, USER),
        (MODERATOR, MODERATOR),
        (ADMIN, ADMIN),
    )
    email = models.EmailField(
        'E-mail', max_length=254,
        unique=True,
        blank=True)
    role = models.CharField(
        'Роль',
        default=USER,
        choices=CHOICES_ROLE,
        max_length=10,
        blank=True)
    bio = models.TextField(
        'Биография',
        blank=True)
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=10,
        blank=True)

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    class Meta:
        ordering = ('id',)

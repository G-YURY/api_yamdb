from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models

from .validators import validate_username_not_me


class User(AbstractUser):
    MODERATOR = 'moderator'
    USER = 'user'
    ADMIN = 'admin'

    CHOICES_ROLE = (
        (USER, USER),
        (MODERATOR, MODERATOR),
        (ADMIN, ADMIN),
    )
    username = models.CharField(
        'Имя пользователя',
        validators=[
            validate_username_not_me,
            UnicodeUsernameValidator()
        ],
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        'E-mail',
        unique=True,
        validators=[MinLengthValidator(1), MaxLengthValidator(254)],
        blank=False,
        null=False
    )
    role = models.CharField(
        'Роль',
        default=USER,
        choices=CHOICES_ROLE,
        max_length=100,
        blank=True
    )
    bio = models.TextField(
        'Биография',
        blank=True
    )

    @property
    def is_admin_role(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator_role(self):
        return self.role == self.MODERATOR or self.is_superuser

    @property
    def is_user_role(self):
        return self.role == self.USER or self.is_superuser

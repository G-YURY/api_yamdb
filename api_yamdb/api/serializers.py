from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import AccessToken

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    # password = serializers.HiddenField(default='system')
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email',
            'first_name', 'last_name',
            'bio', 'role',
        )


class UserRegistrationSerializer(serializers.ModelSerializer):
    """ Сериализация регистрации пользователя и создания нового. """
    password = serializers.HiddenField(default='system', required=False)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('email', 'username', 'password',)


class TokenSerializer(serializers.Serializer):
    token = serializers.SerializerMethodField()

    def create(self, validated_data):
        _username = self.initial_data['username']
        try:
            _user = User.objects.get(username=_username)
        except ObjectDoesNotExist:
            _user = None

        if not _user:
            message = {f'{_username}': 'Пользователь не найден.'}
            raise NotFound(message)

        _code = self.initial_data['confirmation_code']
        if not _user.code == _code:
            message = {'confirmation_code': f'{_code} — код не корректен.'}
            raise ValidationError(message)
        _user.code = None
        _token = AccessToken().for_user(_user)
        return _token

    def get_token(self, obj):
        return str(self.instance)

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator(),
                    UniqueValidator(queryset=User.objects.all())])
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())])
    # )    username = serializers.CharField(
    #     max_length=150,
    #     required=True,
    #     validators=[UnicodeUsernameValidator(), ]
    # )
    # email = serializers.EmailField(
    #     max_length=254,
    #     required=True,
    # )

    class Meta:
        model = User
        fields = (
            'username', 'email',
            'first_name', 'last_name',
            'bio', 'role',
        )


class UserNotAdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[UnicodeUsernameValidator(), ]
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=254,
        required=True,
    )
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[UnicodeUsernameValidator(), ]
    )

    def validate_username(self, value):
        """ Проверить значение поля <username>.
        """
        if value == 'me':
            raise serializers.ValidationError(
                'Значение поля не может быть `me`.'
            )
        return value

    def validate(self, attrs):
        """ Проверяем, существует ли пользователь с данным адресом электронной
            почты или именем пользователя
        """
        email, username = attrs.get('email', None), attrs.get('username', None)
        if email is None or username is None:
            raise ValidationError(
                'Нужно указать адрес электронной почты и имя пользователя.'
            )
        return attrs


class TokenSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(required=True)
    username = serializers.CharField(required=True)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all())

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')

    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        """Получение среднего рейтинга."""
        if obj.reviews.all():
            return int(round(
                obj.reviews.all().aggregate(Avg('score'))['score__avg']
            ))
        return None


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')

    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        """Получение среднего рейтинга."""
        if obj.reviews.all():
            return int(round(
                obj.reviews.all().aggregate(Avg('score'))['score__avg']
            ))
        return None


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        model = Review

    def validate_score(self, value):
        """Проверка значения поля от 1 до 10."""
        if not (1 <= value <= 10):
            raise serializers.ValidationError(
                'Введите число рейтинга от 1 до 10!'
            )
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date',)
        model = Comment

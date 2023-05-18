import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from django.core.mail import send_mail
from django.db.models import Avg
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email',
            'first_name', 'last_name',
            'bio', 'role',
        )

    def validate_first_name(self, value):
        """
        Проверить string <first_name> <= 150 characters.
        """
        if len(value) > 150:
            raise serializers.ValidationError(
                'Длина строки не может быть больше 150 символов.'
            )
        return value

    def validate_last_name(self, value):
        """
        Проверить string <last_name> <= 150 characters.
        """
        if len(value) > 150:
            raise serializers.ValidationError(
                'Длина строки не может быть больше 150 символов.'
            )
        return value

    def validate_username(self, value):
        """
        Проверить string <username>.
        """
        if len(value) > 150:
            raise serializers.ValidationError(
                'Длина строки не может быть больше 150 символов.'
            )
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Строка содержит недопустимые символы.'
            )
        if value == 'me':
            raise serializers.ValidationError(
                'Значение поля не может быть `me`.'
            )
        return value

    def validate_email(self, value):
        """
        Проверить string <email> <= 254 characters.
        """
        if len(value) > 254:
            raise serializers.ValidationError(
                'Длина строки не может быть больше 254 символов.'
            )
        return value

    def validate_role(self, value):
        """
        Проверить корректное поле role.
        """
        if value not in ('admin', 'user', 'moderator'):
            raise serializers.ValidationError('выбрана не существующая роль')
        return value


class UserNotAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username', )

    def create(self, validated_data):
        is_email = is_username = False
        if User.objects.filter(username=validated_data['username']).exists():
            is_username = True
        if User.objects.filter(email=validated_data['email']).exists():
            is_email = True

        if not is_email == is_username:
            message = {'<email> & <username>': 'Поля должны быть уникальными.'}
            raise ValidationError(message)

        confirmation_code = get_random_string(
            length=5, allowed_chars='0123456789')
        validated_data['confirmation_code'] = confirmation_code
        user, created = User.objects.update_or_create(
            username=validated_data['username'],
            defaults=validated_data
        )
        send_mail(
            'Your confirmation code',
            confirmation_code, 'admin@yamdb.ru', [validated_data['email'], ],)
        return user

    def validate_username(self, value):
        """ Проверить string <username>.
        """
        if len(value) > 150:
            raise serializers.ValidationError(
                'Длина строки не может быть больше 150 символов.'
            )
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Строка содержит недопустимые символы.'
            )
        if value == 'me':
            raise serializers.ValidationError(
                'Значение поля не может быть `me`.'
            )
        return value

    def validate_email(self, value):
        """ Проверить string <email> <= 254 characters.
        """
        if len(value) > 254:
            raise serializers.ValidationError(
                'Длина строки не может быть больше 254 символов.'
            )
        return value


class TokenSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(required=True)
    username = serializers.CharField(required=True)

    def validate_username(self, value):
        """ Проверить string <username>.
        """
        if len(value) > 150:
            raise serializers.ValidationError(
                'Длина строки не может быть больше 150 символов.'
            )
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Строка содержит недопустимые символы.'
            )
        if value == 'me':
            raise serializers.ValidationError(
                'Значение поля не может быть `me`.'
            )
        return value


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'
        pass


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'
        pass


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

    def validate(self, data):
        """Проверка на оставление одного отзыва."""
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Можно оставить только один отзыв!.')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date',)
        model = Comment

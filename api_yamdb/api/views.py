from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.viewsets import ModelViewSet

from .permissions import (IsAdminRole, IsAnyIsAdmin,
                          IsAuthorActionOrAdminOrModeratorOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleSerializer,
                          TokenSerializer, SignUpSerializer,
                          UserSerializer, UserNotAdminSerializer)

from api.filters import TitlesFilter
from api.mixins import CreateListDestroyViewSet
from api_yamdb.settings import HOST_EMAIL
from reviews.models import Category, Genre, Review, Title
from users.models import User


class UserViewSet(ModelViewSet):
    """Получение списка пользователей. Доступ Админ."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminRole,)
    filter_backends = (SearchFilter,)
    search_fields = ('username', )
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        methods=['get', 'patch'], detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'GET':
            user = get_object_or_404(
                User, username=request.user)
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        user = get_object_or_404(
            User, username=request.user
        )
        serializer = UserNotAdminSerializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_registry_signup(request):
    """Регистрация пользователя."""
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    is_email = is_username = False
    if User.objects.filter(username=serializer.data['username']).exists():
        is_username = True
    if User.objects.filter(email=serializer.data['email']).exists():
        is_email = True

    if not is_email == is_username:
        message = {'<email> & <username>': 'Поля должны быть уникальными.'}
        raise ValidationError(message)

    user, created = User.objects.update_or_create(
        username=serializer.data['username'], defaults=serializer.data)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(subject='Код доступа',
              message=f'Your confirmation code {confirmation_code}',
              from_email=HOST_EMAIL,
              recipient_list=[serializer.data.get('email')])
    return Response(serializer.data, status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """Получение токена."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User, username=serializer.data.get('username'))
    code = serializer.data['confirmation_code']
    if not default_token_generator.check_token(user, code):
        raise ValidationError(
            {'confirmation_code': f'{code} — код не актуален.'})
    token = str(AccessToken().for_user(user))

    return Response({'token': token}, status=HTTP_200_OK)


class AdminOrReadyViewSet(CreateListDestroyViewSet):
    """Кастомный вьюсет для Genre и Category."""
    permission_classes = (IsAnyIsAdmin,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(AdminOrReadyViewSet):
    """Получить список всех жанров. Доступно без токена."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(AdminOrReadyViewSet):
    """Получить список всех категорий. Доступно без токена."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Получить список всех произведений. Доступно без токена."""
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAnyIsAdmin,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitlesFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update',):
            return TitleSerializer
        return TitleReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Получение списка всех отзывов. Доступно без токена."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorActionOrAdminOrModeratorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        serializer.save(author=self.request.user,
                        title=get_object_or_404(Title, pk=title_id))


class CommentViewSet(viewsets.ModelViewSet):
    """Получение списка всех комментариев. Доступно без токена."""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorActionOrAdminOrModeratorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_review(self, review_id, title_id):
        review = get_object_or_404(Review, id=review_id, title_id=title_id)
        return review

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = self.get_review(review_id, title_id)
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        serializer.save(
            author=self.request.user,
            review=self.get_review(review_id, title_id)
        )

from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.status import HTTP_200_OK
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import AccessToken

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import (IsAdminRole, IsAnyIsAdmin,
                          IsUserEditOnlyPermission,
                          IsAuthorActionOrAdminOrModeratorOrReadOnly)

from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleSerializer,
                          TokenSerializer, UserRegistrationSerializer,
                          UserSerializer, UserNotAdminSerializer)

from api.filters import TitlesFilter
from api.mixins import CreateListDestroyViewSet
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
        permission_classes=(IsUserEditOnlyPermission,)
    )
    def me(self, request):
        if request.method == 'GET':
            user = get_object_or_404(
                User, username=request.user
            )
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


class UserCreateView(APIView):
    """Создание пользователя."""
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenCreateView(APIView):
    """Получение токена."""
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        _username = serializer.data['username']
        if not User.objects.filter(username=_username).exists():
            raise NotFound('Такого значения поля в базе данных нет.')

        _user = User.objects.get(username=_username)

        _code = serializer.data['confirmation_code']
        if not _user.confirmation_code == _code:
            message = {'confirmation_code': f'{_code} — код не актуален.'}
            raise ValidationError(message)
        if _user.role:
            _role = _user.role
        else:
            _role = 'user'
        User.objects.filter(
            username=_username).update(role=_role, confirmation_code='')
        _token = str(AccessToken().for_user(_user))

        return Response({'token': _token}, status=status.HTTP_200_OK)


class GenreViewSet(CreateListDestroyViewSet):
    """Получить список всех жанров. Доступно без токена."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAnyIsAdmin,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class CategoryViewSet(CreateListDestroyViewSet):
    """Получить список всех категорий. Доступно без токена."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAnyIsAdmin, )
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Получить список всех произведений. Доступно без токена."""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAnyIsAdmin,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update',):
            return TitleSerializer
        return TitleReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Получение списка всех отзывов. Доступно без токена."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorActionOrAdminOrModeratorOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        review = title.reviews.filter(author=self.request.user)
        review_count = review.count()
        if review_count > 0:
            raise ValidationError('Нельза оставить больше одного отзыва')
        else:
            serializer.save(author=self.request.user,
                            title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Получение списка всех комментариев. Доступно без токена."""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorActionOrAdminOrModeratorOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        title = get_object_or_404(Title, pk=title_id)
        queryset = title.reviews.all()
        review = get_object_or_404(queryset, pk=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        serializer.save(
            author=self.request.user,
            review=get_object_or_404(
                Review, pk=review_id,
                title=get_object_or_404(Title, pk=title_id)
            )
        )

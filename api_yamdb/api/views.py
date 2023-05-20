from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import (IsAdminRole, IsAnyIsAdmin,
                          IsAuthorActionOrAdminOrModeratorOrReadOnly)

from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleSerializer,
                          TokenSerializer, SignUpSerializer,
                          UserSerializer, UserNotAdminSerializer)

from api.filters import TitlesFilter
from api.mixins import CreateListDestroyViewSet
from reviews.models import Category, Genre, Review, Title
from users.models import User
from api_yamdb.settings import HOST_EMAIL


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
def UserCreateView(request):
    """Регистрация пользователя."""
    serializer = SignUpSerializer(data=request.data)
    if (User.objects.filter(username=request.data.get('username'),
                            email=request.data.get('email'))):
        user = User.objects.get(username=request.data.get('username'))
        serializer = SignUpSerializer(user, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user = User.objects.get(username=request.data.get('username'))
    send_mail(subject="Код доступа",
              message=f'Your confirmation code {user.confirmation_code}',
              from_email=HOST_EMAIL,
              recipient_list=[request.data.get('email')])
    return Response(
        serializer.data, status=HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def TokenCreateView(request):
    """Получение токена."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User, username=request.data.get('username')
    )
    if str(user.confirmation_code) == request.data.get(
            'confirmation_code'):
        refresh = RefreshToken.for_user(user)
        token = {'token': str(refresh.access_token)}
        return Response(
            token, status=HTTP_200_OK
        )
    return Response(
        {'confirmation_code': 'Неверный код подтверждения.'},
        status=HTTP_400_BAD_REQUEST
    )


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

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title_id=title_id)
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        serializer.save(
            author=self.request.user,
            review=get_object_or_404(Review, id=review_id, title_id=title_id)
        )

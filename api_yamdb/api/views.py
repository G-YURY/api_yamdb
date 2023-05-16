from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .pagination import ReviewsPagination, UsersPagination
from .permissions import (IsAdminRole, IsAuthorIsAllRoles, IsAnyIsAdmin,
                          IsAuthorActionsOrReadOnly, IsModeratorRole,
                          IsUserRole)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleSerializer,
                          TokenSerializer, UserRegistrationSerializer,
                          UserSerializer)
from api.filters import TitlesFilter
from api.mixins import CreateListDestroyViewSet
from reviews.models import Category, Genre, Review, Title
from users.models import User


def send_code(email, confirmation_code):
    subject = 'Your confirmation code'
    send_mail(
        subject, confirmation_code, 'admin@yamdb.ru', [email, ],
    )


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = UsersPagination
    lookup_field = 'username'


class UserMeViewSet(RetrieveDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = 'username'

    # def get_object(self):
    #     print('********************')
    #     # queryset = self.get_queryset()
    #     # filter = {}
    #     # for field in self.multiple_lookup_fields:
    #     #     filter[field] = self.kwargs[field]
    #     obj = self.request.user
    #     # self.check_object_permissions(self.request, obj)
    #     return obj


class UserCreateView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        try:
            _user_email = User.objects.get(email=self.request.data['email'])
            _field_name_email = 'email'
        except ObjectDoesNotExist:
            _user_email = None

        try:
            _user_username = User.objects.get(
                username=self.request.data['username'])
            _field_name_username = 'username'
        except ObjectDoesNotExist:
            _user_username = None

        if not _user_email == _user_username:
            _field_name = _field_name_email or _field_name_username
            _field = _user_email.email or _user_username.username
            message = {
                f'{_field_name}': f'{_field} - поля не совпадают.'
            }
            raise ValidationError(message)

        try:
            _user = User.objects.get(
                email=self.request.data['email'],
                username=self.request.data['username']
            )
        except ObjectDoesNotExist:
            _user = None

        confirmation_code = get_random_string(
            length=5,
            allowed_chars='0123456789'
        )
        data = {'code': confirmation_code, 'role': 'user', }
        if not _user:
            serializer.save(code=confirmation_code)
        else:
            serializer.update(_user, data)

        send_code(self.request.data['email'], confirmation_code)


class TokenCreateView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenreViewSet(CreateListDestroyViewSet):
    """Получить список всех жанров. Доступно без токена"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAnyIsAdmin,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class CategoryViewSet(CreateListDestroyViewSet):
    """Получить список всех категорий. Доступно без токена"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAnyIsAdmin, )
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'
    pagination_class = ReviewsPagination


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = (IsAnyIsAdmin,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.action == 'list' or 'retrieve':
            return TitleReadSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = ReviewsPagination
    permission_classes = (IsAuthorActionsOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        print(self.request.method)
        title_id = self.kwargs.get('title_id')
        serializer.save(author=self.request.user,
                        title=get_object_or_404(Title, pk=title_id)
                        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = ReviewsPagination
    permission_classes = (IsAuthorActionsOrReadOnly,)

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

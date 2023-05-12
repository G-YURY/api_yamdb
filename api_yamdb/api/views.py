from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.viewsets import ModelViewSet

from .permissions import IsAuthorActionsOrReadOnly
from .serializers import RegistrationSerializer, UserSerializer
from .serializers import ReviewSerializer, CommentSerializer
from .pagination import ReviewsPagination
from users.models import User
from reviews.models import Title, Review


def send_code(email, confirmation_code):
    subject = 'Your confirmation code'
    send_mail(
        subject, confirmation_code, 'admin@yamdb.ru', ['user4@example.com', ],
    )


class UsersPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = UsersPagination


class UserCreateView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        confirmation_code = get_random_string(
            length=5,
            allowed_chars='0123456789'
        )
        print(confirmation_code)
        send_code(self.request.data['email'], confirmation_code)
        serializer.save(password='system', role=confirmation_code)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = ReviewsPagination
    permission_classes = IsAuthorActionsOrReadOnly

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        serializer.save(author=self.request.user,
                        title=get_object_or_404(Title, pk=title_id)
                        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = ReviewsPagination
    permission_classes = IsAuthorActionsOrReadOnly

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.comments.all()

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

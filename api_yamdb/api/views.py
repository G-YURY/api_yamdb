from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .permissions import IsAuthorActionsOrReadOnly
from .serializers import (TokenSerializer, UserRegistrationSerializer,
                          UserSerializer)
from users.models import User


def send_code(email, confirmation_code):
    subject = 'Your confirmation code'
    send_mail(
        subject, confirmation_code, 'admin@yamdb.ru', [email, ],
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
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        # user = self.request.user
        confirmation_code = get_random_string(
            length=5,
            allowed_chars='0123456789'
        )
        data = {'code': confirmation_code}
        if not _user:
            serializer.save(code=confirmation_code)
        else:
            serializer.update(_user, data)

        send_code(self.request.data['email'], confirmation_code)


class TokenCreateView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        serializer = TokenSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

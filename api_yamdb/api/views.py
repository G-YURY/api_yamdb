from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.viewsets import ModelViewSet

from .permissions import IsAuthorActionsOrReadOnly
from .serializers import RegistrationSerializer, UserSerializer
from users.models import User


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
        # user = self.request.user
        confirmation_code = get_random_string(
            length=5,
            allowed_chars='0123456789'
        )
        print(confirmation_code)
        send_code(self.request.data['email'], confirmation_code)
        serializer.save(password='system', role=confirmation_code)

from django.urls import include, path
from rest_framework import routers

from api.views import UserViewSet, UserCreateView, TokenCreateView

router_v1 = routers.DefaultRouter()

router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path(
        'v1/auth/token/',
        TokenCreateView.as_view(),
        name='token'
    ),
    path(
        'v1/auth/signup/',
        UserCreateView.as_view(),
        name='signup'
    ),
]

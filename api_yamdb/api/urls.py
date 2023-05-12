from django.urls import include, path
from rest_framework import routers

from api.views import UserViewSet, UserCreateView, TitleViewSet
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

router_v1 = routers.DefaultRouter()

router_v1.register('users', UserViewSet, basename='users')
#router_v1.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path(
        'v1/auth/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'v1/auth/signup/',
        UserCreateView.as_view(),
        name='token_obtain_pair'
    ),
]

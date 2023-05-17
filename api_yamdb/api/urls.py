from django.urls import include, path
from rest_framework import routers

from .views import CommentViewSet, ReviewViewSet
from api.views import (CategoryViewSet, GenreViewSet, TitleViewSet,
                       TokenCreateView, UserCreateView, UserMeViewSet,
                       UserViewSet)

router_v1 = routers.DefaultRouter()

router_v1.register(r'users', UserViewSet, basename='users')

router_v1.register('genres', GenreViewSet, basename='genres')

router_v1.register('categories', CategoryViewSet, basename='categories')

router_v1.register('titles', TitleViewSet, basename='titles')

router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)


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
    # path('v1/user/me/', UserMeViewSet, name='me')
]

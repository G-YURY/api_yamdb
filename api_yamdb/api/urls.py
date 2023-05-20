from django.urls import include, path
from rest_framework import routers

from .views import CommentViewSet, ReviewViewSet
from api.views import CategoryViewSet, GenreViewSet, TitleViewSet, UserViewSet
from django.urls import path

from api.views import get_token, user_registry

urls_auth = [
    path('signup/', user_registry, name='signup'),
    path('token/', get_token, name='token'),
]

router_v1 = routers.DefaultRouter()

router_v1.register('users', UserViewSet, basename='users')

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
    path('v1/auth/', include(urls_auth)),
]

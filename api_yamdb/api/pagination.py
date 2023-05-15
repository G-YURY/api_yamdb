from rest_framework.pagination import PageNumberPagination


class UsersPagination(PageNumberPagination):
    page_size = 100


class ReviewsPagination(PageNumberPagination):
    page_size = 10

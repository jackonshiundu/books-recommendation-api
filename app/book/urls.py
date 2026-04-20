"""
Books URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_nested.routers import NestedDefaultRouter

from .views import BookViewSet, ReviewViewset

router = DefaultRouter()

router.register("books", BookViewSet)

book_router = NestedDefaultRouter(router, "books", lookup="book")
book_router.register("reviews", ReviewViewset, basename="book-reviews")

app_name = "book"

urlpatterns = [
    path("", include(router.urls)),
    path("", include(book_router.urls)),
]

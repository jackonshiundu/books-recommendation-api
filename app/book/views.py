"""
Books Views.
"""
from rest_framework import permissions, viewsets
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view

from core.models import Book
# from django.db.models import Avg

from .serializers import BookSerializer

from rest_framework.exceptions import PermissionDenied

from rest_framework.authentication import TokenAuthentication


@extend_schema(tags=["Books Management"])
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="my_books",
                description="Get only your books",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="recommended",
                description="Get recommended books",
                required=False,
                type=bool,
            ),
        ]
    )
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """
        Anyone can view books.
        Only authenticated users can create, update, delete.
        """
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Returns books based on query params:

        GET /api/books/                     → all books sorted by avg rating
        GET /api/books/?my_books=true       → only books the user contributed
        GET /api/books/?recommended=true    → books matching user's top genres
        """
        """
        queryset=Book.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by("-avg_rating")
        """

        queryset = Book.objects.all()

        my_books = self.request.query_params.get("my_books")
        if my_books:
            queryset = queryset.filter(contributor=self.request.user)

        """
        elif recommended:
            # get user's top genres by preference score
            top_genres = UserPreference.objects.filter(
                user=self.request.user
            ).order_by('-score').values_list('genre', flat=True)[:5]

            # exclude books the user already rated
            already_rated = Review.objects.filter(
                user=self.request.user
            ).values_list('book_id', flat=True)

            queryset = queryset.filter(
                genre__in=top_genres
            ).exclude(id__in=already_rated)"""
        return queryset

    def perform_create(self, serializer):
        """Create Book and save the current logged in user as the conributor"""
        serializer.save(contributor=self.request.user)

    def perform_update(self, serializer):
        """Only contributor can update their book"""
        book = self.get_object()
        if book.contributor != self.request.user:
            raise PermissionDenied("You can only edit your own books.")
        serializer.save()

    def perform_destroy(self, instance):
        """Only contributor can delete their book"""
        if instance.contributor != self.request.user:
            raise PermissionDenied("You can only delete your own books.")
        instance.delete()

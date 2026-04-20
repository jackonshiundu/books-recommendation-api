"""
Books Views.
"""
from rest_framework import permissions, viewsets
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view

from core.models import Book, Review
from django.db.models import Avg
from rest_framework.decorators import action


from .serializers import (
    BookSerializer,
    BookDetailSerializer,
    ReviewSerializer,
    ReviewDetailSerializer,
)

from rest_framework.exceptions import PermissionDenied, ValidationError

from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response


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

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookDetailSerializer
        return BookSerializer

    def get_queryset(self):
        """
        Returns books based on query params:

        GET /api/books/                     → all books sorted by avg rating
        GET /api/books/?my_books=true       → only books the user contributed
        GET /api/books/?recommended=true    → books matching user's top genres
        """

        queryset = Book.objects.annotate(avg_rating=Avg("reviews__rating")).order_by(
            "-avg_rating"
        )

        queryset = Book.objects.all()

        my_books = self.request.query_params.get("my_books")
        recommended = self.request.query_params.get("recommended")
        if my_books:
            queryset = queryset.filter(contributor=self.request.user)

        elif recommended:
            # genres from books they contributed
            contributed_genres = Book.objects.filter(
                contributor=self.request.user
            ).values_list("genre", flat=True)

            # genres from books they rated above 3
            rated_genres = Review.objects.filter(
                user=self.request.user, rating__gt=3
            ).values_list("book__genre", flat=True)

            # combine both genre sources and remove duplicates
            from itertools import chain

            all_genres = set(chain(contributed_genres, rated_genres))

            queryset = queryset.filter(genre__in=all_genres)

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


@extend_schema(tags=["Reviews Management"])
class ReviewViewset(viewsets.ModelViewSet):
    """Viewset for managing reviews."""

    serializer_class = ReviewSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """
        Anyone can read reviews.
        Only authenticated users can create, update,delete.
        """

        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        """Use details serializer for for retrieve."""
        if self.action == "retrieve":
            return ReviewDetailSerializer
        return ReviewSerializer

    def get_queryset(self):
        """Retrive all books for a book or my review for a book."""

        return Review.objects.filter(book_id=self.kwargs["book_pk"]).order_by(
            "created_at"
        )

    def perform_create(self, serializer):
        """Createa review - on per user per book."""
        book_id = self.kwargs["book_pk"]
        book = Book.objects.get(id=book_id)

        if Review.objects.filter(book=book, user=self.request.user).exists():
            raise ValidationError("You have already reviewed this book.")

        serializer.save(user=self.request.user, book=book)

    def perform_update(self, serializer):
        """Only the review owner can update"""
        review = self.get_object()

        if review.user != self.request.user:
            raise PermissionDenied("You can only edit your own review")
        serializer.save()

    def perform_destroy(self, instance):
        """Only the review owner can delete."""
        if instance.user != self.request.user:
            raise PermissionDenied("You can only delete your own reviews.")
        instance.delete()

    @action(
        detail=False,
        methods=["get"],
        url_path="mine",
        permission_classes=[permissions.IsAuthenticated],
    )
    def mine(self, request, book_pk=None):
        """Viewset for getting my review for a book"""
        review = Review.objects.filter(book_id=book_pk, user=request.user).first()

        if not review:
            return Response(
                {"detail": "You have not reviewed this book yet."}, status=404
            )

        serializer = ReviewDetailSerializer(review)
        return Response(serializer.data)

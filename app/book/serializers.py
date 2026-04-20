"""
Books Serializer.
"""
from rest_framework import serializers
from core.models import Book, Review


class ReviewSerializer(serializers.ModelSerializer):
    """Review Serialize."""

    class Meta:
        model = Review
        fields = [
            "id",
            "book",
            "user",
            "rating",
            "review_text",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "book", "created_at", "updated_at"]


class ReviewDetailSerializer(ReviewSerializer):
    """Review Detail Serializer — includes username for display"""

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "book",
            "user",
            "rating",
            "review_text",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "book", "created_at", "updated_at"]


class BookSerializer(serializers.ModelSerializer):
    """Boook Data serializer"""

    cover_image = serializers.ImageField(required=False)

    class Meta:
        model = Book
        fields = [
            "id",
            "book_name",
            "author",
            "summary",
            "published_date",
            "genre",
            "age_group",
            "cover_image",
            "isbn",
            "contributor",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "contributor", "created_at", "updated_at"]

    def create(self, validated_data):
        return Book.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update a book."""

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class BookDetailSerializer(BookSerializer):
    """Serializer for book detail view — used for retrieve and update"""

    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + [
            "summary",
            "published_date",
            "created_at",
            "updated_at",
            "reviews",
        ]
        read_only_fields = BookSerializer.Meta.read_only_fields + [
            "created_at",
            "updated_at",
        ]

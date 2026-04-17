"""
Books Serializer.
"""
from rest_framework import serializers
from core.models import Book


class BookSerializer(serializers.ModelSerializer):
    """Boook Data serializer"""

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

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + [
            "summary",
            "published_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = BookSerializer.Meta.read_only_fields + [
            "created_at",
            "updated_at",
        ]

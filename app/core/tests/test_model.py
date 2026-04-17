from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Book, Review
from datetime import date

User = get_user_model()


def create_user(email="user@example.com", password="test12345"):
    """Helper function to create a user"""
    return User.objects.create_user(email=email, password=password)


def create_book(contributor, genre="Self Help"):
    """Helper function to create a book"""
    return Book.objects.create(
        contributor=contributor,
        book_name="Atomic Habits",
        author="James Clear",
        genre=genre,
    )


class ModelTest(TestCase):
    """Test to test models"""

    def test_create_user_with_email_successfull(self):
        """Test creating a new user with an email is successful"""
        email = "test@example.com"
        password = "testpass123"

        user = User.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_email_normalized(self):
        """Test the email for a new user is normalized."""

        sample_emails = [
            ["test1@example.com", "test1@example.com"],
            ["TEST2@EXAMPLE.COM", "TEST2@example.com"],
            ["Test3@Example.Com", "Test3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]

        for email, expected in sample_emails:
            user = User.objects.create_user(email=email, password="sample1234")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test creating a user without an email raises a ValueError"""

        with self.assertRaises(ValueError):
            User.objects.create_user("", password="sample1234")

    def test_create_superuser(self):
        """Test creating a new superuser"""
        super_user = User.objects.create_superuser(
            email="admin@example.com", password="admin12345"
        )
        self.assertTrue(super_user.is_superuser)

    def test_book_model(self):
        """Test creating a book successful"""
        user = create_user()
        book = Book.objects.create(
            contributor=user,
            isbn="9780439554930",
            book_name="Harry Potter and the Sorcerer's Stone",
            author="J.K. Rowling",
            summary="A young boy discovers he is a wizard and attends a magical school.",
            published_date=date(1997, 6, 26),
            genre="Fantasy",
            age_group="children",   # FIXED
            cover_image="harry_potter_1.jpg",
        )

        self.assertEqual(str(book), book.book_name)  # FIXED

    def test_create_review_successful(self):
        """Test creating a review successful"""

        user = create_user()
        book = create_book(contributor=user)

        review = Review.objects.create(
            book=book,
            user=user,
            rating=5,
            review_text="Great book!"
        )

        self.assertEqual(review.book, book)
        self.assertEqual(review.user, user)
        self.assertEqual(review.rating, 5)

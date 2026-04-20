from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Book, Review, UserPrefrence
from datetime import date
from django.core.exceptions import ValidationError

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
            age_group="children",
            cover_image="harry_potter_1.jpg",
        )

        self.assertEqual(str(book), book.book_name)

    def test_create_review_successful(self):
        """Test creating a review successful"""

        user = create_user()
        book = create_book(contributor=user)

        review = Review.objects.create(
            book=book, user=user, rating=5, review_text="Great book!"
        )

        self.assertEqual(review.book, book)
        self.assertEqual(review.user, user)
        self.assertEqual(review.rating, 5)

    def test_review_rating_below_minimum_fails(self):
        """Test that a rating below 1 raises validation error."""
        user = create_user()
        book = create_book(contributor=user)

        review = Review.objects.create(user=user, book=book, rating=0)
        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_review_rating_above_maximum_fails(self):
        """Test that a rating below 1 raises validation error."""
        user = create_user()
        book = create_book(contributor=user)

        review = Review.objects.create(user=user, book=book, rating=6)
        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_one_review_per_user_per_book(self):
        """Test that a user cannot review the same book twice"""
        user = create_user()
        book = create_book(contributor=user)
        Review.objects.create(book=book, user=user, rating=4)
        with self.assertRaises(Exception):
            Review.objects.create(book=book, user=user, rating=3)

    def test_different_users_can_review_same_book(self):
        """Test that different users can review the same book"""
        user1 = create_user(email="user1@example.com")
        user2 = create_user(email="user2@example.com")
        book = create_book(contributor=user1)
        Review.objects.create(book=book, user=user1, rating=5)
        Review.objects.create(book=book, user=user2, rating=3)
        self.assertEqual(Review.objects.filter(book=book).count(), 2)

    def test_review_text_is_optional(self):
        """Test that review text is optional"""
        user = create_user()
        book = create_book(contributor=user)
        review = Review.objects.create(book=book, user=user, rating=4)
        self.assertIsNone(review.review_text)

    def test_review_has_created_at_and_updated_at(self):
        """Test that review has timestamps"""
        user = create_user()
        book = create_book(contributor=user)
        review = Review.objects.create(book=book, user=user, rating=4)
        self.assertIsNotNone(review.created_at)
        self.assertIsNotNone(review.updated_at)

    def test_create_preference_successful(self):
        """Test creating a user preference is successful"""
        user = create_user()
        pref = UserPrefrence.objects.create(user=user, genre="Self Help", score=1)
        self.assertEqual(pref.user, user)
        self.assertEqual(pref.genre, "Self Help")
        self.assertEqual(pref.score, 1)

    def test_preference_default_score_is_zero(self):
        """Test that default score is 0"""
        user = create_user()
        pref = UserPrefrence.objects.create(user=user, genre="Fiction")
        self.assertEqual(pref.score, 0)

    def test_unique_together_user_and_genre(self):
        """Test that a user cannot have duplicate genre preferences"""
        user = create_user()
        UserPrefrence.objects.create(user=user, genre="Fiction")
        with self.assertRaises(Exception):
            UserPrefrence.objects.create(user=user, genre="Fiction")

    def test_different_genres_for_same_user(self):
        """Test that a user can have multiple genre preferences"""
        user = create_user()
        UserPrefrence.objects.create(user=user, genre="Fiction")
        UserPrefrence.objects.create(user=user, genre="Self Help")
        self.assertEqual(UserPrefrence.objects.filter(user=user).count(), 2)

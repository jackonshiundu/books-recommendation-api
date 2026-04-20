"""
Review endpoints Tests
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import Book, Review

from datetime import date

from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


def review_list_url(book_id):
    """Return review list URL for a book."""
    return reverse("book:book-reviews-list", args=[book_id])


def review_detail_url(book_id, review_id):
    """Return review detail URL."""
    return reverse("book:book-reviews-detail", args=[book_id, review_id])


def mine_url(book_id):
    """Return my review URL for a book."""
    return reverse("book:book-reviews-mine", args=[book_id])


def create_book(user, **params):
    """Create an return a sample Book."""
    defaults = {
        "book_name": "Harry Potter and the Sorcerer's Stone",
        "author": "J.K. Rowling",
        "summary": "A young boy discovers he is a wizard and attends a magical school.",
        "published_date": date(1997, 6, 26),
        "genre": "Fantasy",
        "age_group": "children",
        "cover_image": "harry_potter_1.jpg",
    }
    defaults.update(params)

    book = Book.objects.create(contributor=user, **defaults)

    return book


def create_user(email="test@example.com", password="example1234"):
    """Create and return a user."""
    return User.objects.create_user(email, password)


class PublicReviewsAPI(TestCase):
    """Test unauthenticated API reviews Endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.book = create_book(user=self.user)

    def test_book_reviews_return_success(self):
        """Test unauthenticated user can retrieve book reviews."""

        Review.objects.create(book=self.book, user=self.user, rating=4)
        res = self.client.get(review_list_url(self.book.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_get_single_review_success(self):
        """Test unauthenticated user can retrieve a single review."""
        review = Review.objects.create(book=self.book, user=self.user, rating=4)

        res = self.client.get(review_detail_url(self.book.id, review.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["rating"], review.rating)

    def test_unauthenticated_create_review_fails(self):
        """Test unauthenticated user cannot create a review."""
        payload = {"rating": 4, "review_text": "great book"}
        res = self.client.post(review_list_url(self.book.id), payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateReviewAPITest(TestCase):
    """Test authenticated API reviews Endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)
        self.book = create_book(user=self.user)

    def test_create_review_success(self):
        """Test authenticated user can create a review."""

        payload = {"rating": 4, "review_text": "great book"}

        res = self.client.post(review_list_url(self.book.id), payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["rating"], payload["rating"])
        self.assertEqual(Review.objects.filter(book=self.book.id).count(), 1)

    def test_create_duplicate_review_fails(self):
        """Test user cannot review the same book twice."""
        Review.objects.create(book=self.book, user=self.user, rating=4)

        payload = {"rating": 3, "review_text": "Second review attempt."}

        res = self.client.post(review_list_url(self.book.id), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_different_users_can_review_same_book(self):
        """Test different users can review the same book."""

        other_user = create_user(email="other@example.com")
        other_client = APIClient()
        other_client.force_authenticate(user=other_user)

        Review.objects.create(book=self.book, user=self.user, rating=4)
        payload = {"rating": 4, "review_text": "Also a great book!"}

        res = other_client.post(review_list_url(self.book.id), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.filter(book=self.book).count(), 2)

    def test_update_own_revew_success(self):
        """Test user can update their own review."""
        review = Review.objects.create(book=self.book, user=self.user, rating=4)
        payload = {"rating": 5, "review_text": "Changed my mind, great book!"}

        res = self.client.patch(review_detail_url(self.book.id, review.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.rating, payload["rating"])

    def test_update_other_users_review_fails(self):
        """Test user cannot update another user's review."""
        other_user = create_user(email="other@example.com")
        review = Review.objects.create(book=self.book, user=other_user, rating=3)

        payload = {"rating": 1}
        res = self.client.patch(review_detail_url(self.book.id, review.id), payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_review_success(self):
        """Test user can delete their own review."""
        review = Review.objects.create(book=self.book, user=self.user, rating=4)

        res = self.client.delete(review_detail_url(self.book.id, review.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    def test_delete_other_users_reviews_fails(self):
        """Test user cannot delete another user's review."""
        other_user = create_user(email="other@example.com")
        review = Review.objects.create(book=self.book, user=other_user, rating=4)

        res = self.client.delete(review_detail_url(self.book.id, review.id))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Review.objects.filter(id=review.id).exists())

    def test_get_my_review_for_book_success(self):
        """Test user can get their own review for a specific book."""

        review = Review.objects.create(
            book=self.book, user=self.user, rating=5, review_text="loved it!."
        )

        res = self.client.get(mine_url(self.book.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["rating"], review.rating)

    def test_get_my_review_not_reviewed_returns_404(self):
        """Test getting my review when not reviewed returns 404."""
        res = self.client.get(mine_url(self.book.id))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

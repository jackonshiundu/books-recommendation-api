"""
Books endpoints Tests
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import Book
from book.serializers import BookSerializer
from datetime import date

from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

BOOK_URL = reverse("book:book-list")


def book_detail_url(book_id):
    """Return book detail URL."""
    return reverse("book:book-detail", args=[book_id])


def create_user(email="test@example.com", password="example1234"):
    """Create and return a user."""
    return User.objects.create_user(email, password)


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


class PublicBooksApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_all_book_success(self):
        """Test to check books retrieval sucess"""

        res = self.client.get(BOOK_URL)
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_single_book_success(self):
        """Test unauthenticated user can retrieve a single book."""
        self.user = create_user()
        book = Book.objects.create(
            contributor=self.user,
            book_name="Test Book",
            author="Test Author",
            genre="Fiction",
        )

        res = self.client.get(book_detail_url(book.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["book_name"], book.book_name)


class PrivateBooksApiTest(TestCase):
    """Test authenticaed Books API requests"""

    def setUp(self):
        self.client = APIClient()

        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_add_a_book(self):
        """Test to check book add successful."""

        payload = {
            "book_name": "Harry Potter and the Sorcerer's Stone",
            "author": "J.K. Rowling",
            "summary": "A young boy discovers he is a wizard and attends a magical school.",
            "genre": "Fantasy",
            "age_group": "children",
        }

        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        book = Book.objects.get(id=res.data["id"])

        for k, v in payload.items():
            self.assertEqual(getattr(book, k), v)

        self.assertEqual(book.contributor, self.user)

    def test_my_books_route_limits_to_user_books(self):
        """Test to check if the user's books are limited biy them"""
        other_user = User.objects.create_user(
            email="other@example.com", password="testpass123"
        )

        create_book(user=other_user, isbn="9780439554930")
        create_book(user=self.user)

        res = self.client.get(BOOK_URL, {"my_books": True})

        books = Book.objects.filter(contributor=self.user).order_by("-id")
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update(self):
        """Test partial update to the Books"""

        book = create_book(user=self.user)
        payload = {
            "age_group": "adult",
        }

        url = book_detail_url(book.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        book.refresh_from_db()
        self.assertEqual(book.age_group, payload["age_group"])
        self.assertEqual(book.contributor, self.user)

    def test_full_update(self):
        """Test full update success."""

        book = create_book(user=self.user)

        payload = {
            "book_name": "The Sorcerer's Stone",
            "author": "J.K. Rowling",
            "summary": "A young boy discovers he is a wizard and attends a magical school.",
            "published_date": date(1997, 7, 26),
            "genre": "Fantasy",
            "age_group": "adult",
            "cover_image": "harry_potter_2.jpg",
        }

        url = book_detail_url(book.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        book.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(book, k), v)

    def test_delete_book_success(self):
        """Test to check if deleting a book is successfull."""

        book = create_book(user=self.user)

        url = book_detail_url(book.id)

        res = self.client.delete(url)

        self.assertTrue(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())

    def test_error_deleting_other_users_book_erro(self):
        """Test to check deletign ptehr user erros"""

        new_user = create_user(email="newuser@example.com", password="passwordnew123")

        book = create_book(user=new_user)
        url = book_detail_url(book.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(id=book.id).exists())

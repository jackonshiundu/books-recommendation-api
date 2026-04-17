from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and saves a new user"""
        if not email:
            raise ValueError("Users must have an email address.")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and saves a new super user"""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User Model"""

    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Custom fields
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    objects = UserManager()
    USERNAME_FIELD = "email"


class Book(models.Model):
    """Book Model"""

    AGE_GROUP_CHOICES = [
        ("children", "Children"),
        ("young_adult", "Young Adult"),
        ("adult", "Adult"),
    ]
    contributor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="contributed_books"
    )
    isbn = models.CharField(max_length=20, unique=True, null=True, blank=True)
    book_name = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    summary = models.TextField(blank=True)
    published_date = models.DateField(null=True, blank=True)
    genre = models.CharField(max_length=50)
    age_group = models.CharField(max_length=50, choices=AGE_GROUP_CHOICES, blank=True)
    cover_image = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.book_name


class Review(models.Model):
    """Review Model"""

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("book", "user")


class UserPrefrence(models.Model):
    """User prefrence Model."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="preferences")
    genre = models.CharField(max_length=50)
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = ("user", "genre")

"""
URLs fro the user API.
"""
from django.urls import path
from user import views

app_name = "user"

urlpatterns = [
    path("create/", views.CreateUser.as_view(), name="create"),
    path("login/", views.CreateToken.as_view(), name="login"),
    path("me/", views.ManageUserView.as_view(), name="me"),
]

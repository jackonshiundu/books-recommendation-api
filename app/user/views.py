"""
Views for the user API.
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from drf_spectacular.utils import extend_schema
from rest_framework.settings import api_settings

from .serializers import UserSerializer, AuthTokenSerializer

# Create your views here.


@extend_schema(tags=["User Management"])
class CreateUser(generics.CreateAPIView):
    "Create a new user."

    serializer_class = UserSerializer


@extend_schema(tags=["User Management"])
class CreateToken(ObtainAuthToken):
    """Create a new auth token for the user."""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


@extend_schema(tags=["User Management"])
class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """Manage aithenicated users views"""

    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return Authenticated User"""
        return self.request.user

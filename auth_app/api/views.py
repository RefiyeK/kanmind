
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


from auth_app.models import User
from .serializers import RegistrationSerializer, LoginSerializer


class RegistrationView(APIView):
    """View for registering new users. Returns an auth token after successful creation."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Creates a new user and returns the auth token together with user data."""
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'fullname': user.fullname,
                'email': user.email,
                'user_id': user.id,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """View for logging in an existing user. Returns an auth token on successful authentication."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticates the user via email and password and returns the auth token."""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'fullname': user.fullname,
                'email': user.email,
                'user_id': user.id,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailCheckView(APIView):
    """View for checking whether an email address belongs to a registered user."""

    # No permission_classes override: relies on the default IsAuthenticated from settings.

    def get(self, request):
        """Looks up a user by email address and returns their data."""
        email = request.query_params.get('email')
        if not email:
            return Response(
                {'error': 'The email parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = User.objects.filter(email=email).first()
        if user is None:
            return Response(
                {'error': 'No user with this email address was found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        data = {'id': user.id, 'email': user.email, 'fullname': user.fullname}
        return Response(data, status=status.HTTP_200_OK)

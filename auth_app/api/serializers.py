from rest_framework import serializers
from auth_app.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for registering new users with password confirmation."""

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        """Verifies that the password and the password confirmation match."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {'password': 'The passwords do not match.'}
            )
        return attrs

    def create(self, validated_data):
        """Creates a new user with a hashed password via the CustomUserManager."""
        # Remove repeated_password since it is not a field on the User model.
        validated_data.pop('repeated_password')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for login: validates email and password against the database."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticates the user based on email and password."""
        email = attrs.get('email')
        password = attrs.get('password')
        # Same message in both cases to avoid revealing whether the email exists.
        user = User.objects.filter(email=email).first()
        if user is None:
            raise serializers.ValidationError(
                'Invalid email or password.'
            )
        if not user.check_password(password):
            raise serializers.ValidationError(
                'Invalid email or password.'
            )
        # Pass the authenticated user to the view via validated_data.
        attrs['user'] = user
        return attrs

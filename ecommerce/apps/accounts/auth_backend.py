from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

UserModel = get_user_model()


class EmailAuthBackend(object):
    """
    Email Authentication Backend

    Allows a user to sign in using an email/password pair rather than
    a username/password pair.
    """

    def authenticate(self, _request, email=None, password=None):
        """Authenticate a user based on email address as the user name."""
        try:
            user = UserModel.objects.get(email=email)
            if user.check_password(password):
                return user
            else:
                print("password mismatch")
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

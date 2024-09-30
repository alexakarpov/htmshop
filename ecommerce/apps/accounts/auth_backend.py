import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

UserModel = get_user_model()

logger = logging.getLogger(__name__)


class EmailAuthBackend(object):
    """
    Email Authentication Backend

    Allows a user to sign in using an email/password pair rather than
    a username/password pair.
    """

    def authenticate(self, _request, email=None, password=None):
        """Authenticate a user based on email address as the user name."""
        logger.debug("custom auth - authenticate")
        try:
            user = UserModel.objects.get(email=email)
            if user.check_password(password):
                logger.debug(f"custom auth - got a valid password for {user}")
                return user
            else:
                logger.error(f"password mismatch for {email}")
                return None
        except UserModel.DoesNotExist:
            logger.debug("in custom auth - user doesn't exist")
            return None

    def get_user(self, user_id):
        logger.debug("in custom auth - get_user")
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

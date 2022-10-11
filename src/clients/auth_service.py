from logging import getLogger

logger = getLogger(__name__)


class AuthService(object):
    @classmethod
    def get_user_data(cls, username: str) -> dict:
        # This is mock client.
        # This should request the auth service and get user data.
        # This is not that cachable. because users can be too many
        # and changes to their profile may be frequent.
        try:
            return {
                "username": "mockuser",
                "email": "mockemail@gmail.com",
                "age": 20
            }
        except Exception as e:
            logger.error(str(e))
            return {}

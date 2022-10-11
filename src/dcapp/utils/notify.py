import logging
from clients.brand_page_service import BrandPageService
from clients.auth_service import AuthService

logger = logging.getLogger(__name__)


def send_notification_to_brand(brand_slug: str, username: str):
    notify_method_to_function = {
        "webhook": send_webhook_notification,
        "email": send_email_notification
    }
    notify_info = BrandPageService.get_notify_info(brand_slug)
    if not notify_info:
        logger.error(
            "Unable to send {} data to {}".format(username, brand_slug)
        )
        return  # Can retry the task with delay.

    func = notify_method_to_function.get(notify_info.get("method"))
    if not func:
        logger.error(
            "No function found for notification with method {}".format(
                notify_info.get("method")
            )
        )
        logger.error(
            "Unable to send {} data to {}".format(username, brand_slug)
        )
        return  # Can retry the task with delay.

    user_data = AuthService.get_user_data(username)
    if not user_data:
        logger.error(
            "Unable to send {} data to {}".format(username, brand_slug)
        )
        return  # Can retry the task with delay.

    func(notify_info["data"], user_data)


def send_webhook_notification(notify_data: str, user_data: str):
    # url = notify_data['url']
    # requests.post(
    #     url, json=user_data,
    #     content_type='application/json', retry=settings.retry_count
    # )
    pass


def send_email_notification(notify_data: str, user_data: str):
    # request email service to send the email.
    pass

import logging

from threading import Thread

from clients.brand_page_service import BrandPageService
from clients.auth_service import AuthService

logger = logging.getLogger(__name__)


def send_async_notification_to_brand(brand_slug: str, username: str):
    # This is for the purpose of demonstrating async communication.
    # Using threads for async tasks is not a good practice in production.
    # Threads are hard to debug, and lose data in case of container crash.
    # With high loads and in production, Its better to use a
    # persistant task queue like Celery.
    thread = Thread(
        target=send_notification_to_brand,
        args=(brand_slug, username)
    )
    thread.start()


def send_notification_to_brand(brand_slug: str, username: str):
    notify_method_to_function = {
        "webhook": send_webhook_notification,
        "email": send_email_notification
    }
    notify_method, notify_data = BrandPageService.get_notify_info(brand_slug)
    if not notify_method or not notify_data:
        logger.error(
            "Unable to send {} data to {}".format(username, brand_slug)
        )
        return  # Can retry the task with delay.

    func = notify_method_to_function.get(notify_method)
    if not func:
        logger.error(
            "No function found for notification with method {}".format(notify_method)
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

    func(notify_data, user_data)


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

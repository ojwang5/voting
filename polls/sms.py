import logging
import os

logger = logging.getLogger(__name__)


def _get_env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    return value.strip() if isinstance(value, str) else value


def send_sms(to_phone: str, message: str) -> bool:
    """Send an SMS using Africa's Talking.

    Returns True on successful API call, otherwise False.

    Required environment variables:
      - AT_USERNAME
      - AT_API_KEY
      - AT_FROM (shortcode / sender id)

    Note: This project keeps OTP demo visible in UI for now; this function is
    only responsible for delivery.
    """
    if not to_phone:
        logger.warning("SMS not sent: empty to_phone")
        return False
    if not message:
        logger.warning("SMS not sent: empty message")
        return False

    at_username = _get_env("AT_USERNAME")
    at_api_key = _get_env("AT_API_KEY")
    at_from = _get_env("AT_FROM")

    if not at_username or not at_api_key or not at_from:
        logger.error(
            "SMS not sent: missing Africa's Talking config. "
            "Set AT_USERNAME, AT_API_KEY, AT_FROM"
        )
        return False

    # Import lazily so the app can start without the dependency in dev.
    try:
        from africastalking import AfricasTalking
    except Exception as e:
        logger.exception("Africa's Talking SDK import failed")
        return False

    try:
        africastalking = AfricasTalking(at_username, at_api_key)
        sms = africastalking.SMS

        # Africa's Talking expects E.164 or local format. We send as-is.
        response = sms.send(
            to=[to_phone],
            message=message,
            sender_id=at_from,
        )

        # Typical response: { 'SMSMessageData': [ ... ] }
        logger.info("Africa's Talking SMS response: %s", response)
        return True
    except Exception as e:
        logger.exception("Failed to send SMS via Africa's Talking: %s", str(e))
        return False


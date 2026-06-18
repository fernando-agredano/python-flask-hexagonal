import logging
from app.domain.entities.notification import Notification
from app.domain.ports.notification_sender_port import NotificationSenderPort

logger = logging.getLogger(__name__)


class EmailSender(NotificationSenderPort):
    """
    Adaptador de email simulado.
    En producción aquí iría SMTP, SendGrid, SES, etc.
    El dominio nunca sabe si es real o simulado.
    """

    def send(self, notification: Notification) -> bool:
        logger.info(
            f"[EMAIL] Para: {notification.recipient} | "
            f"Asunto: {notification.subject} | "
            f"Cuerpo: {notification.body[:60]}..."
        )
        # Simulamos éxito (en producción: llamada real al servicio de email)
        return True

    def supports(self, channel: str) -> bool:
        return channel == "email"


class SmsSender(NotificationSenderPort):
    """
    Adaptador SMS simulado.
    En producción aquí iría Twilio, AWS SNS, etc.
    """

    def send(self, notification: Notification) -> bool:
        logger.info(
            f"[SMS] Para: {notification.recipient} | "
            f"Mensaje: {notification.body[:80]}"
        )
        return True

    def supports(self, channel: str) -> bool:
        return channel == "sms"


class InAppSender(NotificationSenderPort):
    """
    Adaptador de notificación in-app simulado.
    En producción podría escribir a Redis, WebSocket, Firebase, etc.
    """

    def send(self, notification: Notification) -> bool:
        logger.info(
            f"[IN_APP] Para: {notification.recipient} | "
            f"Titulo: {notification.subject}"
        )
        return True

    def supports(self, channel: str) -> bool:
        return channel == "in_app"

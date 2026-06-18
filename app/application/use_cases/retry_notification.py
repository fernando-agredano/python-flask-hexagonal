from typing import List
from app.domain.ports.notification_repository_port import NotificationRepositoryPort
from app.domain.ports.notification_sender_port import NotificationSenderPort

MAX_RETRIES = 3


class RetryNotificationUseCase:
    def __init__(
        self,
        repository: NotificationRepositoryPort,
        senders: List[NotificationSenderPort],
    ):
        self._repository = repository
        self._senders = senders

    def execute(self, notification_id: str):
        notification = self._repository.find_by_id(notification_id)
        if not notification:
            raise ValueError(f"Notificación '{notification_id}' no encontrada")

        if not notification.can_retry(MAX_RETRIES):
            raise ValueError(
                f"La notificación no puede reintentarse. "
                f"Status: {notification.status.value}, "
                f"Intentos: {notification.retry_count}/{MAX_RETRIES}"
            )

        notification.increment_retry()

        sender = next(
            (s for s in self._senders if s.supports(notification.channel.value)),
            None
        )
        if not sender:
            notification.mark_failed(f"No hay sender para canal '{notification.channel.value}'")
            return self._repository.update(notification)

        success = sender.send(notification)
        if success:
            notification.mark_sent()
        else:
            notification.mark_failed("El sender reportó error en reintento")

        return self._repository.update(notification)

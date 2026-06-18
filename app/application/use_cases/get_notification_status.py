from typing import Optional
from app.domain.entities.notification import Notification
from app.domain.ports.notification_repository_port import NotificationRepositoryPort


class GetNotificationStatusUseCase:
    def __init__(self, repository: NotificationRepositoryPort):
        self._repository = repository

    def execute(self, notification_id: str) -> Notification:
        notification = self._repository.find_by_id(notification_id)
        if not notification:
            raise ValueError(f"Notificación '{notification_id}' no encontrada")
        return notification

from typing import List, Optional
from app.domain.entities.notification import Notification, NotificationStatus
from app.domain.ports.notification_repository_port import NotificationRepositoryPort


class ListNotificationsUseCase:
    def __init__(self, repository: NotificationRepositoryPort):
        self._repository = repository

    def execute(
        self,
        status: Optional[str] = None,
        channel: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        parsed_status = None
        if status:
            try:
                parsed_status = NotificationStatus(status)
            except ValueError:
                valid = [s.value for s in NotificationStatus]
                raise ValueError(f"Status inválido: '{status}'. Válidos: {valid}")

        items = self._repository.find_all(
            status=parsed_status,
            channel=channel,
            limit=limit,
            offset=offset,
        )
        total = self._repository.count(status=parsed_status)

        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.notification import Notification, NotificationStatus


class NotificationRepositoryPort(ABC):
    """
    Puerto de salida (driven port).
    Define QUÉ necesita el dominio para persistir notificaciones.
    La infraestructura provee la implementación concreta.
    """

    @abstractmethod
    def save(self, notification: Notification) -> Notification:
        pass

    @abstractmethod
    def find_by_id(self, notification_id: str) -> Optional[Notification]:
        pass

    @abstractmethod
    def find_all(
        self,
        status: Optional[NotificationStatus] = None,
        channel: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Notification]:
        pass

    @abstractmethod
    def update(self, notification: Notification) -> Notification:
        pass

    @abstractmethod
    def count(self, status: Optional[NotificationStatus] = None) -> int:
        pass

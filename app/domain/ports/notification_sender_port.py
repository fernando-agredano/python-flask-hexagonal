from abc import ABC, abstractmethod
from app.domain.entities.notification import Notification


class NotificationSenderPort(ABC):
    """
    Puerto de salida (driven port).
    Define QUÉ necesita el dominio para enviar notificaciones.
    Puede haber múltiples adaptadores: email real, SMS, simulado, etc.
    """

    @abstractmethod
    def send(self, notification: Notification) -> bool:
        """
        Intenta enviar la notificación.
        Retorna True si fue exitoso, False si falló.
        """
        pass

    @abstractmethod
    def supports(self, channel: str) -> bool:
        """Indica si este sender soporta el canal dado."""
        pass

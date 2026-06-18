from typing import List
from app.domain.entities.notification import Notification, NotificationChannel
from app.domain.ports.notification_repository_port import NotificationRepositoryPort
from app.domain.ports.notification_sender_port import NotificationSenderPort


class SendNotificationUseCase:
    """
    Caso de uso: enviar una notificación nueva.
    No sabe nada de Flask, SQLite ni email real — solo orquesta puertos.
    """

    def __init__(
        self,
        repository: NotificationRepositoryPort,
        senders: List[NotificationSenderPort],
    ):
        self._repository = repository
        self._senders = senders

    def execute(
        self,
        recipient: str,
        subject: str,
        body: str,
        channel: str,
    ) -> Notification:
        # Validar canal
        try:
            ch = NotificationChannel(channel)
        except ValueError:
            valid = [c.value for c in NotificationChannel]
            raise ValueError(f"Canal inválido: '{channel}'. Válidos: {valid}")

        # Crear entidad de dominio
        notification = Notification(
            recipient=recipient,
            subject=subject,
            body=body,
            channel=ch,
        )

        # Persistir en estado PENDING
        saved = self._repository.save(notification)

        # Buscar sender que soporte el canal
        sender = next((s for s in self._senders if s.supports(channel)), None)
        if not sender:
            saved.mark_failed(f"No hay sender disponible para el canal '{channel}'")
            return self._repository.update(saved)

        # Intentar envío
        success = sender.send(saved)
        if success:
            saved.mark_sent()
        else:
            saved.mark_failed("El sender reportó un error al enviar")

        return self._repository.update(saved)

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Integer, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.domain.entities.notification import (
    Notification,
    NotificationStatus,
    NotificationChannel,
)
from app.domain.ports.notification_repository_port import NotificationRepositoryPort

Base = declarative_base()


class NotificationModel(Base):
    """Modelo SQLAlchemy — vive en la capa de infraestructura, no en el dominio."""
    __tablename__ = "notifications"

    id = Column(String, primary_key=True)
    recipient = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    error_message = Column(String, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False)
    sent_at = Column(DateTime, nullable=True)


class SQLiteNotificationRepository(NotificationRepositoryPort):
    """
    Adaptador concreto del puerto NotificationRepositoryPort.
    Implementa la persistencia usando SQLite + SQLAlchemy.
    El dominio nunca importa esta clase directamente.
    """

    def __init__(self, session: Session):
        self._session = session

    def save(self, notification: Notification) -> Notification:
        model = NotificationModel(
            id=notification.id,
            recipient=notification.recipient,
            subject=notification.subject,
            body=notification.body,
            channel=notification.channel.value,
            status=notification.status.value,
            error_message=notification.error_message,
            retry_count=notification.retry_count,
            created_at=notification.created_at,
            sent_at=notification.sent_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, notification_id: str) -> Optional[Notification]:
        model = self._session.query(NotificationModel).filter_by(id=notification_id).first()
        return self._to_entity(model) if model else None

    def find_all(
        self,
        status: Optional[NotificationStatus] = None,
        channel: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Notification]:
        query = self._session.query(NotificationModel)
        if status:
            query = query.filter(NotificationModel.status == status.value)
        if channel:
            query = query.filter(NotificationModel.channel == channel)
        models = query.order_by(NotificationModel.created_at.desc()).offset(offset).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def update(self, notification: Notification) -> Notification:
        model = self._session.query(NotificationModel).filter_by(id=notification.id).first()
        if not model:
            raise ValueError(f"Notificación {notification.id} no existe en DB")
        model.status = notification.status.value
        model.error_message = notification.error_message
        model.retry_count = notification.retry_count
        model.sent_at = notification.sent_at
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def count(self, status: Optional[NotificationStatus] = None) -> int:
        query = self._session.query(NotificationModel)
        if status:
            query = query.filter(NotificationModel.status == status.value)
        return query.count()

    @staticmethod
    def _to_entity(model: NotificationModel) -> Notification:
        return Notification(
            id=model.id,
            recipient=model.recipient,
            subject=model.subject,
            body=model.body,
            channel=NotificationChannel(model.channel),
            status=NotificationStatus(model.status),
            error_message=model.error_message,
            retry_count=model.retry_count,
            created_at=model.created_at,
            sent_at=model.sent_at,
        )

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.adapters.repositories.sqlite_notification_repository import (
    SQLiteNotificationRepository,
    Base,
)
from app.adapters.notifications.senders import EmailSender, SmsSender, InAppSender
from app.application.use_cases.send_notification import SendNotificationUseCase
from app.application.use_cases.get_notification_status import GetNotificationStatusUseCase
from app.application.use_cases.list_notifications import ListNotificationsUseCase
from app.application.use_cases.retry_notification import RetryNotificationUseCase

# Railway provee DATABASE_URL automáticamente al conectar PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./notifications.db")

# Railway a veces da postgres:// — SQLAlchemy necesita postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


class Container:
    """
    Contenedor de dependencias (DI manual).
    Construye y conecta adaptadores con casos de uso.
    El dominio nunca importa este archivo.
    """

    def __init__(self):
        connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
        self._engine = create_engine(DATABASE_URL, connect_args=connect_args)
        Base.metadata.create_all(bind=self._engine)
        self._SessionLocal = sessionmaker(bind=self._engine)
        self._senders = [EmailSender(), SmsSender(), InAppSender()]

    def _session(self) -> Session:
        return self._SessionLocal()

    def _repository(self) -> SQLiteNotificationRepository:
        return SQLiteNotificationRepository(self._session())

    def send_notification_use_case(self) -> SendNotificationUseCase:
        return SendNotificationUseCase(self._repository(), self._senders)

    def get_status_use_case(self) -> GetNotificationStatusUseCase:
        return GetNotificationStatusUseCase(self._repository())

    def list_notifications_use_case(self) -> ListNotificationsUseCase:
        return ListNotificationsUseCase(self._repository())

    def retry_notification_use_case(self) -> RetryNotificationUseCase:
        return RetryNotificationUseCase(self._repository(), self._senders)

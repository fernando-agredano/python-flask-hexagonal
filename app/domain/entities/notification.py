from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


@dataclass
class Notification:
    recipient: str
    subject: str
    body: str
    channel: NotificationChannel
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: NotificationStatus = NotificationStatus.PENDING
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    retry_count: int = 0

    def mark_sent(self) -> None:
        self.status = NotificationStatus.SENT
        self.sent_at = datetime.utcnow()
        self.error_message = None

    def mark_failed(self, reason: str) -> None:
        self.status = NotificationStatus.FAILED
        self.error_message = reason

    def can_retry(self, max_retries: int = 3) -> bool:
        return self.status == NotificationStatus.FAILED and self.retry_count < max_retries

    def increment_retry(self) -> None:
        self.retry_count += 1
        self.status = NotificationStatus.PENDING

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "recipient": self.recipient,
            "subject": self.subject,
            "body": self.body,
            "channel": self.channel.value,
            "status": self.status.value,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
        }

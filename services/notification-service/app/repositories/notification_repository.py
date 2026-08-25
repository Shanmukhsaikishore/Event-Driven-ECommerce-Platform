from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:

    def create(
        self,
        db: Session,
        notification: Notification,
    ) -> Notification:

        db.add(notification)
        db.flush()

        return notification

    def get_by_notification_id(
        self,
        db: Session,
        notification_id: str,
    ) -> Notification | None:

        return (
            db.query(Notification)
            .filter(
                Notification.notification_id == notification_id
            )
            .first()
        )
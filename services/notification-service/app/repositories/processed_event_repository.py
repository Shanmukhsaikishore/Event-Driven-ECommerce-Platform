from sqlalchemy.orm import Session

from app.models.processed_event import ProcessedEvent


class ProcessedEventRepository:

    def get_by_event_id(
        self,
        db: Session,
        event_id: str,
    ) -> ProcessedEvent | None:

        return (
            db.query(ProcessedEvent)
            .filter(
                ProcessedEvent.event_id == event_id
            )
            .first()
        )

    def create(
        self,
        db: Session,
        processed_event: ProcessedEvent,
    ) -> ProcessedEvent:

        db.add(processed_event)

        return processed_event
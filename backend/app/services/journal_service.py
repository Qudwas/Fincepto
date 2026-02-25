from uuid import UUID
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from app.crud.accounting import post_journal, reverse_journal


class JournalService:
    @staticmethod
    def post(db: Session, journal_id: UUID, user_id: UUID):
        return post_journal(db, journal_id, user_id)

    @staticmethod
    def reverse(db: Session, journal_id: UUID, user_id: UUID, reversal_date: date, description: str = None):
        return reverse_journal(db, journal_id, user_id, reversal_date, description)


journal_service = JournalService()

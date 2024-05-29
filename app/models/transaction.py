from sqlalchemy import Column, String, Float, Integer, DateTime, UniqueConstraint
from .user import db

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = Column(String, primary_key=True)
    uid = Column(String, unique=True)
    type = Column(String)
    amount = Column(Float)
    user_id = Column(Integer)
    timestamp = Column(DateTime)

    __table_args__ = (
        UniqueConstraint('uid', name='uq_transaction_uid'),
    )

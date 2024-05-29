from gino import Gino
from sqlalchemy import Column, Integer, String, Float

db = Gino()

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    balance = Column(Float)

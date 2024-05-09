from sqlalchemy import Column, Integer, String, TIMESTAMP, text, BLOB, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    # Define the relationship with the UserHistory table
    user_history = relationship('UserHistory', back_populates='user')

class UserHistory(Base):
    __tablename__ = 'user_history'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('User.user_id'))  # Assuming your User model has user_id
    username = Column(String(255), nullable=False)
    image_data = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    prediction_result = Column(JSON)

    # Define the relationship with the User table
    user = relationship('User', back_populates='user_history', primaryjoin='User.user_id == UserHistory.user_id')

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255))
    image_path = Column(String(255))
    feedback = Column(String(255))

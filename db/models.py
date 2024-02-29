from sqlalchemy import (
    Column, Integer, String, Enum, DateTime, Boolean, create_engine, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum

from sqlalchemy.orm import relationship

# Определение базовой модели
Base = declarative_base()


# Перечисление возможных статусов пользователя
class UserStatus(PyEnum):
    alive = "alive"
    dead = "dead"
    finished = "finished"


# Модель Message для хранения сообщений и триггеров
class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    time = Column(Integer, nullable=False)
    text = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, text={self.text[:30]})>"


# Модель User для хранения данных пользователя
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True, nullable=False)  # Добавлено для идентификации в Telegram
    created_at = Column(Integer, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.alive)
    status_updated_at = Column(Integer, nullable=True)
    schedule = Column(Integer, nullable=True)
    point_of_reference = Column(String, nullable=True, default='msg_1')

    messages = relationship("Message", back_populates="user", order_by=Message.id)

    def __repr__(self):
        return f"<User(id={self.id}, chat_id={self.chat_id}, status={self.status})>"

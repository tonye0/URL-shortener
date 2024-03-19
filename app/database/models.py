from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    __tablename__ = 'users'  # This is the name of the table in the database

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('now()')
    )

    user_url = relationship("URL", back_populates="user")


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, nullable=False)
    long_url = Column(String, nullable=False)
    short_url = Column(String, unique=True, nullable=False)
    clicks = Column(Integer, default=0)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('now()')
    )
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="user_url")
    click = relationship("Click", back_populates="url")


class Click(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('now()')
    )
    url_id = Column(Integer, ForeignKey("urls.id"))

    url = relationship("URL", back_populates="click")



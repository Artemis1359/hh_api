from app.db import Base, engine
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, MetaData
from sqlalchemy.orm import Mapped


class Tokens(Base):
    __tablename__ = "hh_tokens"

    id: Mapped[int] = Column("id", Integer, primary_key=True, nullable=False)
    access_token: Mapped[str] = Column("access_token", String(128), nullable=False)
    refresh_token: Mapped[str] = Column("refresh_token", String(128), nullable=False)
    created_at: Mapped[datetime] = Column("created_at", DateTime, default=datetime.utcnow())


class ResumeIds(Base):
    __tablename__ = "hh_resume_ids"

    id: Mapped[str] = Column("id", String(128), primary_key=True, nullable=False)
    created_at: Mapped[datetime] = Column("created_at", DateTime, default=datetime.utcnow())

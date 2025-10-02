from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
	Column,
	Integer,
	String,
	DateTime,
	Boolean,
	ForeignKey,
	UniqueConstraint,
	Index,
	Text,
)
from sqlalchemy.orm import relationship

from .database import Base


class Subject(Base):
	__tablename__ = "subjects"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String(120), unique=True, nullable=False, index=True)


class Profession(Base):
	__tablename__ = "professions"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String(120), unique=True, nullable=False, index=True)


class Character(Base):
	__tablename__ = "characters"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String(120), unique=True, nullable=False, index=True)


class Session(Base):  # user session for numbering/export
	__tablename__ = "sessions"

	id = Column(Integer, primary_key=True, index=True)
	started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
	ended_at = Column(DateTime, nullable=True)
	active = Column(Boolean, default=True, nullable=False)
	starting_serial = Column(Integer, default=1, nullable=False)
	current_serial = Column(Integer, default=1, nullable=False)

	entries = relationship("Entry", back_populates="session", cascade="all, delete-orphan")


class Entry(Base):
	__tablename__ = "entries"

	id = Column(Integer, primary_key=True, index=True)

	# categorization
	subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
	profession_id = Column(Integer, ForeignKey("professions.id"), nullable=True)
	character_id = Column(Integer, ForeignKey("characters.id"), nullable=True)

	type = Column(String(10), nullable=False)  # TEXT | QUOTE

	session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)
	puzzle_number = Column(Integer, nullable=False)

	method = Column(String(40), nullable=False)
	parameter = Column(String(200), nullable=True)

	plaintext = Column(Text, nullable=False)
	normalized_plaintext = Column(Text, nullable=False, index=True)

	ciphertext = Column(Text, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

	session = relationship("Session", back_populates="entries")
	subject = relationship("Subject")
	profession = relationship("Profession")
	character = relationship("Character")

	__table_args__ = (
		UniqueConstraint(
			"normalized_plaintext", "method", "parameter", name="uq_plain_method_param"
		),
		Index("ix_method_param", "method", "parameter"),
	)
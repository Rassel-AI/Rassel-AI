from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
	name: str = Field(min_length=1, max_length=120)


class CategoryOut(CategoryBase):
	id: int

	class Config:
		from_attributes = True


class SessionOut(BaseModel):
	id: int
	started_at: datetime
	ended_at: Optional[datetime]
	active: bool
	starting_serial: int
	current_serial: int


class SetStartingSerialIn(BaseModel):
	starting_serial: int = Field(ge=1, le=1000000)


class EncryptIn(BaseModel):
	subject: Optional[str] = None
	profession: Optional[str] = None
	character: Optional[str] = None
	type: Literal["TEXT", "QUOTE"]

	min_length: int = 1
	max_length: int = 120

	method: Literal[
		"caesar",
		"monoalpha",
		"playfair",
		"hill",
		"vigenere",
		"otp",
		"railfence",
		"rowcolumn",
	]
	parameter: Optional[str] = None

	text: str


class EncryptOut(BaseModel):
	duplicate: bool
	entry_id: Optional[int]
	ciphertext: str
	puzzle_number: Optional[int]
	puzzle_line: Optional[str]


class EntryOut(BaseModel):
	id: int
	subject: Optional[str]
	profession: Optional[str]
	character: Optional[str]
	type: str
	session_id: Optional[int]
	puzzle_number: int
	method: str
	parameter: Optional[str]
	plaintext: str
	ciphertext: str
	created_at: datetime


class SearchQuery(BaseModel):
	subject: Optional[str] = None
	profession: Optional[str] = None
	character: Optional[str] = None
	method: Optional[str] = None
	q: Optional[str] = None
	limit: int = 50
	offset: int = 0


class StatsOut(BaseModel):
	total_entries: int
	subjects: List[str]
	professions: List[str]
	characters: List[str]
from __future__ import annotations

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session as OrmSession
from sqlalchemy import select, func
from typing import Optional, List
import os

from .database import SessionLocal, engine
from .models import Base, Subject, Profession, Character, Entry, Session as DbSession
from .schemas import (
	CategoryOut,
	EncryptIn,
	EncryptOut,
	EntryOut,
	SearchQuery,
	SessionOut,
	SetStartingSerialIn,
	StatsOut,
)
from .ciphers import encrypt_dispatch, validate_dispatch
from .utils import normalize_text, validate_text_semantics, verify_quote_and_author, render_session_rtf


# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cipher Lab", description="Classical ciphers lab with session export.", version="1.0.0")

app.mount("/static", StaticFiles(directory="/workspace/app/static"), name="static")


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


# ---------- Helper functions ----------

def _get_or_create(db: OrmSession, model, name: Optional[str]):
	if not name:
		return None
	name_norm = name.strip()
	obj = db.execute(select(model).where(model.name == name_norm)).scalar_one_or_none()
	if obj:
		return obj
	obj = model(name=name_norm)
	db.add(obj)
	db.commit()
	db.refresh(obj)
	return obj


def _get_active_session(db: OrmSession) -> DbSession:
	sess = db.execute(select(DbSession).where(DbSession.active == True)).scalar_one_or_none()
	if sess:
		return sess
	sess = DbSession(active=True, starting_serial=1, current_serial=1)
	db.add(sess)
	db.commit()
	db.refresh(sess)
	return sess


# ---------- Routes ----------

@app.get("/", response_class=HTMLResponse)
async def index():
	with open("/workspace/app/static/index.html", "r", encoding="utf-8") as f:
		return HTMLResponse(f.read())


@app.get("/api/stats", response_model=StatsOut)
async def stats(db: OrmSession = Depends(get_db)):
	total = db.execute(select(func.count(Entry.id))).scalar() or 0
	subjects = [r[0] for r in db.execute(select(Subject.name)).all()]
	professions = [r[0] for r in db.execute(select(Profession.name)).all()]
	characters = [r[0] for r in db.execute(select(Character.name)).all()]
	return StatsOut(total_entries=total, subjects=subjects, professions=professions, characters=characters)


@app.post("/api/admin/category/subject", response_model=CategoryOut)
async def add_subject(name: str = Query(..., min_length=1, max_length=120), db: OrmSession = Depends(get_db)):
	existing = db.execute(select(Subject).where(Subject.name == name)).scalar_one_or_none()
	if existing:
		raise HTTPException(400, detail="Subject already exists")
	obj = Subject(name=name)
	db.add(obj)
	db.commit()
	db.refresh(obj)
	return obj


@app.post("/api/admin/category/profession", response_model=CategoryOut)
async def add_profession(name: str = Query(..., min_length=1, max_length=120), db: OrmSession = Depends(get_db)):
	existing = db.execute(select(Profession).where(Profession.name == name)).scalar_one_or_none()
	if existing:
		raise HTTPException(400, detail="Profession already exists")
	obj = Profession(name=name)
	db.add(obj)
	db.commit()
	db.refresh(obj)
	return obj


@app.post("/api/admin/category/character", response_model=CategoryOut)
async def add_character(name: str = Query(..., min_length=1, max_length=120), db: OrmSession = Depends(get_db)):
	existing = db.execute(select(Character).where(Character.name == name)).scalar_one_or_none()
	if existing:
		raise HTTPException(400, detail="Character already exists")
	obj = Character(name=name)
	db.add(obj)
	db.commit()
	db.refresh(obj)
	return obj


@app.get("/api/session", response_model=SessionOut)
async def get_session(db: OrmSession = Depends(get_db)):
	sess = _get_active_session(db)
	return SessionOut(
		id=sess.id,
		started_at=sess.started_at,
		ended_at=sess.ended_at,
		active=sess.active,
		starting_serial=sess.starting_serial,
		current_serial=sess.current_serial,
	)


@app.post("/api/session/start", response_model=SessionOut)
async def start_session(body: SetStartingSerialIn, db: OrmSession = Depends(get_db)):
	# End any existing
	db.query(DbSession).filter(DbSession.active == True).update({DbSession.active: False})
	db.commit()
	sess = DbSession(active=True, starting_serial=body.starting_serial, current_serial=body.starting_serial)
	db.add(sess)
	db.commit()
	db.refresh(sess)
	return SessionOut(
		id=sess.id,
		started_at=sess.started_at,
		ended_at=sess.ended_at,
		active=sess.active,
		starting_serial=sess.starting_serial,
		current_serial=sess.current_serial,
	)


@app.post("/api/session/end")
async def end_session(db: OrmSession = Depends(get_db)):
	sess = db.execute(select(DbSession).where(DbSession.active == True)).scalar_one_or_none()
	if not sess:
		raise HTTPException(400, detail="No active session")
	sess.active = False
	db.commit()
	return {"ok": True, "session_id": sess.id}


@app.get("/api/session/export/{session_id}")
async def export_session(session_id: int, db: OrmSession = Depends(get_db)):
	sess = db.get(DbSession, session_id)
	if not sess:
		raise HTTPException(404, detail="Session not found")
	entries = db.execute(select(Entry).where(Entry.session_id == session_id).order_by(Entry.puzzle_number)).scalars().all()
	rows = []
	for e in entries:
		rows.append({
			"ciphertext": e.ciphertext,
			"puzzle_number": e.puzzle_number,
			"plaintext": e.plaintext,
			"parameter": e.parameter or "",
		})
	rtf = render_session_rtf(rows)
	path = f"/workspace/session_{session_id}.rtf"
	with open(path, "w", encoding="utf-8") as f:
		f.write(rtf)
	return FileResponse(path, filename=f"session_{session_id}.rtf", media_type="application/rtf")


@app.post("/api/encrypt", response_model=EncryptOut)
async def encrypt(body: EncryptIn, db: OrmSession = Depends(get_db)):
	if not (body.min_length <= len(body.text) <= body.max_length):
		raise HTTPException(400, detail=f"Text length must be between {body.min_length} and {body.max_length}.")
	param = body.parameter or ""
	ok, msg = validate_dispatch(body.method, param)
	if not ok:
		raise HTTPException(400, detail=msg)
	# uniqueness check
	norm = normalize_text(body.text)
	existing = db.execute(
		select(Entry).where(
			Entry.normalized_plaintext == norm,
			Entry.method == body.method,
			Entry.parameter == param,
		)
	).scalar_one_or_none()
	if existing:
		puzzle_line = f"Puzzle {existing.puzzle_number} answer: {existing.plaintext} ({existing.parameter or ''})"
		return EncryptOut(duplicate=True, entry_id=existing.id, ciphertext=existing.ciphertext, puzzle_number=existing.puzzle_number, puzzle_line=puzzle_line)
	# validation hints
	hint = validate_text_semantics(body.text, body.type)
	if body.type == 'QUOTE':
		qerr = verify_quote_and_author(body.text)
		if qerr:
			hint = qerr
	# encrypt
	try:
		cipher = encrypt_dispatch(body.method, body.text, param)
	except Exception as e:
		raise HTTPException(400, detail=str(e))
	# get categories
	subj = _get_or_create(db, Subject, body.subject)
	prof = _get_or_create(db, Profession, body.profession)
	ch = _get_or_create(db, Character, body.character)
	# session and puzzle number
	sess = _get_active_session(db)
	pnum = sess.current_serial
	sess.current_serial = pnum + 1
	db.add(sess)
	# store entry
	entry = Entry(
		subject_id=subj.id if subj else None,
		profession_id=prof.id if prof else None,
		character_id=ch.id if ch else None,
		type=body.type,
		session_id=sess.id,
		puzzle_number=pnum,
		method=body.method,
		parameter=param,
		plaintext=body.text,
		normalized_plaintext=norm,
		ciphertext=cipher,
	)
	db.add(entry)
	try:
		db.commit()
	except Exception as e:
		db.rollback()
		raise HTTPException(400, detail="Duplicate or invalid entry.")
	db.refresh(entry)
	puzzle_line = f"Puzzle {entry.puzzle_number} answer: {entry.plaintext} ({entry.parameter or ''})"
	resp = EncryptOut(duplicate=False, entry_id=entry.id, ciphertext=entry.ciphertext, puzzle_number=entry.puzzle_number, puzzle_line=puzzle_line)
	if hint:
		return JSONResponse(content=resp.dict() | {"hint": hint})
	return resp


@app.post("/api/search", response_model=List[EntryOut])
async def search(body: SearchQuery, db: OrmSession = Depends(get_db)):
	stmt = select(Entry)
	if body.subject:
		stmt = stmt.join(Subject, isouter=True).where(Subject.name == body.subject)
	if body.profession:
		stmt = stmt.join(Profession, isouter=True).where(Profession.name == body.profession)
	if body.character:
		stmt = stmt.join(Character, isouter=True).where(Character.name == body.character)
	if body.method:
		stmt = stmt.where(Entry.method == body.method)
	if body.q:
		qnorm = f"%{normalize_text(body.q)}%"
		stmt = stmt.where(Entry.normalized_plaintext.like(qnorm))
	stmt = stmt.order_by(Entry.created_at.desc()).limit(body.limit).offset(body.offset)
	rows = db.execute(stmt).scalars().all()
	out: List[EntryOut] = []
	for e in rows:
		out.append(EntryOut(
			id=e.id,
			subject=e.subject.name if e.subject else None,
			profession=e.profession.name if e.profession else None,
			character=e.character.name if e.character else None,
			type=e.type,
			session_id=e.session_id,
			puzzle_number=e.puzzle_number,
			method=e.method,
			parameter=e.parameter,
			plaintext=e.plaintext,
			ciphertext=e.ciphertext,
			created_at=e.created_at,
		))
	return out
# Cipher Lab (Localhost)

A stylish, dark-mode FastAPI app to encrypt text/quotes using 8 classical ciphers, store/search results, manage sessions with auto-numbering, and export session outputs to RTF.

## Features
- Caesar, Monoalphabetic, Playfair, Hill (2x2/3x3), Vigenère, One-Time Pad, Rail Fence, Row-Column
- Cipher-specific parameter validation with helpful errors
- SQLite DB with uniqueness (Text/Quote + Method + Parameter)
- Categories (Subject, Profession, Character), user-selectable and searchable
- Session management with starting serial, auto-increment, and RTF export
- Responsive, modern dark UI with copy buttons

## Requirements
- Python 3.10+

## Setup
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000`.

## Usage Notes
- Set a starting serial (optional) and click End Session to close numbering.
- Download the RTF after ending a session via the Download button.
- Categories can be typed directly; they are created on encrypt if new.
- OTP requires a pad length matching the number of letters in the input.
- Hill matrix accepts 4 or 9 integers (spaces/commas/semicolons allowed). Determinant must be coprime with 26.

## Project Structure
- `app/main.py` FastAPI app and routes
- `app/models.py` SQLAlchemy models
- `app/schemas.py` Pydantic schemas
- `app/ciphers/` Cipher implementations
- `app/static/` Frontend (HTML/CSS/JS)

## Export
RTF is generated in runtime and downloaded via the browser. A copy is saved to `/workspace/session_<id>.rtf`.

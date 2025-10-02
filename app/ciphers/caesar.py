from __future__ import annotations

from typing import Tuple


def validate_caesar(parameter: str) -> Tuple[bool, str]:
	try:
		shift = int(parameter)
	except Exception:
		return False, "Shift must be an integer between 1 and 25."
	if not (1 <= shift <= 25):
		return False, "Shift must be between 1 and 25."
	return True, ""


def _shift_char(ch: str, shift: int) -> str:
	if ch.isalpha():
		base = ord('A') if ch.isupper() else ord('a')
		return chr((ord(ch) - base + shift) % 26 + base)
	return ch


def encrypt_caesar(text: str, parameter: str) -> str:
	ok, msg = validate_caesar(parameter)
	if not ok:
		raise ValueError(msg)
	shift = int(parameter)
	return ''.join(_shift_char(c, shift) for c in text)
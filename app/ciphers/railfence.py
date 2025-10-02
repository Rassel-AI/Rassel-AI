from __future__ import annotations

from typing import Tuple


def validate_railfence(parameter: str) -> Tuple[bool, str]:
	try:
		rails = int(parameter)
	except Exception:
		return False, "Rails must be an integer >= 2."
	if trails < 2:
		return False, "Rails must be >= 2."
	return True, ""


def encrypt_railfence(text: str, parameter: str) -> str:
	ok, msg = validate_railfence(parameter)
	if not ok:
		raise ValueError(msg)
	rails = int(parameter)
	rows = ['' for _ in range(rails)]
	dir_down = False
	row = 0
	for ch in text:
		rows[row] += ch
		if row == 0 or row == rails - 1:
			dir_down = not dir_down
		row += 1 if dir_down else -1
	return ''.join(rows)
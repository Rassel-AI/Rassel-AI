from __future__ import annotations

from typing import Tuple
import math


def validate_rowcolumn(parameter: str) -> Tuple[bool, str]:
	try:
		cols = int(parameter)
	except Exception:
		return False, "Columns must be an integer >= 2."
	if cols < 2:
		return False, "Columns must be >= 2."
	return True, ""


def encrypt_rowcolumn(text: str, parameter: str) -> str:
	ok, msg = validate_rowcolumn(parameter)
	if not ok:
		raise ValueError(msg)
	cols = int(parameter)
	rows = math.ceil(len(text) / cols)
	grid = [['' for _ in range(cols)] for _ in range(rows)]
	idx = 0
	for r in range(rows):
		for c in range(cols):
			if idx < len(text):
				grid[r][c] = text[idx]
				idx += 1
	cipher = []
	for c in range(cols):
		for r in range(rows):
			if grid[r][c] != '':
				cipher.append(grid[r][c])
	return ''.join(cipher)
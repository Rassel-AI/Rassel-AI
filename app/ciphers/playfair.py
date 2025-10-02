from __future__ import annotations

from typing import Tuple, List

ALPHABET = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'  # J merged into I


def validate_playfair(parameter: str) -> Tuple[bool, str]:
	key = ''.join(ch for ch in parameter.upper() if ch.isalpha()).replace('J', 'I')
	if len(key) < 1:
		return False, "Keyword must have at least 1 letter."
	return True, ""


def _build_table(keyword: str) -> List[List[str]]:
	seen = set()
	key = ''.join(ch for ch in keyword.upper() if ch.isalpha()).replace('J', 'I')
	sequence = []
	for ch in key:
		if ch not in seen and ch in ALPHABET:
			seen.add(ch)
			sequence.append(ch)
	for ch in ALPHABET:
		if ch not in seen:
			seen.add(ch)
			sequence.append(ch)
	return [sequence[i:i+5] for i in range(0, 25, 5)]


def _find_pos(table: List[List[str]], ch: str) -> Tuple[int, int]:
	for r in range(5):
		for c in range(5):
			if table[r][c] == ch:
				return r, c
	raise ValueError("Character not in table")


def _prepare_text(text: str) -> List[str]:
	letters = [ch for ch in text.upper() if ch.isalpha()]
	letters = [ 'I' if ch == 'J' else ch for ch in letters ]
	pairs = []
	i = 0
	while i < len(letters):
		a = letters[i]
		b = letters[i+1] if i+1 < len(letters) else 'X'
		if a == b:
			pairs.append(a + 'X')
			i += 1
		else:
			pairs.append(a + b)
			i += 2
	if len(pairs[-1]) == 1:
		pairs[-1] = pairs[-1] + 'X'
	return pairs


def encrypt_playfair(text: str, parameter: str) -> str:
	ok, msg = validate_playfair(parameter)
	if not ok:
		raise ValueError(msg)
	table = _build_table(parameter)
	pairs = _prepare_text(text)
	res = []
	for digraph in pairs:
		a, b = digraph[0], digraph[1]
		ra, ca = _find_pos(table, a)
		rb, cb = _find_pos(table, b)
		if ra == rb:
			res.append(table[ra][(ca+1)%5] + table[rb][(cb+1)%5])
		elif ca == cb:
			res.append(table[(ra+1)%5][ca] + table[(rb+1)%5][cb])
		else:
			res.append(table[ra][cb] + table[rb][ca])
	return ''.join(res)
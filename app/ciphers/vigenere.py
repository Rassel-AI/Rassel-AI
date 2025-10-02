from __future__ import annotations

from typing import Tuple


def validate_vigenere(parameter: str) -> Tuple[bool, str]:
	key = ''.join(ch for ch in parameter if ch.isalpha())
	if len(key) < 1:
		return False, "Keyword must contain letters."
	return True, ""


def encrypt_vigenere(text: str, parameter: str) -> str:
	ok, msg = validate_vigenere(parameter)
	if not ok:
		raise ValueError(msg)
	key = ''.join(ch for ch in parameter if ch.isalpha())
	res = []
	ki = 0
	for ch in text:
		if ch.isalpha():
			shift = (ord(key[ki % len(key)].lower()) - ord('a'))
			base = ord('A') if ch.isupper() else ord('a')
			enc = chr((ord(ch) - base + shift) % 26 + base)
			res.append(enc)
			ki += 1
		else:
			res.append(ch)
	return ''.join(res)
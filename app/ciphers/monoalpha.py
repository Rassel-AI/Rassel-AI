from __future__ import annotations

from typing import Tuple

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def validate_monoalpha(parameter: str) -> Tuple[bool, str]:
	key = parameter.upper().replace(' ', '')
	if len(key) != 26 or not key.isalpha():
		return False, "Key must be 26 unique letters."
	if len(set(key)) != 26:
		return False, "Key must contain each letter exactly once."
	return True, ""


def encrypt_monoalpha(text: str, parameter: str) -> str:
	ok, msg = validate_monoalpha(parameter)
	if not ok:
		raise ValueError(msg)
	key = parameter.upper().replace(' ', '')
	mapping = {ALPHABET[i]: key[i] for i in range(26)}
	result_chars = []
	for c in text:
		if c.isalpha():
			upper = c.upper()
			mapped = mapping[upper]
			result_chars.append(mapped if c.isupper() else mapped.lower())
		else:
			result_chars.append(c)
	return ''.join(result_chars)
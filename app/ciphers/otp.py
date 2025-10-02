from __future__ import annotations

from typing import Tuple


def validate_otp(parameter: str) -> Tuple[bool, str]:
	key = ''.join(ch for ch in parameter if ch.isalpha())
	if len(key) < 1:
		return False, "Pad must contain letters. Length must match letters in text."
	return True, ""


def encrypt_otp(text: str, parameter: str) -> str:
	key = ''.join(ch for ch in parameter if ch.isalpha())
	if len(key) < 1:
		raise ValueError("Pad must contain letters. Length must match letters in text.")
	res = []
	ki = 0
	for ch in text:
		if ch.isalpha():
			if ki >= len(key):
				raise ValueError("Pad too short. Must match number of letters in input.")
			shift = (ord(key[ki].lower()) - ord('a'))
			base = ord('A') if ch.isupper() else ord('a')
			enc = chr((ord(ch) - base + shift) % 26 + base)
			res.append(enc)
			ki += 1
		else:
			res.append(ch)
	if ki != len([c for c in text if c.isalpha()]):
		raise ValueError("Pad length mismatch.")
	return ''.join(res)
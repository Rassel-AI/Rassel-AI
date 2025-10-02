from __future__ import annotations

from typing import Tuple

from .caesar import encrypt_caesar, validate_caesar
from .monoalpha import encrypt_monoalpha, validate_monoalpha
from .playfair import encrypt_playfair, validate_playfair
from .hill import encrypt_hill, validate_hill
from .vigenere import encrypt_vigenere, validate_vigenere
from .otp import encrypt_otp, validate_otp
from .railfence import encrypt_railfence, validate_railfence
from .rowcolumn import encrypt_rowcolumn, validate_rowcolumn


def encrypt_dispatch(method: str, text: str, parameter: str) -> str:
	method = method.lower()
	if method == "caesar":
		return encrypt_caesar(text, parameter)
	if method == "monoalpha":
		return encrypt_monoalpha(text, parameter)
	if method == "playfair":
		return encrypt_playfair(text, parameter)
	if method == "hill":
		return encrypt_hill(text, parameter)
	if method == "vigenere":
		return encrypt_vigenere(text, parameter)
	if method == "otp":
		return encrypt_otp(text, parameter)
	if method == "railfence":
		return encrypt_railfence(text, parameter)
	if method == "rowcolumn":
		return encrypt_rowcolumn(text, parameter)
	raise ValueError("Unknown cipher method")


def validate_dispatch(method: str, parameter: str) -> Tuple[bool, str]:
	method = method.lower()
	if method == "caesar":
		return validate_caesar(parameter)
	if method == "monoalpha":
		return validate_monoalpha(parameter)
	if method == "playfair":
		return validate_playfair(parameter)
	if method == "hill":
		return validate_hill(parameter)
	if method == "vigenere":
		return validate_vigenere(parameter)
	if method == "otp":
		return validate_otp(parameter)
	if method == "railfence":
		return validate_railfence(parameter)
	if method == "rowcolumn":
		return validate_rowcolumn(parameter)
	return False, "Unknown cipher method"
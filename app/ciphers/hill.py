from __future__ import annotations

from typing import Tuple, List
import math

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def _parse_matrix(param: str) -> List[List[int]]:
	# Accept formats like "2x2: a,b,c,d" or just "a b c d" (4 numbers) or "a,b,c;d,e,f;g,h,i"
	s = param.replace(';', ' ').replace(',', ' ').replace('\n', ' ')
	tokens = [t for t in s.split() if t]
	nums: List[int] = []
	for t in tokens:
		if t.lower() in ("2x2", "3x3"):
			continue
		nums.append(int(t))
	if len(nums) == 4:
		return [ [nums[0], nums[1]], [nums[2], nums[3]] ]
	if len(nums) == 9:
		return [ nums[0:3], nums[3:6], nums[6:9] ]
	raise ValueError("Provide 4 (2x2) or 9 (3x3) integers for key matrix.")


def _determinant(matrix: List[List[int]]) -> int:
	n = len(matrix)
	if n == 2:
		return matrix[0][0]*matrix[1][1] - matrix[0][1]*matrix[1][0]
	elif n == 3:
		a,b,c = matrix[0]
		d,e,f = matrix[1]
		g,h,i = matrix[2]
		return a*(e*i - f*h) - b*(d*i - f*g) + c*(d*h - e*g)
	raise ValueError("Matrix must be 2x2 or 3x3")


def validate_hill(parameter: str) -> Tuple[bool, str]:
	try:
		m = _parse_matrix(parameter)
	except Exception as e:
		return False, str(e)
	det = _determinant(m) % 26
	if math.gcd(det, 26) != 1:
		return False, "Key matrix determinant must be coprime with 26."
	return True, ""


def _chunk_letters(text: str, size: int) -> List[List[int]]:
	letters = [ (ord(ch.upper()) - ord('A')) for ch in text if ch.isalpha() ]
	while len(letters) % size != 0:
		letters.append(ord('X') - ord('A'))
	chunks: List[List[int]] = []
	for i in range(0, len(letters), size):
		chunks.append(letters[i:i+size])
	return chunks


def encrypt_hill(text: str, parameter: str) -> str:
	ok, msg = validate_hill(parameter)
	if not ok:
		raise ValueError(msg)
	m = _parse_matrix(parameter)
	n = len(m)
	chunks = _chunk_letters(text, n)
	res = []
	for block in chunks:
		cipher_vals = []
		for r in range(n):
			total = 0
			for c in range(n):
				total += m[r][c] * block[c]
			cipher_vals.append(total % 26)
		for val in cipher_vals:
			res.append(chr(val + ord('A')))
	# reintegrate non-letters keeping sequence simple: we output uppercase letters only
	return ''.join(res)
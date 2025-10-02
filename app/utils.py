from __future__ import annotations

import re
from typing import Optional, List
from spellchecker import SpellChecker

spell = SpellChecker()


def normalize_text(text: str) -> str:
	return re.sub(r"\s+", " ", text.strip()).lower()


def validate_text_semantics(text: str, kind: str) -> Optional[str]:
	# Offline heuristic: spell-check for TEXT; minimal check for QUOTE.
	words = re.findall(r"[A-Za-z']+", text)
	if kind == 'TEXT':
		miss = list(spell.unknown(words))
		if len(miss) > 0 and len(words) >= 3:
			return f"Potential spelling issues: {', '.join(sorted(miss)[:8])}"
	else:
		if len(words) < 2:
			return "Quote seems too short."
	return None


def verify_quote_and_author(text: str) -> Optional[str]:
	# Stub for offline mode. In connected mode one could integrate web checks.
	if len(text.strip()) < 3:
		return "Quote too short."
	return None


def render_session_rtf(entries: List[dict]) -> str:
	# Minimal RTF with UTF-8 fallback escaped as ASCII where necessary.
	def esc(s: str) -> str:
		return s.replace('\\', r'\\').replace('{', r'\{').replace('}', r'\}')
	rtf_lines = [r"{\rtf1\ansi\deff0"]
	for e in entries:
		cipher = esc(e['ciphertext'])
		pnum = e['puzzle_number']
		plain = esc(e['plaintext'])
		param = esc(e.get('parameter') or '')
		line = f"{cipher} \line Puzzle {pnum} answer: {plain} ({param}) \par \par"
		rtf_lines.append(line)
	rtf_lines.append('}')
	return ''.join(rtf_lines)
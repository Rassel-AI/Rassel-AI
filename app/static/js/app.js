const qs = (s)=>document.querySelector(s);
const qsa = (s)=>Array.from(document.querySelectorAll(s));

const state = {
	lastCiphertext: '',
	lastPuzzleLine: '',
	session: null,
};

const hints = {
	caesar: 'Shift: integer 1-25',
	monoalpha: '26-letter key, permutation of A-Z',
	playfair: 'Keyword (letters). J merges with I',
	hill: 'Matrix: 4 or 9 integers (e.g., "2 3 1 4" or "2,3;1,4")',
	vigenere: 'Keyword letters',
	otp: 'Pad letters, exactly matches number of letters in text',
	railfence: 'Rails: integer >= 2',
	rowcolumn: 'Columns: integer >= 2',
};

function setParamHint(){
	const m = qs('#method').value;
	qs('#paramHint').innerText = hints[m] || '';
}

function toast(msg){
	const el = qs('#message');
	el.textContent = msg || '';
}

async function loadStats(){
	const r = await fetch('/api/stats');
	const j = await r.json();
	qs('#totalEntries').innerText = j.total_entries;
	populateDatalist('#subjects', j.subjects);
	populateDatalist('#professions', j.professions);
	populateDatalist('#characters', j.characters);
	qs('#subjectsCount').innerText = j.subjects.length;
	qs('#professionsCount').innerText = j.professions.length;
	qs('#charactersCount').innerText = j.characters.length;
}

function populateDatalist(id, items){
	const d = qs(id);
	d.innerHTML = '';
	items.sort().forEach(v=>{
		const opt = document.createElement('option');
		opt.value = v;
		d.appendChild(opt);
	});
}

async function ensureSession(){
	if (state.session) return state.session;
	const r = await fetch('/api/session');
	state.session = await r.json();
	return state.session;
}

async function startSession(){
	const start = parseInt(qs('#startSerial').value || '1', 10);
	const r = await fetch('/api/session/start', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({starting_serial: start})});
	state.session = await r.json();
	toast('Session started.');
	qs('#downloadBtn').disabled = true;
}

async function endSession(){
	if (!state.session) await ensureSession();
	if (!confirm('Do you want to download the session output?')){
		await fetch('/api/session/end', {method:'POST'});
		toast('Session ended.');
		qs('#downloadBtn').disabled = false;
		return;
	}
	await fetch('/api/session/end', {method:'POST'});
	qs('#downloadBtn').disabled = false;
	toast('Session ended. Use Download to get the RTF.');
}

async function downloadSession(){
	if (!state.session){ await ensureSession(); }
	const id = state.session.id;
	window.location.href = `/api/session/export/${id}`;
}

function renderOutput(ciphertext, puzzleLine){
	const out = qs('#output');
	out.innerHTML = '';
	const ct = document.createElement('div');
	ct.className = 'card';
	const h = document.createElement('div');
	h.innerHTML = `<span class="badge">Ciphertext</span> <button class="copy">Copy</button>`;
	const pre = document.createElement('pre');
	pre.textContent = ciphertext;
	ct.appendChild(h); ct.appendChild(pre);
	out.appendChild(ct);

	const pl = document.createElement('div');
	pl.className = 'card';
	pl.innerHTML = `<span class="badge">Puzzle</span> ${puzzleLine} <button class="copy">Copy</button>`;
	out.appendChild(pl);

	out.querySelectorAll('.copy').forEach(btn=>{
		btn.addEventListener('click', ()=>{
			const target = btn.parentElement.tagName === 'DIV' && btn.parentElement.nextSibling && btn.parentElement.nextSibling.tagName==='PRE'
				? btn.parentElement.nextSibling.textContent
				: btn.parentElement.textContent.replace('Copy','').trim();
			navigator.clipboard.writeText(target);
			toast('Copied to clipboard.');
		});
	});
}

async function doEncrypt(){
	await ensureSession();
	const body = {
		subject: qs('#subject').value || null,
		profession: qs('#profession').value || null,
		character: qs('#character').value || null,
		type: qsa('input[name="type"]').find(x=>x.checked).value,
		min_length: parseInt(qs('#minLen').value || '1', 10),
		max_length: parseInt(qs('#maxLen').value || '120', 10),
		method: qs('#method').value,
		parameter: qs('#parameter').value || '',
		text: qs('#text').value,
	};
	const r = await fetch('/api/encrypt', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
	if (!r.ok){
		const j = await r.json();
		toast(j.detail || 'Error');
		return;
	}
	const j = await r.json();
	state.lastCiphertext = j.ciphertext;
	state.lastPuzzleLine = j.puzzle_line;
	renderOutput(j.ciphertext, j.puzzle_line);
	toast(j.hint ? `Note: ${j.hint}` : 'Encrypted.');
}

async function doSearch(){
	const body = {
		subject: qs('#sSubject').value || null,
		profession: qs('#sProfession').value || null,
		character: qs('#sCharacter').value || null,
		method: qs('#sMethod').value || null,
		q: qs('#sQuery').value || null,
		limit: 50,
		offset: 0,
	};
	const r = await fetch('/api/search', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
	const list = await r.json();
	const res = qs('#results');
	res.innerHTML = '';
	list.forEach(e=>{
		const card = document.createElement('div');
		card.className = 'card';
		card.innerHTML = `<div><span class="badge">#${e.puzzle_number}</span> <span class="badge">${e.method}</span> <span class="badge">${e.parameter||''}</span></div>`+
		`<div><strong>Ciphertext:</strong> ${e.ciphertext}</div>`+
		`<div><strong>Answer:</strong> ${e.plaintext}</div>`+
		`<div class="muted">Subject: ${e.subject||'-'}, Profession: ${e.profession||'-'}, Character: ${e.character||'-'}</div>`;
		res.appendChild(card);
	});
}

function bind(){
	qs('#method').addEventListener('change', setParamHint);
	qs('#encryptBtn').addEventListener('click', doEncrypt);
	qs('#nextBtn').addEventListener('click', ()=>{
		qs('#text').value = '';
		qs('#text').focus();
		toast('Enter next input.');
	});
	qs('#endBtn').addEventListener('click', endSession);
	qs('#downloadBtn').addEventListener('click', downloadSession);
	qs('#searchBtn').addEventListener('click', doSearch);
	setParamHint();
}

(async function init(){
	await loadStats();
	await ensureSession();
	bind();
})();
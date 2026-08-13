import os
import json
from pathlib import Path

#input_folder_1 = Path("Data/Spanish_ALL/Corpus_associative")
input_folder_2 = Path("Data/Spanish_ALL/Corpus_lexical")
input_folder_3 = Path("Data/Spanish_FID/Gold_standard")

def collect_subjects(folder: Path):
	subjects = set()
	if not folder.exists():
		return subjects
	for root, _, files in os.walk(folder):
		for fname in files:
			if not fname.lower().endswith('.json'):
				continue
			fpath = Path(root) / fname
			try:
				with open(fpath, 'r', encoding='utf-8') as fh:
					data = json.load(fh)
			except Exception:
				continue
			# subjects may be under key 'subjects'
			subs = data.get('subjects') if isinstance(data, dict) else None
			if not subs:
				continue
			for s in subs:
				# prefer uri if present, else label
				if isinstance(s, dict):
					key = s.get('uri') or s.get('label')
				else:
					key = str(s)
				if key:
					subjects.add(key)
	return subjects

def main():
	sets = []
	for folder in (input_folder_2, input_folder_3):
		sets.append((folder, collect_subjects(folder)))

	all_subjects = set().union(*(s for _, s in sets))

	for folder, sset in sets:
		print(f"{folder}: {len(sset)} different subjects")
	print(f"ALL FOLDERS: {len(all_subjects)} different subjects")

if __name__ == '__main__':
	main()
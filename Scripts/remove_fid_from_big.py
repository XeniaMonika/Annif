import json
from pathlib import Path

corpus_big_path = Path(r"C:\Users\kudelamo\Projects\Annif\Data\Spanish_ALL\corpus.jsonl")
corpus_small_path = Path(r"C:\Users\kudelamo\Projects\Annif\Data\Spanish_FID\corpus.jsonl")


def load_corpus(path):
	"""Return dict: text -> set of subject URIs."""
	mapping = {}
	with path.open("r", encoding="utf-8") as fh:
		for line in fh:
			line = line.strip()
			if not line:
				continue
			try:
				obj = json.loads(line)
			except json.JSONDecodeError:
				continue
			text = obj.get("text")
			if text is None:
				continue
			subjects = obj.get("subjects") or []
			uris = {s.get("uri") for s in subjects if isinstance(s, dict) and s.get("uri")}
			# if text appears multiple times, union subject sets
			mapping.setdefault(text, set()).update(uris)
	return mapping


def compare(big_map, small_map):
	texts_both = set(big_map.keys()) & set(small_map.keys())
	same_text_count = len(texts_both)

	same_text_same_subjects = [t for t in texts_both if big_map[t] == small_map[t]]
	same_text_diff_subjects = [t for t in texts_both if big_map[t] != small_map[t]]

	print(f"Texts in both files: {same_text_count}")
	print(f"Same text and same subjects: {len(same_text_same_subjects)}")
	print(f"Same text but different subjects: {len(same_text_diff_subjects)}")

	# show a few examples of differences
	if same_text_diff_subjects:
		print("\nExamples of same text with different subjects:")
		for t in same_text_diff_subjects[:10]:
			print("TEXT:", t)
			print("  big subjects:", sorted(big_map[t]) )
			print("  small subjects:", sorted(small_map[t]) )


if __name__ == "__main__":
	big = load_corpus(corpus_big_path)
	small = load_corpus(corpus_small_path)
	compare(big, small)

	def remove_texts_from_big(big_path, small_map):
		"""Remove any entries from the big corpus whose text appears in small_map.
		Overwrite the big corpus file with the remaining entries and return count.
		"""
		kept = []
		with big_path.open("r", encoding="utf-8") as fh:
			for line in fh:
				line = line.strip()
				if not line:
					continue
				try:
					obj = json.loads(line)
				except json.JSONDecodeError:
					continue
				text = obj.get("text")
				if text is None:
					continue
				if text in small_map:
					continue
				kept.append(line)
		# overwrite file
		with big_path.open("w", encoding="utf-8") as fh:
			for line in kept:
				fh.write(line + "\n")
		return len(kept)

	# remove overlaps and save big corpus
	remaining = remove_texts_from_big(corpus_big_path, small)
	print(f"Entries left in big corpus: {remaining}")

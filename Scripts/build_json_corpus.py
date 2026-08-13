import os
import json

input_corpus_path = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_FID\\corpus.jsonl"
mapped_keywords_path = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Vocabs\\keywords_mapped_both.json"
output_folder_big = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_FID\\Gold_standard"



def convert_corpus_to_json_files(corpus_path, mapped_keywords_path, output_folder):
	os.makedirs(output_folder, exist_ok=True)

	# load mapping into dict by id (e.g. 'gnd/4077640-2') -> spa_label
	with open(mapped_keywords_path, 'r', encoding='utf-8') as f:
		mappings = json.load(f)
	id_to_label = {m.get('id', ''): m.get('spa_label', '') for m in mappings}

	def extract_gnd_id(uri):
		if not uri:
			return ''
		if 'gnd/' in uri:
			return 'gnd/' + uri.split('gnd/')[1]
		return uri

	with open(corpus_path, 'r', encoding='utf-8') as f:
		for i, line in enumerate(f, start=1):
			line = line.strip()
			if not line:
				continue
			try:
				entry = json.loads(line)
			except Exception:
				continue

			filename = f"entry_{i}.json"
			doc_id = f"entry_{i}"

			title_text = entry.get('text', '')

			subjects_out = []
			for s in entry.get('subjects', []):
				uri = s.get('uri', '')
				gnd_id = extract_gnd_id(uri)
				label = id_to_label.get(gnd_id, '')
				subjects_out.append({'uri': uri, 'label': label})

			out = {
				'document_id': doc_id,
				'text': '',
				'metadata': {
					'title': title_text,
					'author': ''
				},
				'subjects': subjects_out
			}

			out_path = os.path.join(output_folder, filename)
			with open(out_path, 'w', encoding='utf-8') as outf:
				json.dump(out, outf, ensure_ascii=False, indent=2)


if __name__ == '__main__':
	# generate for both corpora
	convert_corpus_to_json_files(input_corpus_path, mapped_keywords_path, output_folder_big)
	

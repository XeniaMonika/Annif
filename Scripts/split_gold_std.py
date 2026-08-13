

import json
import random

input_file = r"C:\Users\kudelamo\Projects\Annif\Data\Spanish_FID\corpus.jsonl"
output_validation_file = r"C:\Users\kudelamo\Projects\Annif\Data\Spanish_FID\corpus_validation.jsonl"
output_test_file = r"C:\Users\kudelamo\Projects\Annif\Data\Spanish_FID\corpus_test.jsonl"

# Desired sizes
VALIDATION_SIZE = 6146
TEST_SIZE = 12292

def main(seed=42):
	random.seed(seed)
	with open(input_file, 'r', encoding='utf-8') as f:
		lines = [line.rstrip('\n') for line in f if line.strip()]

	total = len(lines)
	required = VALIDATION_SIZE + TEST_SIZE
	if total < required:
		raise SystemExit(f"Input has {total} records but {required} required")

	# Shuffle for random split but reproducible
	indices = list(range(total))
	random.shuffle(indices)

	val_idx = set(indices[:VALIDATION_SIZE])
	test_idx = set(indices[VALIDATION_SIZE:VALIDATION_SIZE+TEST_SIZE])

	with open(output_validation_file, 'w', encoding='utf-8') as vf, \
		 open(output_test_file, 'w', encoding='utf-8') as tf:
		for i, line in enumerate(lines):
			if i in val_idx:
				vf.write(line + '\n')
			elif i in test_idx:
				tf.write(line + '\n')

if __name__ == '__main__':
	main()


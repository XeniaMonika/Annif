import os
import json
import random
from pathlib import Path

input_folder = r"C:\Users\kudelamo\Projects\Annif\Data\Spanish_FID\Gold_standard"
output_validation_folder = r"C:\Users\kudelamo\Projects\Annif\Data\Spanish_FID\Validation"
output_test_folder = r"C:\Users\kudelamo\Projects\Annif\Data\Spanish_FID\Test"

# Create output folders if they don't exist
Path(output_validation_folder).mkdir(parents=True, exist_ok=True)
Path(output_test_folder).mkdir(parents=True, exist_ok=True)

# Get all JSON files from input folder
json_files = [f for f in os.listdir(input_folder) if f.endswith('.json')]
print(f"Total JSON files found: {len(json_files)}")

# Shuffle files randomly
random.shuffle(json_files)

# Split: 6,146 for validation, 12,292 for test
validation_count = 6146
test_count = 12292

validation_files = json_files[:validation_count]
test_files = json_files[validation_count:validation_count + test_count]

# Copy validation files
for idx, filename in enumerate(validation_files, 1):
    src = os.path.join(input_folder, filename)
    # Rename files to entry_1.json, entry_2.json, ... when saving
    new_name = f"entry_{idx}.json"
    dst = os.path.join(output_validation_folder, new_name)
    with open(src, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    if idx % 1000 == 0:
        print(f"Copied {idx} validation files...")

print(f"Validation set: {len(validation_files)} files saved to {output_validation_folder}")

# Copy test files
for idx, filename in enumerate(test_files, 1):
    src = os.path.join(input_folder, filename)
    # Rename files to entry_1.json, entry_2.json, ... when saving
    new_name = f"entry_{idx}.json"
    dst = os.path.join(output_test_folder, new_name)
    with open(src, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    if idx % 1000 == 0:
        print(f"Copied {idx} test files...")

print(f"Test set: {len(test_files)} files saved to {output_test_folder}")
print("Split completed successfully!")

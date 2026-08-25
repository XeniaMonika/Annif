import deepl
import json
import os

# --- Config ---
auth_key = ""  
input_path = "./Data/Vocabs/keywords_untranslated.json"       
output_path = "./Data/Vocabs/keywords_translated_deepl.json"     
batch_size = 50  

translator = deepl.Translator(auth_key)

# --- Load input terms ---
with open(input_path, "r", encoding="utf-8") as f:
    terms = json.load(f)  # {id: german_term}

ids = list(terms.keys())

# --- Load existing progress, if any (resume support) ---
if os.path.exists(output_path):
    with open(output_path, "r", encoding="utf-8") as f:
        results = json.load(f)
    print(f"Resuming: {len(results)} terms already translated.")
else:
    results = {}

# Skip IDs already translated
remaining_ids = [i for i in ids if i not in results]
print(f"{len(remaining_ids)} terms left to translate out of {len(ids)} total.")

# --- Translate in batches ---
for batch_start in range(0, len(remaining_ids), batch_size):
    batch_ids = remaining_ids[batch_start:batch_start + batch_size]
    batch_terms = [terms[i] for i in batch_ids]

    batch_num = batch_start // batch_size + 1
    print(f"Translating batch {batch_num} ({len(batch_ids)} terms)...")

    try:
        translations = translator.translate_text(
            batch_terms, source_lang="DE", target_lang="ES"
        )
    except deepl.DeepLException as e:
        print(f"Error on batch {batch_num}: {e}")
        print("Stopping here — progress so far is saved. Re-run the script to resume.")
        break

    for id_, translation in zip(batch_ids, translations):
        results[id_] = translation.text

    # --- Checkpoint: save after every batch ---
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Batch {batch_num} done. {len(results)}/{len(ids)} total translated. Progress saved.")

print(f"Finished. {len(results)}/{len(ids)} terms translated.")
import csv
import json
import re
import time
from pathlib import Path

from openai import OpenAI


# ============================================================
# CONFIGURATION
# ============================================================

input_file = "./Data/Vocabs/vocabs.csv"


OPENAI_API_KEY = ""

mapping_file = "./Data/Vocabs/vocabs_uri_es.json"

MODEL = "gpt-5.6-luna"
BATCH_SIZE = 50
MAX_RETRIES = 5
RETRY_DELAY = 5


client = OpenAI(api_key=OPENAI_API_KEY)


def clean_german_label(label: str) -> str:
    """
    Remove trailing angle-bracket qualifiers such as <Motiv>.
    """
    if label is None:
        return ""

    return re.sub(r"\s*<[^<>]*>\s*", " ", label).strip()

def translate_batch(batch):
    """
    Translate one batch of German labels.

    batch is a list of dictionaries:

        [
            {"id": 0, "text": "Warenkorb"},
            {"id": 1, "text": "Benutzerkonto"},
            ...
        ]

    Returns:

        {
            id: Spanish translation,
            ...
        }

    Example:

        {
            0: "Carrito de compra",
            1: "Cuenta de usuario"
        }
    """

    if not batch:
        return {}

    numbered_labels = "\n".join(
        f"{item['id']}: {item['text']}"
        for item in batch
    )

    expected_ids = {item["id"] for item in batch}

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            print(
                f"    API request: {len(batch)} labels "
                f"(attempt {attempt}/{MAX_RETRIES})"
            )

            response = client.responses.create(
                model=MODEL,

                reasoning={
                    "effort": "none"
                },

                instructions="""
You are a professional German-to-Spanish translator.

Translate German labels into natural, concise Spanish.

VERY IMPORTANT:
- You MUST return exactly one translation for every input ID.
- You MUST preserve every ID exactly.
- Never omit an ID.
- Never create a new ID.
- Never return the same ID twice.
- Translate the text associated with each ID.
- Do not combine multiple labels.
- Do not split one label into multiple translations.
- Do not add explanations.
- Do not add quotation marks around translations.
- Do not invent information.
- Keep product names, brand names, abbreviations and technical terms
  unchanged when appropriate.
- Preserve numbers and meaningful symbols where appropriate.
- The translation should be suitable as a short label in a vocabulary,
  catalogue, database, or user interface.
""",

                input=numbered_labels,

                text={
                    "format": {
                        "type": "json_schema",
                        "name": "translations",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "translations": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {
                                                "type": "integer"
                                            },
                                            "translation": {
                                                "type": "string"
                                            }
                                        },
                                        "required": [
                                            "id",
                                            "translation"
                                        ],
                                        "additionalProperties": False
                                    }
                                }
                            },
                            "required": [
                                "translations"
                            ],
                            "additionalProperties": False
                        }
                    }
                }
            )

            result = json.loads(response.output_text)

            translations = result.get("translations", [])

            # ------------------------------------------------
            # Validate the response
            # ------------------------------------------------

            received_ids = [
                item["id"]
                for item in translations
            ]

            received_id_set = set(received_ids)

            # Check for duplicate IDs.
            if len(received_ids) != len(received_id_set):
                print(
                    "    WARNING: API returned duplicate IDs."
                )
                raise ValueError(
                    "Duplicate IDs returned by API."
                )

            # Check for missing IDs.
            missing_ids = expected_ids - received_id_set

            if missing_ids:
                print(
                    f"    WARNING: API omitted "
                    f"{len(missing_ids)} IDs: "
                    f"{sorted(missing_ids)}"
                )

                raise ValueError(
                    f"Missing IDs: {sorted(missing_ids)}"
                )

            # Check for unexpected IDs.
            unexpected_ids = received_id_set - expected_ids

            if unexpected_ids:
                print(
                    f"    WARNING: API returned unexpected IDs: "
                    f"{sorted(unexpected_ids)}"
                )

                raise ValueError(
                    f"Unexpected IDs: {sorted(unexpected_ids)}"
                )

            # Check exact count.
            if len(translations) != len(batch):
                raise ValueError(
                    f"Expected {len(batch)} translations, "
                    f"received {len(translations)}."
                )

            # Build ID -> translation mapping.
            result_mapping = {}

            for item in translations:

                translation = (
                    item["translation"]
                    .strip()
                )

                if not translation:
                    raise ValueError(
                        f"Empty translation for ID {item['id']}"
                    )

                result_mapping[item["id"]] = translation

            print(
                f"    Successfully received "
                f"{len(result_mapping)} translations."
            )

            return result_mapping

        except Exception as exc:

            print(
                f"    API attempt failed: {exc}"
            )

            if attempt < MAX_RETRIES:

                wait_time = RETRY_DELAY * attempt

                print(
                    f"    Waiting {wait_time} seconds "
                    f"before retry..."
                )

                time.sleep(wait_time)

            else:

                print(
                    "    Maximum retries reached."
                )

    return None


# ============================================================
# INDIVIDUAL FALLBACK
# ============================================================

def translate_individually(batch):
    """
    If a complete batch repeatedly fails validation,
    translate each label individually.

    This is slower but extremely reliable.
    """

    print(
        f"    Falling back to individual translation "
        f"for {len(batch)} labels..."
    )

    translations = {}

    for number, item in enumerate(batch, start=1):

        print(
            f"      Individual label "
            f"{number}/{len(batch)}: "
            f"{item['text']}"
        )

        result = translate_batch([item])

        if result is None:
            raise RuntimeError(
                f"Could not translate label ID "
                f"{item['id']}: {item['text']}"
            )

        translations.update(result)

    return translations


# ============================================================
# SAVE CSV
# ============================================================

def save_csv(path: Path, fieldnames, rows):
    """
    Save the current CSV state.
    """

    temp_path = path.with_suffix(".tmp")

    with temp_path.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    # Replace the original only after the temporary file
    # has been written successfully.
    temp_path.replace(path)


# ============================================================
# SAVE MAPPING
# ============================================================

def save_mapping(mapping_path: Path, mapping: dict):
    """
    Persist the current URI-to-label mapping to disk.
    """

    mapping_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temp_path = mapping_path.with_suffix(".tmp")

    with temp_path.open(
        "w",
        encoding="utf-8"
    ) as fh:

        json.dump(
            mapping,
            fh,
            ensure_ascii=False,
            indent=2
        )

        fh.write("\n")

    temp_path.replace(mapping_path)


# ============================================================
# MAIN
# ============================================================

def main():

    path = Path(input_file)
    mapping_path = Path(mapping_file)

    # --------------------------------------------------------
    # Load existing mapping
    # --------------------------------------------------------

    mapping = {}

    if mapping_path.exists():

        try:

            with mapping_path.open(
                "r",
                encoding="utf-8"
            ) as fh:

                loaded = json.load(fh)

            if isinstance(loaded, dict):
                mapping = loaded

        except (
            json.JSONDecodeError,
            OSError
        ):

            print(
                "WARNING: Could not load existing mapping. "
                "Starting with an empty mapping."
            )

    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        fieldnames = reader.fieldnames or []

        rows = list(reader)

    if (
        "label_de" not in fieldnames
        or "label_es" not in fieldnames
    ):
        raise ValueError(
            "The CSV must contain "
            "'label_de' and 'label_es' columns."
        )

    # --------------------------------------------------------
    # Find missing labels
    # --------------------------------------------------------

    missing = []

    for row_index, row in enumerate(rows):

        existing_es = (
            row.get("label_es") or ""
        ).strip()

        # Already translated -> skip it.
        if existing_es:
            continue

        german = row.get("label_de", "")

        cleaned = clean_german_label(german)

        if cleaned:

            missing.append(
                {
                    "row_index": row_index,
                    "text": cleaned
                }
            )

    print()
    print("=" * 60)
    print(
        f"Missing Spanish labels: {len(missing)}"
    )
    print(
        f"Batch size: {BATCH_SIZE}"
    )
    print(
        f"Model: {MODEL}"
    )
    print("=" * 60)
    print()

    if not missing:

        print(
            "No missing Spanish labels found."
        )

        return

    # --------------------------------------------------------
    # Deduplicate
    # --------------------------------------------------------

    # Map German text -> list of row indices.
    #
    # If "Warenkorb" appears 100 times, only ask GPT
    # to translate "Warenkorb" once.

    unique_labels = {}

    for item in missing:

        text = item["text"]

        if text not in unique_labels:
            unique_labels[text] = []

        unique_labels[text].append(
            item["row_index"]
        )

    print(
        f"Unique German labels: "
        f"{len(unique_labels)}"
    )

    duplicates_saved = (
        len(missing) - len(unique_labels)
    )

    print(
        f"Duplicate translations avoided: "
        f"{duplicates_saved}"
    )

    print()

    # --------------------------------------------------------
    # Build list of unique labels
    # --------------------------------------------------------

    unique_items = []

    for index, text in enumerate(
        unique_labels.keys()
    ):

        unique_items.append(
            {
                "id": index,
                "text": text
            }
        )

    # --------------------------------------------------------
    # Translation loop
    # --------------------------------------------------------

    translations_by_text = {}

    total_unique = len(unique_items)

    for start in range(
        0,
        total_unique,
        BATCH_SIZE
    ):

        batch = unique_items[
            start:start + BATCH_SIZE
        ]

        end = start + len(batch)

        print()
        print(
            "=" * 60
        )

        print(
            f"Translating unique labels "
            f"{start + 1}-{end} "
            f"of {total_unique}"
        )

        print(
            "=" * 60
        )

        # ----------------------------------------------------
        # Try complete batch
        # ----------------------------------------------------

        batch_result = translate_batch(batch)

        # ----------------------------------------------------
        # If batch fails, translate individually
        # ----------------------------------------------------

        if batch_result is None:

            print()
            print(
                "WARNING: Batch could not be translated "
                "after retries."
            )

            batch_result = translate_individually(
                batch
            )

        # ----------------------------------------------------
        # Convert ID results to German-text results
        # ----------------------------------------------------

        for item in batch:

            item_id = item["id"]

            german_text = item["text"]

            spanish_text = batch_result[item_id]

            translations_by_text[
                german_text
            ] = spanish_text

        # ----------------------------------------------------
        # Update CSV rows
        # ----------------------------------------------------

        rows_updated = 0

        for text, row_indices in unique_labels.items():

            if text not in translations_by_text:
                continue

            spanish = translations_by_text[text]

            for row_index in row_indices:

                row = rows[row_index]

                # Only update rows that are still empty.
                if not (
                    row.get("label_es") or ""
                ).strip():

                    row["label_es"] = spanish

                    rows_updated += 1

                    # Update URI mapping.
                    uri = (
                        row.get("uri")
                        or row.get("URI")
                        or row.get("Uri")
                        or ""
                    ).strip()

                    if uri:
                        mapping[uri] = spanish

        # ----------------------------------------------------
        # CHECKPOINT
        # ----------------------------------------------------

        print()
        print(
            f"Saving checkpoint..."
        )

        save_csv(
            path,
            fieldnames,
            rows
        )

        save_mapping(
            mapping_path,
            mapping
        )

        print(
            f"Checkpoint saved. "
            f"Updated {rows_updated} CSV rows."
        )

        print(
            f"Progress: "
            f"{end}/{total_unique} unique labels."
        )

    # --------------------------------------------------------
    # Final statistics
    # --------------------------------------------------------

    remaining = 0

    for row in rows:

        if not (
            row.get("label_es") or ""
        ).strip():

            german = clean_german_label(
                row.get("label_de", "")
            )

            if german:
                remaining += 1

    print()
    print("=" * 60)
    print("TRANSLATION COMPLETE")
    print("=" * 60)

    print(
        f"Originally missing: {len(missing)}"
    )

    print(
        f"Unique German labels: {total_unique}"
    )

    print(
        f"Duplicate translations avoided: "
        f"{duplicates_saved}"
    )

    print(
        f"Remaining untranslated labels: "
        f"{remaining}"
    )

    print()
    print(
        f"CSV: {path}"
    )

    print(
        f"Mapping: {mapping_path}"
    )

    print("=" * 60)



if __name__ == "__main__":
    main()
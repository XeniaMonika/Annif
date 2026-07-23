import json

input_file = "./Data/Vocabs/keywords_mapped_both.json"
output_file = "./Data/Vocabs/keywords_untranslated.json"

def main():
    with open(input_file, encoding="utf-8") as f:
        keywords = json.load(f)

    untranslated = {
        item["id"]: item["keyword"]
        for item in keywords
        if not item.get("spa_label")
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(untranslated, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
import json

corpus_big_path = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_ALL\\corpus.jsonl"
corpus_small_path = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_FID\\corpus.jsonl"
out_big = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_ALL\\corpus_above_25.jsonl"
out_small = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_FID\\corpus_above_25.jsonl"

def filter_corpus(path, output_path):
    entries = []
    removed = 0

    with open(path, "r", encoding="utf-8") as src:
        for line in src:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            text = record.get("text", "")
            if len(text) < 25:
                removed += 1
            else:
                entries.append(record)

    before = removed + len(entries)

    with open(output_path, "w", encoding="utf-8") as out:
        for record in entries:
            out.write(json.dumps(record, ensure_ascii=False) + "\n")

    return before, removed, len(entries)


def main():
    for path, output_path in [(corpus_big_path, out_big), (corpus_small_path, out_small)]:
        before, removed, left = filter_corpus(path, output_path)
        print(f"{path}: before={before}, removed={removed}, left={left}")


if __name__ == "__main__":
    main()

import json
import csv

input_file_data = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Vocabs\\keywords_mapped_both.json"
input_file_gnd = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Vocabs\\sachbegriffe.csv"
output_file = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Vocabs\\vocabs_ready.csv"


def normalize_gnd_uri(value):
    value = (value or "").strip()
    if not value:
        return ""

    if value.startswith("https://d-nb.info/"):
        return value
    if value.startswith("http://d-nb.info/"):
        return "https://d-nb.info/" + value.replace("http://d-nb.info/", "", 1)
    if value.startswith("/"):
        value = value.lstrip("/")
    if value.startswith("gnd/"):
        return "https://d-nb.info/" + value
    return "https://d-nb.info/gnd/" + value


def main():
    with open(input_file_data, "r", encoding="utf-8") as f:
        data_rows = json.load(f)

    existing_rows = []
    row_by_uri = {}

    with open(input_file_gnd, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row:
                continue
            uri = (row.get("uri") or "").strip()
            if uri:
                row_by_uri[uri] = row
            existing_rows.append(row)

    for item in data_rows:
        uri = normalize_gnd_uri(item.get("id"))
        if not uri:
            continue

        keyword = (item.get("keyword") or "").strip()
        spa_label = (item.get("spa_label") or "").strip()

        if uri not in row_by_uri:
            row_by_uri[uri] = {
                "uri": uri,
                "label_de": keyword,
                "label_es": spa_label,
                "notation": "",
            }
            existing_rows.append(row_by_uri[uri])
        else:
            row = row_by_uri[uri]
            if keyword and not row.get("label_de"):
                row["label_de"] = keyword
            if spa_label:
                row["label_es"] = spa_label

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["uri", "label_de", "label_es"], extrasaction="ignore")
        writer.writeheader()
        for row in existing_rows:
            output_row = {
                "uri": (row.get("uri") or "").strip(),
                "label_de": (row.get("label_de") or "").strip(),
                "label_es": (row.get("label_es") or "").strip(),
            }
            writer.writerow(output_row)


if __name__ == "__main__":
    main()


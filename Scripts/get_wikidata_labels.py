import requests
import json

qids_path = "./Data/Vocabs/gnd_wikidata_links.json"
output_path = "./Data/Vocabs/wikidata_spanish_labels.json"

headers = {"User-Agent": "AnnifSubjectIndexing/1.0 (monika.kudela@sub.uni-hamburg.de)"}


with open(qids_path, "r", encoding="utf-8") as f:
    qids = [link["qid"] for link in json.load(f).values()]

def fetch_spanish_labels(qids, batch_size=50):
    """qids: list of Wikidata Q-IDs (without the Q prefix stripped).
    Returns {qid: {"label": str, "aliases": [str, ...]}}"""
    results = {}
    for i in range(0, len(qids), batch_size):
        batch = qids[i:i + batch_size]
        #print(batch)
        resp = requests.get(
            "https://www.wikidata.org/w/api.php",
            params={
                "action": "wbgetentities",
                "ids": "|".join(batch),
                "props": "labels|aliases",
                "languages": "es",
                "format": "json",
            },
            headers=headers,
        )
        print(f"Fetched batch {i // batch_size + 1}: {resp.status_code}")
        data = resp.json().get("entities", {})
        print(f"Data received for batch {i // batch_size + 1}: {len(data)} entities")
        for qid, entity in data.items():
            label = entity.get("labels", {}).get("es", {}).get("value", "")
            aliases = [a["value"] for a in entity.get("aliases", {}).get("es", [])]
            results[qid] = {"label": label, "aliases": aliases}
    return results

spanish_labels = fetch_spanish_labels(qids)
print(f"Fetched Spanish labels for {len(spanish_labels)} Q-IDs.")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(spanish_labels, f, ensure_ascii=False, indent=2)
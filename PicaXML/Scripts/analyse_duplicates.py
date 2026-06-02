import json

dataset_1 = "C:\\Users\\kudelamo\\Projects\\Annif\\PicaXML\\Data\\Spanish\\duplicates_author_title_isbn.json"
dataset_2 = "C:\\Users\\kudelamo\\Projects\\Annif\\PicaXML\\Data\\Spanish\\duplicates_author_title.json"


# Comapre th length of the isbn files fpr pica and marc
def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
try:
    dataset_1_data = load_json(dataset_1)
    dataset_2_data = load_json(dataset_2)
except Exception as e:
    print(f"Error loading files: {e}")
    raise

marc_len = len(dataset_1_data) if hasattr(dataset_1_data, "__len__") else 0
pica_len = len(dataset_2_data) if hasattr(dataset_2_data, "__len__") else 0

print(f"Marc document length: {marc_len}")
print(f"Pica document length: {pica_len}")
print(f"Difference: {abs(marc_len - pica_len)}")


# Compare the titles and prinz how many title are the same and how many are different

def extract_titles(data):
    titles = []
    if isinstance(data, dict):
        data_iter = data.values()
    elif isinstance(data, list):
        data_iter = data
    else:
        return titles

    for item in data_iter:
        if isinstance(item, dict):
            for key in ("title", "title_full", "main_title", "titel", "titel_full"):
                if key in item:
                    titles.append(item[key])
                    break
        elif isinstance(item, str):
            titles.append(item)

    return [t.strip() for t in titles if isinstance(t, str) and t.strip()]

marc_titles = set(extract_titles(dataset_1_data))
pica_titles = set(extract_titles(dataset_2_data))

same_titles = marc_titles & pica_titles
all_titles = marc_titles | pica_titles
ten_first_same_titles = list(same_titles)[:10]


different_titles = all_titles - same_titles

print(f"Same titles: {len(same_titles)}")
print(f"Different titles: {len(different_titles)}")
print(f"First 10 same titles: {ten_first_same_titles}")

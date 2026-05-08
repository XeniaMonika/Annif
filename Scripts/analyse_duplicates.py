import json

INPUT_FILE = "./Data/Spanish/duplicates_author_title_isbn.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    duplicates = json.load(f)

print("Analyzing duplicates with different keyword sets...\n")

groups_with_different_keywords = 0
total_groups = len(duplicates)
isbns_with_different_keywords = []

for group in duplicates:
    author = group["author"]
    title = group["title"]
    isbn = group["isbn"]
    records = group["records"]
    
    # Extract keyword sets from all records
    keyword_sets = [tuple(sorted(rec["keywords"])) for rec in records]
    
    # Check if all keyword sets are identical
    if len(set(keyword_sets)) > 1:
        groups_with_different_keywords += 1
        isbns_with_different_keywords.append(isbn)
        print(f"DIFFERENT KEYWORDS: {author} - {title}")
        for i, rec in enumerate(records):
            print(f"  Record {i+1} (id: {rec['id']}):")
            print(f"    Keywords: {rec['keywords']}")
        print()

print(f"Total duplicate groups: {total_groups}")
print(f"Groups with different keyword sets: {groups_with_different_keywords}")
print(f"Groups with identical keyword sets: {total_groups - groups_with_different_keywords}")
print(f"\nISBNs with different keyword sets:")
for isbn in isbns_with_different_keywords:
    print(f"  {isbn}")

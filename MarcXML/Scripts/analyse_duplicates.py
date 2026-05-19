import json


#Find duplicate groups with different keyword sets in the file with same isbns
'''

INPUT_FILE = "./Data/Spanish/duplicates_author_title_isbn.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    duplicates = json.load(f)

print("Analyzing duplicates with different keyword sets...\n")

groups_with_different_keywords = 0
total_groups = len(duplicates)
isbns_with_different_keywords = []
same_id_groups = 0
isbns_with_same_ids = []

for group in duplicates:
    author = group["author"]
    title = group["title"]
    isbn = group["isbn"]
    records = group["records"]
    
    # Extract keyword sets from all records
    keyword_sets = [tuple(sorted(rec["keywords"])) for rec in records]
    ids = [rec["id"] for rec in records]
    
    print(keyword_sets)
    # Check if all keyword sets are identical
    if len(set(keyword_sets)) > 1:
        groups_with_different_keywords += 1
        isbns_with_different_keywords.append(isbn)
        print(f"DIFFERENT KEYWORDS: {author} - {title}")
        for i, rec in enumerate(records):
            print(f"  Record {i+1} (id: {rec['id']}):")
            print(f"    Keywords: {rec['keywords']}")
        print()

    # Check if any record IDs are repeated within the group
    if len(set(ids)) < len(ids):
        same_id_groups += 1
        isbns_with_same_ids.append(isbn)
        print(f"SAME IDS: {author} - {title}")
        for i, rec in enumerate(records):
            print(f"  Record {i+1} (id: {rec['id']})")
        print()

print(f"Total duplicate groups: {total_groups}")
print(f"Groups with different keyword sets: {groups_with_different_keywords}")
print(f"Groups with identical keyword sets: {total_groups - groups_with_different_keywords}")
print(f"Groups with same ids: {same_id_groups}")
print(f"\nISBNs with different keyword sets:")
for isbn in isbns_with_different_keywords:
    print(f"  {isbn}")

print(f"\nISBNs with same ids:")
for isbn in isbns_with_same_ids:
    print(f"  {isbn}")
'''


#Find duplicate groups with different keyword sets in the file without isbns

INPUT_FILE = "./Data/Spanish/duplicates_author_title.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    duplicates = json.load(f)

print("Analyzing duplicates with different keyword sets...\n")

groups_with_different_keywords = 0
total_groups = len(duplicates)
records_with_different_keywords = {}
same_id_groups = 0
isbns_with_same_ids = []

for group in duplicates:
    author = group["author"]
    title = group["title"]
    #isbn = group["isbn"]
    records = group["records"]
    
    # Extract keyword sets from all records
    keyword_sets = [tuple(sorted(rec["keywords"])) for rec in records]
    isbn = [rec["isbn"] for rec in records]

  

    # Check if all keyword sets are identical
    if len(set(keyword_sets)) > 1:
        groups_with_different_keywords += 1
        records_with_different_keywords.update({title: isbn})
        print(f"DIFFERENT KEYWORDS: {author} - {title}")
        for i, rec in enumerate(records):
            print(f"  Record {i+1} (id: {rec['id']}):")
            print(f"    Keywords: {rec['keywords']}")
        print()



print(f"Total duplicate groups: {total_groups}")
print(f"Groups with different keyword sets: {groups_with_different_keywords}")
print(f"Groups with identical keyword sets: {total_groups - groups_with_different_keywords}")
print(f"\nISBNs with different keyword sets:")
for title, isbn in records_with_different_keywords.items():
    print(f"{title}: {isbn}")


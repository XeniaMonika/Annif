import os
import json
import xml.etree.ElementTree as ET



input_folder_big = "./Data/Spanish_ALL/Split"
input_folder_small = "./Data/Spanish_FID"
output_folder_big = "./Data/Spanish_ALL"
output_folder_small = "./Data/Spanish_FID"

NS1 = "info:srw/schema/5/picaXML-v1.0"
ns = {"ns1": NS1}

def text_of(elem):
    return elem.text.strip() if elem is not None and elem.text else None


def map_titles_to_authors(input_folders, output_folders):
    records = []
    author_count = 0
    total = 0
    for folder in input_folders:
        for root, _, files in os.walk(folder):
            for fname in files:
                if fname.endswith("clean.xml"):
                    path = os.path.join(root, fname)
                    try:
                        tree = ET.parse(path)
                        for record in tree.findall('.//ns1:record', ns):
                            total += 1
                            subtitle = text_of(record.find(".//ns1:datafield[@tag='021A']/ns1:subfield[@code='d']", ns)) or ""
                            title_full = f"{title} : {subtitle}" if subtitle and title else (title or subtitle or "")
                            author = text_of(record.find(".//ns1:datafield[@tag='028A']/ns1:subfield[@code='a']", ns)) or ""
                            if author:
                                author_count += 1
                            records.append({"title": title_full, "author": author})
                    except Exception:
                        continue
                
    # save to each output folder
    for out in output_folders:
        try:
            os.makedirs(out, exist_ok=True)
            outpath = os.path.join(out, "title_author_mapping.json")
            with open(outpath, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    pct = (author_count / total * 100) if total else 0
    print(f"Author count: {author_count} ({pct:.2f}%)")


if __name__ == '__main__':
    map_titles_to_authors([input_folder_small], [output_folder_small])
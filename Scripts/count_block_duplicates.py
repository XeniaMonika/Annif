import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

INPUT_FOLDER_FID = "./Data/Spanish_FID/"
INPUT_FOLDER_ALL = "./Data/Spanish_ALL/Split/"

NS1 = "info:srw/schema/5/picaXML-v1.0"
ns = {"ns1": NS1}


def text_of(element):
    return element.text.strip() if element is not None and element.text else None


def find_duplicates_in_folder(folder_path):
    folder = Path(folder_path)
    xml_files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in {".xml", ".xmk"}]
    if not xml_files:
        print(f"No XML or XMK files found in folder: {folder}")
        return

    records_by_author_title = defaultdict(list)
    total_records = 0

    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for record in root:
            total_records += 1
            title = text_of(record.find(".//ns1:datafield[@tag='021A']/ns1:subfield[@code='a']", ns))
            subtitle = text_of(record.find(".//ns1:datafield[@tag='021A']/ns1:subfield[@code='d']", ns)) or ""
            author_first_name = text_of(record.find(".//ns1:datafield[@tag='028A']/ns1:subfield[@code='D']", ns)) or text_of(record.find(".//ns1:datafield[@tag='028C']/ns1:subfield[@code='D']", ns))
            author_last_name = text_of(record.find(".//ns1:datafield[@tag='028A']/ns1:subfield[@code='A']", ns)) or text_of(record.find(".//ns1:datafield[@tag='028C']/ns1:subfield[@code='A']", ns))
            if title and (author_last_name or author_first_name):
                author = ", ".join(filter(None, (author_last_name, author_first_name)))
                records_by_author_title[(author, title, subtitle)].append(record)

    duplicate_groups = [recs for recs in records_by_author_title.values() if len(recs) > 1]
    duplicate_records = sum(len(recs) for recs in duplicate_groups)
    percentage = duplicate_records / total_records * 100 if total_records else 0

    print(f"Total records: {total_records}")
    print(f"Duplicate groups by author and full title: {len(duplicate_groups)}")
    print(f"Records involved in duplicates: {duplicate_records}")
    print(f"Percentage of records in duplicates: {percentage:.2f}%")

    # return mapping of keys -> list of record elements and total count for further processing
    return records_by_author_title, total_records


def clean_duplicates_in_folder(folder_path):
    # reuse the duplicate analysis to know which keys are duplicates
    records_by_author_title, _ = find_duplicates_in_folder(folder_path)
    duplicate_keys = {k for k, v in records_by_author_title.items() if len(v) > 1}

    folder = Path(folder_path)
    xml_files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in {".xml", ".xmk"}]
    if not xml_files:
        print(f"No XML or XMK files found in folder: {folder}")
        return

    # Keep track globally which duplicate keys we've already kept (to keep first occurrence)
    kept_keys = set()

    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        new_root = ET.Element(root.tag)

        for record in root:
            title = text_of(record.find(".//ns1:datafield[@tag='021A']/ns1:subfield[@code='a']", ns))
            subtitle = text_of(record.find(".//ns1:datafield[@tag='021A']/ns1:subfield[@code='d']", ns)) or ""
            author_first_name = text_of(record.find(".//ns1:datafield[@tag='028A']/ns1:subfield[@code='D']", ns)) or text_of(record.find(".//ns1:datafield[@tag='028C']/ns1:subfield[@code='D']", ns))
            author_last_name = text_of(record.find(".//ns1:datafield[@tag='028A']/ns1:subfield[@code='A']", ns)) or text_of(record.find(".//ns1:datafield[@tag='028C']/ns1:subfield[@code='A']", ns))

            if title and (author_last_name or author_first_name):
                author = ", ".join(filter(None, (author_last_name, author_first_name)))
                key = (author, title, subtitle)
            else:
                # non-keyable records: keep them
                key = None

            if key is None:
                new_root.append(record)
            elif key in duplicate_keys:
                if key not in kept_keys:
                    new_root.append(record)
                    kept_keys.add(key)
                else:
                    # skip duplicate
                    continue
            else:
                new_root.append(record)

        out_path = xml_file.with_name(xml_file.stem + "_no_duplicates" + xml_file.suffix)
        ET.ElementTree(new_root).write(out_path, encoding="utf-8", xml_declaration=True)
        print(f"Wrote cleaned file: {out_path}")


if __name__ == "__main__":
    find_duplicates_in_folder(INPUT_FOLDER_FID)
    clean_duplicates_in_folder(INPUT_FOLDER_FID)

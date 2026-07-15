import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

INPUT_FOLDER_FID = "./Data/Spanish_FID/"
INPUT_FOLDER_ALL = "./Data/Spanish_ALL/Split/"

NS1 = "info:srw/schema/5/picaXML-v1.0"
ns = {"ns1": NS1}

# Matches filenames ending in "gnd.xml" or "gnd_partN.xml", with any prefix
# (e.g. "gnd.xml", "data_gnd.xml", "gnd_part1.xml", "data_gnd_part23.xml")
GND_FILE_PATTERN = re.compile(r"(^|_)gnd(_part\d+)?\.xml$", re.IGNORECASE)


def _is_gnd_file(path: Path) -> bool:
    return path.is_file() and bool(GND_FILE_PATTERN.search(path.name))


def text_of(element):
    return element.text.strip() if element is not None and element.text else None


def find_duplicates_in_folder(folder_path):
    folder = Path(folder_path)
    xml_files = [p for p in folder.iterdir() if _is_gnd_file(p)]
    if not xml_files:
        print(f"No matching XML files found in folder: {folder}")
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
    """
    Removes duplicate records per file, but keeps the results in memory instead
    of writing them to disk. Returns a list of (xml_file, new_root) tuples, where
    new_root is the deduplicated ElementTree root for that file, ready to be
    passed straight into clean_bkk_irrelevant_records.
    """
    # reuse the duplicate analysis to know which keys are duplicates
    records_by_author_title, _ = find_duplicates_in_folder(folder_path)
    duplicate_keys = {k for k, v in records_by_author_title.items() if len(v) > 1}
    folder = Path(folder_path)
    xml_files = [p for p in folder.iterdir() if _is_gnd_file(p)]
    if not xml_files:
        print(f"No matching XML files found in folder: {folder}")
        return []

    # Keep track globally which duplicate keys we've already kept (to keep first occurrence)
    kept_keys = set()
    deduplicated_files = []

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

        deduplicated_files.append((xml_file, new_root))
        print(f"Deduplicated in memory: {xml_file.name} ({len(new_root)} records kept)")

    return deduplicated_files


def _load_irrelevant_domains(folder_path):
    json_path = Path(folder_path) / "irrelevant_domains.json"
    if not json_path.exists():
        print(f"irrelevant_domains.json not found in folder: {json_path}")
        return []

    with json_path.open("r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    if isinstance(data, list):
        return [str(item).strip().lower() for item in data if str(item).strip()]

    print(f"irrelevant_domains.json does not contain a list: {json_path}")
    return []


def _record_has_bkk_classification(record):
    for field in record.findall(".//ns1:datafield[@tag='045Q']", ns):
        for subfield in field.findall("ns1:subfield[@code='V']", ns):
            if text_of(subfield) == "Tkv":
                return True
    return False


def _record_bkk_domains(record):
    x_values = []
    j_values = []

    for field in record.findall(".//ns1:datafield[@tag='045Q']", ns):
        for subfield in field.findall("ns1:subfield[@code='X']", ns):
            text = text_of(subfield)
            if text:
                x_values.append(text)
        for subfield in field.findall("ns1:subfield[@code='j']", ns):
            text = text_of(subfield)
            if text:
                j_values.append(text)

    if x_values:
        return ", ".join(x_values)
    if j_values:
        return ", ".join(j_values)
    return None


def clean_bkk_irrelevant_records(folder_path, deduplicated_files):
    """
    Takes the in-memory deduplicated data produced by clean_duplicates_in_folder
    (a list of (xml_file, root) tuples) and filters out BKK-irrelevant records.
    This is the only step that writes to disk — the intermediate "no duplicates"
    files are never saved.
    """
    input_path = Path(folder_path)
    output_path = input_path
    output_path.mkdir(parents=True, exist_ok=True)

    irrelevant_domains = _load_irrelevant_domains(folder_path)
    if not irrelevant_domains:
        print("No irrelevant domains loaded. No records will be filtered by domain.")

    if not deduplicated_files:
        print(f"No deduplicated data to process for folder: {input_path}")
        return

    for xml_file, dedup_root in deduplicated_files:
        new_root = ET.Element(dedup_root.tag, dedup_root.attrib)
        kept_count = 0

        for record in dedup_root:
            if not _record_has_bkk_classification(record):
                continue

            keywords = _record_bkk_domains(record)
            if keywords:
                terms = [term.strip().lower() for term in keywords.split(",") if term.strip()]
            else:
                terms = []

            if any(term in irrelevant_domains for term in terms):
                continue

            new_root.append(record)
            kept_count += 1

        clean_name = f"{xml_file.stem}_clean{xml_file.suffix}"
        out_file = output_path / clean_name
        ET.ElementTree(new_root).write(out_file, encoding="utf-8", xml_declaration=True)
        print(f"Wrote BKK-cleaned file: {out_file} ({kept_count} records kept)")


if __name__ == "__main__":
    deduplicated_files = clean_duplicates_in_folder(INPUT_FOLDER_ALL)
    clean_bkk_irrelevant_records(INPUT_FOLDER_ALL, deduplicated_files)
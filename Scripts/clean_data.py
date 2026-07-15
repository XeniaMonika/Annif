import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import quoteattr

INPUT_FOLDER_FID = "./Data/Spanish_FID/"
INPUT_FOLDER_ALL = "./Data/Spanish_ALL/Split/"

NS1 = "info:srw/schema/5/picaXML-v1.0"
ns = {"ns1": NS1}

# Re-serializing records with ET.tostring() would otherwise invent ns0/ns1
# prefixes per call; registering the default namespace keeps output clean.
ET.register_namespace("", NS1)

# Matches filenames ending in "gnd.xml" or "gnd_partN.xml", with any prefix
# (e.g. "gnd.xml", "data_gnd.xml", "gnd_part1.xml", "data_gnd_part23.xml")
GND_FILE_PATTERN = re.compile(r"(^|_)gnd(_part\d+)?\.xml$", re.IGNORECASE)


def _is_gnd_file(path: Path) -> bool:
    return path.is_file() and bool(GND_FILE_PATTERN.search(path.name))


def _gnd_files(folder_path):
    folder = Path(folder_path)
    return sorted(p for p in folder.iterdir() if _is_gnd_file(p))


def text_of(element):
    return element.text.strip() if element is not None and element.text else None


def _record_key(record):
    """(author, title, subtitle) key, or None if the record can't be keyed."""
    title = text_of(record.find("ns1:datafield[@tag='021A']/ns1:subfield[@code='a']", ns))
    subtitle = text_of(record.find("ns1:datafield[@tag='021A']/ns1:subfield[@code='d']", ns)) or ""
    author_first_name = (
        text_of(record.find("ns1:datafield[@tag='028A']/ns1:subfield[@code='D']", ns))
        or text_of(record.find("ns1:datafield[@tag='028C']/ns1:subfield[@code='D']", ns))
    )
    author_last_name = (
        text_of(record.find("ns1:datafield[@tag='028A']/ns1:subfield[@code='A']", ns))
        or text_of(record.find("ns1:datafield[@tag='028C']/ns1:subfield[@code='A']", ns))
    )
    if title and (author_last_name or author_first_name):
        author = ", ".join(filter(None, (author_last_name, author_first_name)))
        return (author, title, subtitle)
    return None


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


def _root_info(xml_file):
    """Peek at just the root element's tag/attributes without reading the file body."""
    with open(xml_file, "rb") as f:
        context = ET.iterparse(f, events=("start",))
        _, root = next(context)
        local_name = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        return local_name, dict(root.attrib)


def _iter_records(file_obj):
    """
    Stream a PICA XML file record by record.

    Only the element currently being yielded is ever fully materialized;
    every finished element is cleared immediately afterwards, so peak
    memory stays roughly O(one record) instead of O(file size) — unlike
    ET.parse(), which builds the entire DOM (and therefore the whole file)
    in memory at once.
    """
    depth = 0
    for event, elem in ET.iterparse(file_obj, events=("start", "end")):
        if event == "start":
            depth += 1
        else:
            depth -= 1
            if depth == 1:  # direct child of the root == one record
                yield elem
                elem.clear()


def count_duplicate_keys(folder_path):
    """
    Pass 1: stream every file once and tally how many records share each
    (author, title, subtitle) key. Only compact string tuples and counts
    are kept in memory — never the records themselves.
    """
    xml_files = _gnd_files(folder_path)
    if not xml_files:
        print(f"No matching XML files found in folder: {folder_path}")
        return set(), 0

    key_counts = defaultdict(int)
    total_records = 0

    for xml_file in xml_files:
        with open(xml_file, "rb") as f:
            for record in _iter_records(f):
                total_records += 1
                key = _record_key(record)
                if key is not None:
                    key_counts[key] += 1

    duplicate_keys = {key for key, count in key_counts.items() if count > 1}
    duplicate_records = sum(key_counts[key] for key in duplicate_keys)
    percentage = duplicate_records / total_records * 100 if total_records else 0

    print(f"Total records: {total_records}")
    print(f"Duplicate groups by author and full title: {len(duplicate_keys)}")
    print(f"Records involved in duplicates: {duplicate_records}")
    print(f"Percentage of records in duplicates: {percentage:.2f}%")

    return duplicate_keys, total_records


def _opening_tag(local_name, attrib):
    parts = [f"<{local_name}", f'xmlns="{NS1}"']
    for key, value in attrib.items():
        parts.append(f"{key}={quoteattr(value)}")
    return " ".join(parts) + ">\n"


def clean_folder(folder_path, duplicate_keys):
    """
    Pass 2: stream each file again. For every record, apply the dedup rule
    (keep only the first occurrence of a duplicate key) and the BKK
    relevance rule, then write survivors straight to disk. No in-memory
    tree is ever built for the output — this replaces the old approach of
    accumulating every kept record into an ET.Element before writing.
    """
    input_path = Path(folder_path)
    irrelevant_domains = _load_irrelevant_domains(folder_path)
    if not irrelevant_domains:
        print("No irrelevant domains loaded. No records will be filtered by domain.")

    xml_files = _gnd_files(folder_path)
    if not xml_files:
        print(f"No matching XML files found in folder: {input_path}")
        return

    kept_keys_seen = set()  # global across all files, like the original script

    for xml_file in xml_files:
        root_local, root_attrib = _root_info(xml_file)
        out_file = input_path / f"{xml_file.stem}_clean{xml_file.suffix}"

        kept_count = 0
        with open(xml_file, "rb") as fin, open(out_file, "w", encoding="utf-8") as fout:
            fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            fout.write(_opening_tag(root_local, root_attrib))

            for record in _iter_records(fin):
                key = _record_key(record)
                if key is not None and key in duplicate_keys:
                    if key in kept_keys_seen:
                        continue  # duplicate, and we already kept the first one
                    kept_keys_seen.add(key)

                if not _record_has_bkk_classification(record):
                    continue

                keywords = _record_bkk_domains(record)
                terms = [t.strip().lower() for t in keywords.split(",") if t.strip()] if keywords else []
                if any(term in irrelevant_domains for term in terms):
                    continue

                fout.write(ET.tostring(record, encoding="unicode"))
                fout.write("\n")
                kept_count += 1

            fout.write(f"</{root_local}>\n")

        print(f"Wrote cleaned file: {out_file} ({kept_count} records kept)")


if __name__ == "__main__":
    duplicate_keys, _ = count_duplicate_keys(INPUT_FOLDER_ALL)
    clean_folder(INPUT_FOLDER_ALL, duplicate_keys)
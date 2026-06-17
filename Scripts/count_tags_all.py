import os
import xml.etree.ElementTree as ET

root_folder = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_ALL\\Split"
PICA_NS = "info:srw/schema/5/picaXML-v1.0"


def count_tags_in_file(file_path, tags):
    """Return a dict {tag: count_of_records_containing_tag} for one file."""
    counts = {tag: 0 for tag in tags}

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Parse error in {file_path}: {e}")
        return counts

    records = root.findall(f'.//{{{PICA_NS}}}record')

    for record in records:
        for tag in tags:
            matches = record.findall(f'.//{{{PICA_NS}}}datafield[@tag="{tag}"]')
            if matches:
                counts[tag] += 1

    return counts


def count_tags_in_dataset(tags, folder=None, verbose=True):
    """Walk the folder, sum per-tag counts across all .xml files.

    Returns a dict {tag: total_count}.
    """
    if folder is None:
        folder = root_folder

    totals = {tag: 0 for tag in tags}

    for dirpath, _, filenames in os.walk(folder):
        for filename in filenames:
            if filename.lower().endswith('.xml'):
                file_path = os.path.join(dirpath, filename)
                file_counts = count_tags_in_file(file_path, tags)

                if verbose:
                    summary = ", ".join(f"{t}={c}" for t, c in file_counts.items())
                    print(f"{filename}: {summary}")

                for tag in tags:
                    totals[tag] += file_counts[tag]

    return totals


if __name__ == '__main__':
    tags_to_check = ['007G', '010E', '003S', '003H', '003D', '007H', '045F', '045H', '045R', '045V', '032W', '013D', '011@']
    results = count_tags_in_dataset(tags_to_check)

    print("\n--- Totals ---")
    for tag, total in results.items():
        print(f"'{tag}': {total:,}")
import os
import xml.etree.ElementTree as ET

root_folder = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_ALL\\Split"
PICA_NS = "info:srw/schema/5/picaXML-v1.0"


def iterate_xml_files(folder=None):
    """Yield full paths to .xml files in the given folder tree."""
    if folder is None:
        folder = root_folder

    for dirpath, _, filenames in os.walk(folder):
        for filename in filenames:
            if filename.lower().endswith('.xml'):
                yield os.path.join(dirpath, filename)


def apply_to_xml_files(function, folder=None, *args, **kwargs):
    """Apply a function to every XML file in the folder tree."""
    for file_path in iterate_xml_files(folder):
        yield function(file_path, *args, **kwargs)


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
    """Sum per-tag counts across all .xml files in the folder tree."""
    totals = {tag: 0 for tag in tags}

    for file_path in iterate_xml_files(folder):
        file_counts = count_tags_in_file(file_path, tags)

        if verbose:
            summary = ", ".join(f"{t}={c}" for t, c in file_counts.items())
            print(f"{os.path.basename(file_path)}: {summary}")

        for tag in tags:
            totals[tag] += file_counts[tag]

    return totals

'''
if __name__ == '__main__':
    tags_to_check = ['007G', '010E', '003S', '003H', '003D', '007H', '045F', '045H', '045R', '045V', '032W', '013D', '011@']
    results = count_tags_in_dataset(tags_to_check)

    print("\n--- Totals ---")
    for tag, total in results.items():
        print(f"'{tag}': {total:,}")
'''

def look_for_tags_with_A_and_D_subfields(tag, folder=None):
    """Return list of matches where the given tag contains both subfield a and subfield d.

    Each match is a tuple: (file_path, tag, text_a, text_d).
    """
    if folder is None:
        folder = root_folder

    matches = []
    for file_path in iterate_xml_files(folder):
        try:
            root = ET.parse(file_path).getroot()
        except ET.ParseError as e:
            print(f"Parse error in {file_path}: {e}")
            continue

        for record in root.findall(f'.//{{{PICA_NS}}}record'):
            for datafield in record.findall(f'./{{{PICA_NS}}}datafield[@tag="{tag}"]'):
                subfield_a = datafield.find(f'./{{{PICA_NS}}}subfield[@code="A"]')
                subfield_d = datafield.find(f'./{{{PICA_NS}}}subfield[@code="D"]')
                if subfield_a is not None and subfield_d is not None:
                    text_a = subfield_a.text or ''
                    text_d = subfield_d.text or ''
                    matches.append((file_path, tag, text_a, text_d))
                    break
    return matches

persons = look_for_tags_with_A_and_D_subfields("044L")
print(persons)
print(len(persons))
import os
import xml.etree.ElementTree as ET
from collections import Counter
import json

root_folder_all = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_ALL\\Split"
root_folder_fid = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_FID"
fid_file = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_FID\\data_gnd.xml"
PICA_NS = "info:srw/schema/5/picaXML-v1.0"

        

def iterate_xml_files(folder=None):
    """Yield full paths to .xml files in the given folder tree."""
    if folder is None:
        folder = root_folder_all

    for dirpath, _, filenames in os.walk(folder):
        for filename in filenames:
            if filename.lower().endswith('.xml'):
                yield os.path.join(dirpath, filename)


def apply_to_xml_files(function, folder=None, *args, **kwargs):
    """Apply a function to every XML file in the folder tree."""
    for file_path in iterate_xml_files(folder):
        yield function(file_path, *args, **kwargs)


def count_tags_in_file(file_path, tags):
    """Return a dict {tag: count_of_records_containing_tag} for one file.

    The returned dict also contains the key 'file_path' with the path to the
    file counted.
    """
    counts = {tag: 0 for tag in tags}
    counts['file_path'] = file_path

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

#persons = look_for_tags_with_A_and_D_subfields("044L")
#print(persons)
#print(len(persons))


def extract_045Q_texts(folder_path):
    """Process all .xml files in folder_path, extract 045Q texts and save domains.xml there.

    Extraction rules:
    - If subfield X is present, take that as text
    - If no X, take all subfield j values separated by commas as string
    - If neither X nor j exists, skip this tag

    The function writes a file named domains.xml into folder_path containing counts
    and returns the Counter.
    """
   
    texts = []

    if not os.path.isdir(folder_path):
        print(f"Not a folder: {folder_path}")
        return Counter()

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith('.xml'):
            continue
        file_path = os.path.join(folder_path, filename)
        try:
            root = ET.parse(file_path).getroot()
        except ET.ParseError as e:
            print(f"Parse error in {file_path}: {e}")
            continue

        for record in root.findall(f'.//{{{PICA_NS}}}record'):
            for datafield in record.findall(f'./{{{PICA_NS}}}datafield[@tag="045Q"]'):
                subfield_x = datafield.find(f'./{{{PICA_NS}}}subfield[@code="X"]')
                if subfield_x is not None and subfield_x.text:
                    texts.append(subfield_x.text)
                else:
                    subfields_j = datafield.findall(f'./{{{PICA_NS}}}subfield[@code="j"]')
                    j_texts = [sf.text for sf in subfields_j if sf.text]
                    if j_texts:
                        texts.append(','.join(j_texts))

    counts = Counter(texts)

    # Build JSON output (list of {domain, count})
    out_list = []
    for text, cnt in counts.most_common():
        out_list.append({"domain": text, "count": cnt})

    out_path = os.path.join(folder_path, 'domains.json')
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(out_list, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"Could not write output file {out_path}: {e}")

    return counts


'''
for file in os.listdir(root_folder):
    if file.lower().endswith('.xml'):
        file_path = os.path.join(root_folder, file)
        counts = count_tags_in_file(file_path, ["045Q"])
        print(f"{file}: {counts['045Q']}")
'''

#counts = count_tags_in_file(fid_file, ["045Q"])
#print(counts['045Q'])

domain_texts = extract_045Q_texts(root_folder_all)
print(domain_texts)

# Save this to a file!
import os
import xml.etree.ElementTree as ET

path_pica = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_FID\\data_gnd.xml"
path_marc = "C:\\Users\\kudelamo\\Projects\\Annif\\Data\\Spanish_FID\\data_689.xml"


def read_ppns_marc(filename, target_tag):
    tree = ET.parse(filename)   
    root = tree.getroot()
    ppns = set()
    for elem in root.iter():
        tag_attr = elem.attrib.get("tag")        
        if tag_attr == target_tag:            
            text = elem.text
        elif isinstance(elem.tag, str) and elem.tag.endswith(target_tag):
            text = elem.text
        else:
            continue
        if text:
            text = text.strip()
            if text:
                ppns.add(text)
    return ppns

def read_ppns_pica(filename, target_tag):
    NS1 = "info:srw/schema/5/picaXML-v1.0" 
    ns = {"ns1": NS1}
    tree = ET.parse(filename)   
    root = tree.getroot()
    ppns = set()
    for elem in root.iter():
        tag_attr = elem.attrib.get("tag")        
        if tag_attr == target_tag:            
            subfield = elem.find("ns1:subfield[@code='0']", ns)
            text = subfield.text if subfield is not None else None
        elif isinstance(elem.tag, str) and elem.tag.endswith(target_tag):
            text = elem.text
        else:
            continue
        if text:
            text = text.strip()
            if text:
                ppns.add(text)
    return ppns

def save_list(ppns, filename):
    with open(filename, "w", encoding="utf-8") as out:
        for ppn in sorted(ppns):
            out.write(ppn + "\n")



def main():
    pica_ppns = read_ppns_pica(path_pica, "003@")
    marc_ppns = read_ppns_marc(path_marc, "001")

    only_in_pica = pica_ppns - marc_ppns
    only_in_marc = marc_ppns - pica_ppns

    output_dir = os.path.dirname(path_pica)
    os.makedirs(output_dir, exist_ok=True)

    save_list(only_in_pica, os.path.join(output_dir, "ppns_only_in_pica.txt"))
    save_list(only_in_marc, os.path.join(output_dir, "ppns_only_in_marc.txt"))

    print(f"PPNs only in PICA written to {os.path.join(output_dir, 'ppns_only_in_pica.txt')}")
    print(f"PPNs only in MARC written to {os.path.join(output_dir, 'ppns_only_in_marc.txt')}")


if __name__ == "__main__":
    main()

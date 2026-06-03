
import xml.etree.ElementTree as ET

path_data = "C:\\Users\\kudelamo\\Projects\\Annif\\PicaXML\\Data\\Spanish\\data_gnd.xml"


def record_has_abstract(record):
    for field in record.iter():
        tag = field.tag
        field_id = field.attrib.get("id") or field.attrib.get("tag") or tag
        if field_id == "047I":
            # Check subfields for actual text content
            for subfield in field:
                if subfield.text and subfield.text.strip():
                    return True
            # Fallback: text directly in field element
            if field.text and field.text.strip():
                return True
    return False


def main():
    tree = ET.parse(path_data)
    root = tree.getroot()

    records = root.findall('.//record')
    if not records:
        records = list(root)  # fallback if root contains records directly

    count = sum(1 for record in records if record_has_abstract(record))
    print(f"Records with 047I abstract: {count} out of {len(records)}")


if __name__ == '__main__':
    main()


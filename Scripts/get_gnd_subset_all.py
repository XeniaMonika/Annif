import xml.etree.ElementTree as ET
import os
import re

input_file = "./Data/Spanish_All/data_raw.xml"
output_folder = "./Data/Spanish_All"
output_file = os.path.join(output_folder, "data_gnd.xml")
os.makedirs(output_folder, exist_ok=True)

NS1 = "info:srw/schema/5/picaXML-v1.0"
ns = {"ns1": NS1}


def has_gnd_subfield(datafield, ns):
    subfield_7 = datafield.find("ns1:subfield[@code='7']", ns)
    return subfield_7 is not None and subfield_7.text and subfield_7.text.startswith("gnd")


with open(output_file, "w", encoding="utf-8") as out:
    out.write("<records>\n")
    total_count = 0

    for event, record in ET.iterparse(input_file, events=("end",)):
        if not record.tag.endswith("}record") and record.tag != "record":
            continue
            

        def has_044l_subfield_a_gnd(datafield, ns):
            sf = datafield.find("ns1:subfield[@code='a']", ns)
            return sf is not None and sf.text and sf.text.startswith("gnd")

        has_gnd = any(
            ((datafield.get("tag") == "044K" or datafield.get("tag") == "041A") and has_gnd_subfield(datafield, ns))
            or (datafield.get("tag") == "044L" and has_044l_subfield_a_gnd(datafield, ns))
            for datafield in record.findall(".//ns1:datafield", ns)
        )
        if has_gnd:
            for datafield in record.findall(".//ns1:datafield[@tag='021A']", ns):
                for subfield in datafield.findall("ns1:subfield[@code='a']", ns):
                    subfield.text = re.sub(r"@", "", subfield.text or "")
            for datafield in record.findall(".//ns1:datafield[@tag='004A']", ns):
                for subfield in datafield.findall("ns1:subfield[@code='0']", ns):
                    subfield.text = re.sub(r"-", "", subfield.text or "")
            out.write(ET.tostring(record, encoding="unicode") + "\n")
            total_count += 1

        record.clear()  # releases memory after each record

    out.write("</records>")

print(f"Saved {total_count} records to {output_file}")
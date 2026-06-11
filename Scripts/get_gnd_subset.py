import xml.etree.ElementTree as ET
import os
import re

folders = [
    "./Data/Spanish_FID/lsy_ni",
    "./Data/Spanish_FID/lsy_ro",
    "./Data/Spanish_FID/lsy_ip",
    "./Data/Spanish_FID/ssg_7_34",
    "./Data/Spanish_FID/sfk_fid_rom"
]

output_folder = "./PicaXML/Data/Spanish_FID"
output_file = os.path.join(output_folder, "data_gnd.xml")
os.makedirs(output_folder, exist_ok=True)

NS1 = "info:srw/schema/5/picaXML-v1.0" 
ns = {"ns1": NS1}


def has_gnd_subfield(datafield, ns):
    """Check if datafield has subfield code='7' starting with 'gnd'"""
    subfield_7 = datafield.find("ns1:subfield[@code='7']", ns)
    return subfield_7 is not None and subfield_7.text and subfield_7.text.startswith("gnd")


with open(output_file, "w", encoding="utf-8") as out:
    out.write("<records>\n")
    total_count = 0

    for folder in folders:
        input_file = os.path.join(folder, "data.xml")
        tree = ET.parse(input_file)
        root = tree.getroot()
        count = 0


        for record in root:            

            has_gnd = any(
                (datafield.get("tag") == "044K" or datafield.get("tag") == "041A") and has_gnd_subfield(datafield, ns)
                for datafield in record.findall(".//ns1:datafield", ns)
            )
            if has_gnd:
                #remove @ from titles
                for datafield in record.findall(".//ns1:datafield[@tag='021A']", ns):
                    for subfield in datafield.findall("ns1:subfield[@code='a']", ns):
                        subfield.text = re.sub(r"@", "", subfield.text or "")
                #remove - from isbn
                for datafield in record.findall(".//ns1:datafield[@tag='004A']", ns):
                    for subfield in datafield.findall("ns1:subfield[@code='0']", ns):
                        subfield.text = re.sub(r"-", "", subfield.text or "")
                out.write(ET.tostring(record, encoding="unicode") + "\n")
                count += 1
                total_count += 1     
    
            

        print(f"Added {count} records from {folder}")

    out.write("</records>")

print(f"Saved {total_count} records to {output_file}")


  
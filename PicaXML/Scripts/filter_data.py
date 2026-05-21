import xml.etree.ElementTree as ET
import os
import re

folders = [
    "./PicaXML/Data/Spanish/lsy_ni",
    "./PicaXML/Data/Spanish/lsy_ro",
    "./PicaXML/Data/Spanish/lsy_ip",
    "./PicaXML/Data/Spanish/ssg_7_34",
    "./PicaXML/Data/Spanish/sfk_fid_rom"
]

output_folder = "./PicaXML/Data/Spanish"
output_file = os.path.join(output_folder, "data_gnd.xml")
os.makedirs(output_folder, exist_ok=True)

NS1 = "info:srw/schema/5/picaXML-v1.0" 
ns = {"ns1": NS1}


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
                datafield.get("tag") == "044K" or datafield.get("tag") == "041A" 
                for datafield in record.findall(".//ns1:datafield", ns)
            )
            if has_gnd:
                out.write(ET.tostring(record, encoding="unicode") + "\n")
                count += 1
                total_count += 1
        
            

        print(f"Added {count} records from {folder}")

    out.write("</records>")

print(f"Saved {total_count} records to {output_file}")


  
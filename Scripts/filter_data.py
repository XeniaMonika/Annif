import xml.etree.ElementTree as ET
import os
import re

folders = [
    "./Data/Spanish/lsy_ni",
    "./Data/Spanish/lsy_ro",
    "./Data/Spanish/lsy_ip",
    "./Data/Spanish/ssg_7_34"
]

output_folder = "./Data/Spanish"
output_file = os.path.join(output_folder, "data_689.xml")
os.makedirs(output_folder, exist_ok=True)

NS1 = "http://www.loc.gov/MARC21/slim"
ns = {"ns1": NS1}


with open(output_file, "w", encoding="utf-8") as out:
    out.write("<records>\n")

    for folder in folders:
        input_file = os.path.join(folder, "data.xml")
        tree = ET.parse(input_file)
        root = tree.getroot()
        count = 0


        for record in root:

            for parent in record.findall(".//ns1:*", ns):
                for datafield in list(parent):
                    tag = datafield.get("tag")
                    if tag and tag.startswith("6") and tag != "689":
                        parent.remove(datafield)
                        
            has_689 = any(
                datafield.get("tag") == "689"
                for datafield in record.findall(".//ns1:datafield", ns)
            )
            if has_689:
                out.write(ET.tostring(record, encoding="unicode") + "\n")
                count += 1

             # Remove all 6xx except 689            
            

        print(f"Added {count} records from {folder}")

    out.write("</records>")


  
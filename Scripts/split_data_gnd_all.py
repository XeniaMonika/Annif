import xml.etree.ElementTree as ET

input_file = "./Data/Spanish_ALL/data_gnd.xml"
output_folder = "./Data/Spanish_ALL/Split"
records_per_file = 43000

import os
os.makedirs(output_folder, exist_ok=True)

NS1 = "info:srw/schema/5/picaXML-v1.0"

file_index = 1
record_count = 0
current_file = None

def open_new_file(index):
    path = os.path.join(output_folder, f"data_gnd_part{index}.xml")
    f = open(path, "w", encoding="utf-8")
    f.write(f'<records xmlns:ns1="{NS1}">\n')
    return f

current_file = open_new_file(file_index)

for event, elem in ET.iterparse(input_file, events=("end",)):
    if elem.tag.endswith("}record") or elem.tag == "record":
        current_file.write(ET.tostring(elem, encoding="unicode") + "\n")
        record_count += 1
        elem.clear()

        if record_count % records_per_file == 0:
            current_file.write("</records>")
            current_file.close()
            file_index += 1
            current_file = open_new_file(file_index)

current_file.write("</records>")
current_file.close()

print(f"Split into {file_index} files, {record_count} total records")
import requests
import time
from tqdm import tqdm
import xml.etree.ElementTree as ET
import os

BASE_URL_Hamburg = "https://sru.k10plus.de/opac-de-18"
QUERIES_Hamburg = {
    "./Data/Spanish_xml/lsy_ni": "pica.lsy=ni????? and pica.spr=spa not pica.lsy=ip????? not pica.lsy=ro????? not pica.ssg=7,34",
    "./Data/Spanish_xml/lsy_ro": "pica.lsy=ro????? and pica.spr=spa not pica.lsy=ip????? not pica.lsy=ni????? not pica.ssg=7,34",
    "./Data/Spanish_xml/lsy_ip": "pica.lsy=ip????? and pica.spr=spa not pica.lsy=ro????? not pica.lsy=ni????? not pica.ssg=7,34"
}

BASE_URL_Verbundskatalog = "https://sru.k10plus.de/opac-de-627"
QUERY_Verbundskatalog = {
    "./Data/Spanish_xml/ssg_7_34": "pica.ssg=7,34 and pica.spr=spa not pica.lsy=ip????? not pica.lsy=ni????? not pica.lsy=ro?????"
}

CHUNK_SIZE = 100


def get_total_records(base_url, query):
    params = {
        "version": "1.1",
        "operation": "searchRetrieve",
        "query": query,
        "maximumRecords": 1,
        "recordSchema": "marcxml"
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    ns = {"srw": "http://www.loc.gov/zing/srw/"}
    return int(root.find("srw:numberOfRecords", ns).text)


def fetch_all_records(base_url, query, folder, chunk_size=100):
    total = get_total_records(base_url, query)
    print(f"Total records found: {total}")

    all_records = []
    ns = {"srw": "http://www.loc.gov/zing/srw/"}
    params = {
        "version": "1.1",
        "operation": "searchRetrieve",
        "query": query,
        "maximumRecords": chunk_size,
        "recordSchema": "marcxml"
    }

    for start in tqdm(range(1, total + 1, chunk_size)):
        params["startRecord"] = start
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        for record in root.findall(".//srw:recordData", ns):
            all_records.append(ET.tostring(record, encoding="unicode"))

        time.sleep(0.5)

    print(f"Downloaded {len(all_records)} records")

    os.makedirs(folder, exist_ok=True)
    with open(f"{folder}/data.xml", "w", encoding="utf-8") as f:
        f.write("<records>\n")
        for record in all_records:
            f.write(record + "\n")
        f.write("</records>")
            
    print(f"File saved in {folder}/data.xml")
    return all_records


for folder, query in QUERIES_Hamburg.items():
    all_records = fetch_all_records(BASE_URL_Hamburg, query, folder, CHUNK_SIZE)
    
for folder, query in QUERY_Verbundskatalog.items():
    all_records = fetch_all_records(BASE_URL_Verbundskatalog, query, folder, CHUNK_SIZE)

print(all_records[0])
print(len(all_records))
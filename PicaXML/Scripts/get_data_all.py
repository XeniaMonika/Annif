import requests
import time
from tqdm import tqdm
import xml.etree.ElementTree as ET
import os
from requests.exceptions import ChunkedEncodingError, ConnectionError

BASE_URL = "https://sru.k10plus.de/opac-de-627"
QUERY = "pica.spr=spa"
OUTPUT_FOLDER = "./PicaXML/Data/Spanish_ALL"
OUTPUT_FILE = "data_raw.xml"
PROGRESS_FILE = "./PicaXML/Data/Spanish_ALL/progress.txt"
CHUNK_SIZE = 100
REQUEST_DELAY = 2.0  # increased slightly to be gentler on the server
MAX_RETRIES = 5
RETRY_DELAY = 15


def get_total_records(base_url, query):
    params = {
        "version": "1.1",
        "operation": "searchRetrieve",
        "query": query,
        "maximumRecords": 1,
        "recordSchema": "picaxml"
    }
    response = requests.get(base_url, params=params, timeout=30)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    ns = {"srw": "http://www.loc.gov/zing/srw/"}
    return int(root.find("srw:numberOfRecords", ns).text)


def fetch_with_retry(base_url, params, max_retries=MAX_RETRIES, retry_delay=RETRY_DELAY):
    for attempt in range(max_retries):
        try:
            response = requests.get(base_url, params=params, timeout=60)
            response.raise_for_status()
            return response
        except (ChunkedEncodingError, ConnectionError) as e:
            if attempt < max_retries - 1:
                wait = retry_delay * (attempt + 1)  # back off progressively
                print(f"\nConnection error (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise


def save_progress(start_record):
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(start_record))


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            start = int(f.read().strip())
            print(f"Resuming from record {start}")
            return start
    return 1


def fetch_all_records(base_url, query, folder, output_file, chunk_size=100, delay=1.0):
    total = get_total_records(base_url, query)
    print(f"Total records found: {total}")

    ns = {"srw": "http://www.loc.gov/zing/srw/"}
    params = {
        "version": "1.1",
        "operation": "searchRetrieve",
        "query": query,
        "maximumRecords": chunk_size,
        "recordSchema": "picaxml"
    }

    os.makedirs(folder, exist_ok=True)
    output_path = os.path.join(folder, output_file)
    resume_from = load_progress()

    # open in append mode if resuming, write mode if starting fresh
    file_mode = "a" if resume_from > 1 else "w"
    count = 0

    with open(output_path, file_mode, encoding="utf-8") as f:
        if file_mode == "w":
            f.write("<records>\n")

        all_starts = range(1, total + 1, chunk_size)
        remaining_starts = [s for s in all_starts if s >= resume_from]

        for start in tqdm(remaining_starts, total=len(list(range(1, total + 1, chunk_size))),
                          initial=(resume_from - 1) // chunk_size):
            params["startRecord"] = start
            response = fetch_with_retry(base_url, params)

            root = ET.fromstring(response.content)
            for record in root.findall(".//srw:recordData", ns):
                f.write(ET.tostring(record, encoding="unicode"))
                f.write("\n")
                count += 1

            save_progress(start + chunk_size)  # save next start, not current
            time.sleep(delay)

        f.write("</records>")

    # clean up progress file on successful completion
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
        print("Progress file removed (download complete).")

    print(f"Downloaded {count} records")
    print(f"File saved in {output_path}")
    return count


if __name__ == "__main__":
    fetch_all_records(BASE_URL, QUERY, OUTPUT_FOLDER, OUTPUT_FILE, CHUNK_SIZE, REQUEST_DELAY)
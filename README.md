# Annif
This repository provides the code and datasets used to implement Annif for automated subject indexing at SUB Hamburg. It includes all components required to train, configure, and evaluate Annif for the library’s indexing workflows.

## Requirements

Install the required libraries with:

```bash
pip install requests tqdm
```

## Data

The data files are not tracked in this repository due to their size.
To regenerate them, run the following script from the `Scripts` folder:

```bash
cd Scripts
python get_data.py
```

This will fetch records in the PicaXML fromat from the K10plus SRU API and save them as XML files
in the following locations:

- `Data/Spanish/lsy_ni/data.xml`
- `Data/Spanish/lsy_ro/data.xml`
- `Data/Spanish/lsy_ip/data.xml`
- `Data/Spanish/ssg_7_34/data.xml`

The folders will be created automatically if they don't exist.

## Filtering data

To extract only records containing the GND keywords (Pica field `044K`), run `get_gnd_subset.py` from the repo root:

```bash
python Scripts/get_gnd_subset.py
```

This script reads `data.xml` from each source folder, keeps only records with `044K`, and writes the output to `Data/data_gnd.xml`.

## Finding duplicate records

To find duplicate records that share the same author and title run `find_duplicates_author_title.py` from the repo root. In order to find records that also share the same ISBN run `find_duplicates_author_title_isbn.py`

```bash
python Scripts/find_duplicates_author_title_isbn.py
```

The scripts print duplicate groups to the console and saves duplicate metadata to:

- `Data/Spanish_xml/duplicates_author_title.json`
or
- `Data/Spanish_xml/duplicates_author_title_isbn.json`

Use that JSON file to inspect duplicate records.


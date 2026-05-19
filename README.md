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

To extract only records containing the MARC `689` field, run `filter_data.py` from the repo root:

```bash
python Scripts/filter_data.py
```

This script reads `data.xml` from each source folder, keeps only records with `689`, and writes the output to `Data/data_filtered.xml`.

## Finding duplicate records

To find duplicate records that share the same author, title, and ISBN, run `find_duplicates.py` from the repo root:

```bash
python Scripts/find_duplicates.py
```

The script prints duplicate groups to the console and saves duplicate metadata to:

- `Data/Spanish_xml/duplicates_author_title_isbn.json`

Use that JSON file to inspect duplicate records.


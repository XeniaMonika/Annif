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

- `lsy_ni/data.xml`
- `lsy_ro/data.xml`
- `lsy_ip/data.xml`
- `ssg_7_34/data.xml`

The folders will be created automatically if they don't exist.

## Filtering data

To extract only records containing the GND keywords (Pica field `044K`), run `get_gnd_subset.py` from the repo root:

```bash
python Scripts/get_gnd_subset.py
```

This script reads `data.xml` from each source folder, keeps only records with `044K`, and writes the output to `Data/data_gnd.xml`.

## Transform data 

To transform the data from PICAXML to a format requested by Annif (here JSON Lines), run `transform_data.py` from the repo root. The file not only extracts the needed metadata from the XML structure, but also handles duplicate cases by merging titles with the same author, title, ISBN number and/or bibliographic level, or taking titles with the bigger amount of keywords when the bibliographic level of same-title records differ. The ready corpus in JSON Lines format is then saved as `corpus.jsonl` in the `data` folder.


```bash
python Scripts/trasform_data.py
```

## Inspect the corpus
In order to get an overview about the composition of the corpus run `get_stats.py`. This script provides information about the size of the corpus, the amount of abstracts, TOC present in the data, the length of titles, as well as about the distribution of keywords in the corpus. The results are then saved in the `corpus_stats.md` file.

```bash
python Scripts/get_stats.py
```
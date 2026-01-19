# Scoutbook Helper

Python tooling for processing Scoutbook advancement data. This script helps generate Court of Honor (CoH) and Advancement Report spreadsheets from Scoutbook exports.

## Installation

Ensure you have Python 3 installed. It is recommended to use a virtual environment.

```bash
pip install -r requirements.txt
```

## Usage

The script `scoutbook.py` takes several CSV files as input and can generate Excel spreadsheets for various purposes.

```bash
python3 scoutbook.py --advancement advancement_export.csv [advancement_export2.csv ...] [options]
```

### Options

*   `--advancement FILE [FILE ...]` (Required): One or more advancement record export CSV files from Scoutbook.
*   `--fixups FILE` (Optional): A CSV file containing name fixes. Format: `BSA Member ID, First Name, Last Name`.
*   `--roster FILE` (Optional): A CSV file of the troop roster.
*   `--coh OUTPUT_FILE.xlsx` (Optional): Generate a Court of Honor spreadsheet.
*   `--adv OUTPUT_FILE.xlsx` (Optional): Generate an Advancement Report spreadsheet.

### Example

To generate both a Court of Honor and an Advancement report:

```bash
python3 scoutbook.py --advancement advancement_export.csv --roster roster.csv --fixups name_fixups.csv --coh coh_report.xlsx --adv advancement_report.xlsx
```
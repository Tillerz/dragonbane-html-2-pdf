# Dragonbane PDF Character Filler

This repository converts Dragonbane character HTML pages into filled PDF character sheets.

## Overview

- Input HTML files are stored in `input/`.
- The script parses `character_data` blocks from each HTML and fills a PDF form.
- Each HTML file may contain multiple characters.
- Output PDFs are saved to `output/`.
- The empty fillable PDF template is located in `template/sheet.pdf`.

## Sources

- Character HTML generator: https://dbchargen-production.up.railway.app/generate
- Blank Dragonbane fillable character sheet: https://toybox-sw.blogspot.com/2024/04/dragonbane-fillable-character-sheets.html

## Requirements

- Python 3
- `PyPDF2`

If you use a virtual environment, activate it first.

### Install dependencies

```bash
python3 -m pip install PyPDF2
```

Or, if you are using a virtual environment:

```bash
# create venv
python3 -m venv .venv
# activate venv
source .venv/bin/activate
# install the library
python3 -m pip install PyPDF2
```

## Usage

1. Place your `.html` or `.htm` character files into the `input/` folder.
2. Make sure `template/sheet.pdf` contains the blank Dragonbane fillable PDF.
3. Run the batch processor:

```bash
./run.sh
```

This executes:

```bash
python ./scripts/pdf_field_mapping.py --batch --output-dir output
```

### Command options

- `--batch` : process all `*.html` and `*.htm` files in `input/`
- `--html <file>` : process a single HTML file
- `--output-dir <dir>` : set the output directory for filled PDFs
- `--list-html` : list available HTML files
- `--inspect` : print PDF field names and types from the template

Example:

```bash
python3 ./scripts/pdf_field_mapping.py --html input/char1.html --output-dir output
```

## Output filename format

Output PDFs are saved using this filename pattern:

```
<profession>-<STR>-<CON>-<AGL>-<INT>-<WIL>-<CHA>-<name>-<kin>.pdf
```

If the generated filename already exists, a numeric suffix is appended.

## Notes

- The script extracts base64-encoded `character_data` from each HTML block and fills the form using the provided PDF template.
- Multiple characters in a single HTML file are supported.
- The repository includes `run.sh` for a convenient batch run.

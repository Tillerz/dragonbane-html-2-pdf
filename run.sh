#!/usr/bin/bash

# activate venv
source .venv/bin/activate

# execute script
python ./scripts/pdf_field_mapping.py --batch --output-dir output

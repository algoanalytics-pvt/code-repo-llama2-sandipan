#!/bin/bash

# Step 1: Create the directory structure
mkdir -p locales/{en,ja}/LC_MESSAGES
echo "Step 1: Translation directories are created"

# Step 2: Extract translatable strings and generate base.pot
find . -name "*.py" -print0 | xargs -0 xgettext --language=Python --output=locales/base.pot --keyword=_gettext --from-code=UTF-8
echo "Step 2: Text for translation has been extracted from .py files"

# Step 3: Generate translation .po files using a Python script using googletrans
python3 translations/generate_translation_po_files.py
echo "Step 3: Translations for respective languages is done! .po files are generated!"

# Step 4: Compile .po files to .mo files for English (en) and Japanese (ja)
msgfmt -o locales/en/LC_MESSAGES/base.mo locales/en/LC_MESSAGES/base
msgfmt -o locales/ja/LC_MESSAGES/base.mo locales/ja/LC_MESSAGES/base
#echo "Machine readable files have been generated!"

echo "Final Step: Translation files have been generated and compiled!!!"

# make sure to make it executable 
# chmod +x generate_translations.sh

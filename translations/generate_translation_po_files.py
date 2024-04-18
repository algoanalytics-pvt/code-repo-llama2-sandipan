import polib
#pip install --upgrade googletrans==4.0.0-rc1
from googletrans import Translator

# Define target languages and their codes
target_languages = {"English": "en", "Japanese": "ja"}

# Initialize the Google Translator
translator = Translator()

# Load the .pot file
template = polib.pofile("locales/base.pot")  # Replace with your .pot file path

for language, lang_code in target_languages.items():
    # Create a .po file for the language
    po_file = polib.POFile()

    # Set the language code and name
    po_file.metadata = {
        "Language": lang_code,
        "Language-Team": language,
        "Content-Type": "text/plain; charset=UTF-8",
    }

    # Translate each entry in the .pot file
    for entry in template:
        translation = translator.translate(entry.msgid, src="en", dest=lang_code).text
        entry.msgstr = translation
        po_file.append(entry)

    # Save the .po file
    #po_file.save(f"locales/{lang_code}/LC_MESSAGES/{lang_code}.po")
    po_file.save(f"locales/{lang_code}/LC_MESSAGES/base.po")

print("Translation completed.")
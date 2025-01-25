import json

class Glossary:
    # Supported languages
    SUPPORTED_LANGUAGES = ['en', 'fi']

    """
    Get the glossary of the application in wanted language.
    lang_code: str - Language code of the glossary. Must be in ISO 639-1 format. Eg. 'en', 'fr', 'es', 'fi'...
    """

    def __init__(self, lang_code):
        if lang_code not in self.SUPPORTED_LANGUAGES:
            raise Exception(f'Language {lang_code} is not supported. Supported languages are: {self.SUPPORTED_LANGUAGES}')
        self.lang_code = lang_code
        self.glossary = None
    
    def load_glossary(self):
        """
        Load the glossary from json file.
        """
        # Create file path
        file_path = f'glossaries/glossary_{self.lang_code}.json'
        # Open file
        with open(file_path) as file:
            self.glossary = json.load(file)

        file.close()

    def get(self, word_identifier, lower = False):
        """
        Get the glossary from json file.
        """
        if (not self.glossary):
            self.load_glossary()

        # Get the word
        # Check if the word exists
        if self.glossary and word_identifier not in self.glossary:
            raise Exception(f'Word {word_identifier} not found in glossary.')

        if lower:
            return self.glossary[word_identifier].lower()

        return self.glossary[word_identifier]

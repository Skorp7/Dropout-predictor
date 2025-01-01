import sys
from Glossary import Glossary

class Validator:
    def __init__(self, glossary: Glossary):
        self.glossary = glossary

    def validate_environment(self):
        # Verify that the user is running Python 3.7 or higher
        result_str = self.check_python_version()
        # Verify that the required dependencies are installed
        result_str += '\n' + self.check_dependencies()

        return result_str

    def check_python_version(self):
        if sys.version_info.major >= 3 and sys.version_info.minor >= 10:
            return 'Python: OK'
        else:
            return 'Python: ' + self.glossary.get('higher_required') + self.glossary.get('minimum') + ' 3.10.'
        
    def check_dependencies(self):
        # Verify that the required dependencies are installed
        return_str = ''
        try:
            # Read the libraries from the essentials.txt file
            with open('essentials.txt', 'r') as file:
                libraries = file.readlines()

            # Strip any leading/trailing whitespace or newlines
            libraries = [lib.strip() for lib in libraries]

            missing_libraries = []

            # Check if each library is installed
            for lib in libraries:
                try:
                    # Attempt to import the library
                    __import__(lib)
                except ImportError:
                    missing_libraries.append(lib)

            if len(missing_libraries) > 0:
                return_str += self.glossary.get('not_found') + ':'
                for missing in missing_libraries:
                    return_str += f'\n- {missing} (' + self.glossary.get('or_sub_dependency') + ')'

                return return_str
            else:
                return self.glossary.get('others') + ': OK'
        except FileNotFoundError:
            return 'essentials.txt ' + self.glossary.get('not_found')

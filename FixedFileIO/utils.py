import re


class TransactionLimitError(Exception):
    """Exception raised when the maximum
     number of transactions is exceeded."""
    def __init__(self, limit, message="Too many transactions"):
        self.limit = limit
        self.message = message
        super().__init__(f"{message}: {limit}")


def get_values_as_dict(line, slices):
    values = {}
    for key, (start, end) in slices.items():
        values[key] = line[start:end].strip()
    return values


class Validation:
    def __init__(self, filepath):
        self.filepath = filepath

    def _validate_header(self, line):
        pass

    def _validate_transactions(self, lines):
        pass

    def _validate_footer(self, line):
        pass

    def run(self):
        with open(self.filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()

            results = [self._validate_header(lines[0]), self._validate_transactions(lines[1:-1]),
                       self._validate_footer(lines[-1])]

            if all(results):
                return True

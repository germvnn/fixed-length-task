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


def validate_structure(record):
    pass

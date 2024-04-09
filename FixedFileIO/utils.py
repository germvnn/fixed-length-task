def get_values_as_dict(line, slices):
    values = {}
    for key, (start, end) in slices.items():
        values[key] = line[start:end].strip()
    return values


def validate_structure(record):
    pass


def format_currency(value):
    pass

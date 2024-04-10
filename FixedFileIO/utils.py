import logging
import re

from . import constants as const


logger = logging.getLogger(__package__)


class TransactionLimitError(Exception):
    """Exception raised when the maximum
     number of transactions is exceeded."""
    def __init__(self, limit, message="Too many transactions"):
        self.limit = limit
        self.message = message
        super().__init__(f"{message}: {limit}")


def get_values_as_dict(line, slices) -> dict:
    """Extracts substrings from a line based on the provided
     slices and returns them as a dictionary."""
    values = {}
    for key, (start, end) in slices.items():
        values[key] = line[start:end].strip()
    return values


def format_record(record, slices) -> str:
    """Formats a single record for writing to the file based on slice definitions."""
    line = ''
    for field, (start, end) in slices.items():
        value = str(record.get(field, ''))
        length = end - start

        if field in ['Counter', 'Amount', 'Control sum']:
            value = value.zfill(length)
            line += value.rjust(length)
        else:
            line += value.ljust(length)
    return line


def check_fields_length(field_name, value) -> None:
    """Checks if the value for the given field name exceeds the maximum allowed length."""
    max_length = const.MAX_LENGTHS.get(field_name, 0)
    if len(str(value)) > max_length:
        logger.error(f"Value for {field_name} exceeds maximum length of {max_length}.")
        raise ValueError(f"Value for {field_name} is too long.")


def validate_field_value(field_name, value) -> None:
    """Checks if the value is validate"""
    validation_function = const.FIELD_VALIDATIONS.get(field_name, None)
    if validation_function and not validation_function(str(value)):
        logger.error(f"Invalid value for {field_name}: {value}")
        raise ValueError(f"Invalid value for {field_name}: {value}")


def success(log_message) -> bool:
    """Logs a success message and returns True."""
    logger.info(log_message)
    return True


def failure(log_message) -> bool:
    """Logs a success message and returns False."""
    logger.error(log_message)
    return False


class ValidationExecutor:
    """Class used for validation proper file format"""
    def __init__(self, filepath):
        self.filepath = filepath

    @staticmethod
    def _validate_line_length(line) -> bool:
        """Checks if line length is equal 120"""
        return False if len(line.rstrip('\n')) != 120 else True

    def validate_header(self, line) -> bool:
        """Validation of file's header"""
        slices = const.HEADER_SLICES

        if not self._validate_line_length(line):
            return failure(log_message=f"Required line length: 120 Actual: {len(line) - 1}")  # - \n

        # Get values of fields using constant slices
        field_id = line[slices['Field ID'][0]:slices['Field ID'][1]]
        name = line[slices['Name'][0]:slices['Name'][1]].strip()
        surname = line[slices['Surname'][0]:slices['Surname'][1]].strip()
        patronymic = line[slices['Patronymic'][0]:slices['Patronymic'][1]].strip()
        address = line[slices['Address'][0]:slices['Address'][1]].strip()
        logger.debug(f"Values: {field_id}, {name}, {surname}, {patronymic}, {address}")

        # Field ID validation
        if not re.match(r'^01$', field_id):
            return failure(log_message="Invalid Field ID in header.")

        # Name, Surname, Patronymic validation
        for key, item in {"Name": name, "Surname": surname, "Patronymic": patronymic}.items():
            if not re.match(r'^[A-Za-z\s]+$', item):
                return failure(log_message=f"Invalid {key} in header")

        # Address validation
        if not re.match(r'^[\w\s,.]+$', address):
            return failure(log_message="Invalid Address in header.")

        return success(log_message="Header is valid.")

    def validate_transactions(self, lines) -> bool:
        """Validation of file's transactions"""
        slices = const.TRANSACTIONS_SLICES

        # Check every line
        for line in lines:
            if not self._validate_line_length(line):
                return failure(log_message=f"Required line length: 120 Actual: {len(line) - 1}")  # - \n

            # Get values of fields using constant slices
            field_id = line[slices['Field ID'][0]:slices['Field ID'][1]]
            counter = line[slices['Counter'][0]:slices['Counter'][1]]
            amount = line[slices['Amount'][0]:slices['Amount'][1]]
            currency = line[slices['Currency'][0]:slices['Currency'][1]]

            logger.debug(f"Values: {field_id}, {counter}, {amount}, {currency}")

            # Field ID validation
            if not re.match(r'^02$', field_id):
                return failure(log_message="Invalid Field ID in transaction.")

            # Counter validation
            if not re.match(r'^\d{6}$', counter):
                return failure(log_message="Counter format is not correct.")

            # Amount validation
            if not re.match(r'^\d{12}$', amount):
                return failure(log_message="Amount format is not correct.")

            # Currency validation
            if currency not in const.CURRENCIES:
                return failure(log_message=f"Invalid currency '{currency}' in transaction.")

        return success(log_message="Transactions are valid.")

    def validate_footer(self, line, num_transactions, total_amount) -> bool:
        """Validation of file's footer"""
        slices = const.FOOTER_SLICES

        if not self._validate_line_length(line):
            return failure(log_message=f"Required line length: 120 Actual: {len(line) - 1}")  # - \n

        # Get values of fields using constant slices
        field_id = line[slices['Field ID'][0]:slices['Field ID'][1]]
        total_counter = line[slices['Total Counter'][0]:slices['Total Counter'][1]]
        control_sum = line[slices['Control sum'][0]:slices['Control sum'][1]]

        # Field ID validation
        if not re.match(r'^03$', field_id):
            return failure(log_message="Invalid Field ID in footer.")

        # Total Counter validation
        if not re.match(r'^\d{6}$', total_counter):
            return failure(log_message="Total Counter format is not correct.")
        if int(total_counter) != num_transactions:
            return failure(log_message=f"Total Counter does not match the number of transactions ({num_transactions}).")

        # Control Sum validation
        if not re.match(r'^\d{12}$', control_sum):
            return failure(log_message="Control Sum format is not correct.")
        if int(control_sum) != total_amount:
            return failure(log_message=f"Control Sum does not match the total amount of transactions ({total_amount}).")

        return success(log_message="Footer is valid.")

    def run(self) -> (bool, list):
        """Validation of whole file"""
        with open(self.filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()

            num_transactions = len(lines) - 2  # - (header+footer)

            # Indices of Amount field
            amount_start = const.TRANSACTIONS_SLICES['Amount'][0]
            amount_end = const.TRANSACTIONS_SLICES['Amount'][1]
            # Sum of transactions Amounts
            try:
                total_amount = sum(int(line[amount_start:amount_end]) for line in lines if line.startswith('02'))
            except ValueError:
                logger.error(f"Unavailable to count total_amount")
                total_amount = None

            # List of results of particular validations
            results = {self.validate_header(line=lines[0]),
                       self.validate_transactions(lines=lines[1:-1]),
                       self.validate_footer(line=lines[-1],
                                            num_transactions=num_transactions,
                                            total_amount=total_amount)}

            if all(results):
                return success(log_message=f"Validation OK. Results: {results}"), results
            return failure(log_message=f"Validation NOK. Results: {results}"), results

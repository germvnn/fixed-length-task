import logging

from . import constants as const
from . import utils


logger = logging.getLogger(__package__)


class FixedWidthHandler:
    """
       Handles reading, writing, and modifying fixed-width file format.

       Attributes:
           filepath (str): Path to the fixed-width file.
           field_id_header (str): Field ID for header records.
           field_id_transaction (str): Field ID for transaction records.
           field_id_footer (str): Field ID for footer records.
           transaction_limit (int): Maximum number of transaction records allowed.

       Methods:
           read_file: Reads the fixed-width file
                      and returns its content as structured data.
           write_file: Writes structured data back to the fixed-width file format.
           add_transaction: Adds a new transaction record to the file.
           update_field: Updates the value of a specific
                         field in a header, transaction, or footer record.
       """

    field_id_header: str
    field_id_transaction: str
    field_id_footer: str
    transaction_limit: int

    def __init__(self, filepath):
        """Initializes the handler with file path and default settings."""

        self.filepath = filepath
        self.field_id_header = '01'
        self.field_id_transaction = '02'
        self.field_id_footer = '03'
        self.transaction_limit = 20000

    def read_file(self) -> (dict, list, dict):
        """Reads the fixed-width file, returning the header, list of transactions, and footer."""

        header, transactions, footer = None, [], None
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                for line in file:
                    # Indices of Field ID
                    field_id = line[0:2]
                    if field_id == self.field_id_header:  # Header
                        header = utils.get_values_as_dict(line, const.HEADER_SLICES)
                        logger.debug(f"Load header: {header}")
                    elif field_id == self.field_id_transaction:  # Transaction
                        transaction = utils.get_values_as_dict(line, const.TRANSACTIONS_SLICES)
                        transactions.append(transaction)
                        logger.debug(f"Load transaction: {transaction}")
                    elif field_id == self.field_id_footer:  # Footer
                        footer = utils.get_values_as_dict(line, const.FOOTER_SLICES)
                        logger.debug(f"Load footer: {footer}")
        except Exception as e:
            logger.error(f"Failed to read file {self.filepath}: {e}")
            raise
        # Check whether there are no more than 20000 transactions
        if len(transactions) > self.transaction_limit:
            logger.error(f"Number of transactions reached limit - {self.transaction_limit}")
            raise utils.TransactionLimitError(self.transaction_limit)
        logger.info("File successfully loaded")
        return header, transactions, footer

    def _format_record(self, record, slices) -> str:
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

    def write_file(self, header, transactions, footer) -> None:
        """Writes the header, transactions, and footer back to the fixed-width file."""

        # Check whether there are no more than 20000 transactions
        if len(transactions) > self.transaction_limit:
            logger.error(f"Number of transactions reached limit - {self.transaction_limit}")
            raise utils.TransactionLimitError(self.transaction_limit)
        try:
            with open(self.filepath, 'w', encoding='utf-8') as file:
                # Header
                header_line = self._format_record(header, const.HEADER_SLICES)
                file.write(header_line + '\n')
                logger.debug(f"Write {header_line} into {self.filepath}")

                # Transactions
                for transaction in transactions:
                    transaction_line = self._format_record(transaction, const.TRANSACTIONS_SLICES)
                    file.write(transaction_line + '\n')
                    logger.debug(f"Write {transaction_line} into {self.filepath}")

                # Footer
                footer['Control sum'] = sum(int(transaction['Amount']) for transaction in transactions)
                footer_line = self._format_record(footer, const.FOOTER_SLICES)
                file.write(footer_line + '\n')
                logger.debug(f"Write {footer_line} into {self.filepath}")
        except Exception as e:
            logger.error(f"Failed to write file {self.filepath}: {e}")
            raise
        logger.info("File successfully wrote")

    def add_transaction(self, amount, currency) -> None:
        """Adds a new transaction record to the file."""

        if currency not in const.CURRENCIES:
            logger.error(const.CURRENCY_ERROR)
            raise ValueError(const.CURRENCY_ERROR)

        header, transactions, footer = self.read_file()

        # Next transaction's number
        next_counter = str(len(transactions) + 1).zfill(6)

        # Add new transaction to list
        new_transaction = {
            'Field ID': self.field_id_transaction,
            'Counter': next_counter,
            'Amount': f"{int(float(amount) * 100):012}",
            'Currency': currency,
            'Reserved': ''
        }
        transactions.append(new_transaction)
        logger.debug(f"Add transaction: {new_transaction}")

        # Update Total Counter
        footer['Total Counter'] = f"{len(transactions):06}"
        logger.debug(f"Set new Total Counter: {footer['Total Counter']}")
        self.write_file(header, transactions, footer)

    def _update_header_field(self, header, field_name, value) -> None:
        """Updates a field value in the header record."""

        if field_name not in const.HEADER_FIELDS:
            message = f"{field_name} is not a valid field for header."
            logger.error(message)
            raise ValueError(message)
        header[field_name] = value
        logger.info(f"Value of {field_name} successfully updated into {value}")

    def _update_transaction_field(self, transactions, field_name, value, counter) -> None:
        """Updates a field value in a specific transaction record."""

        if field_name not in const.TRANSACTION_FIELDS:
            message = f"{field_name} is not a valid field for transaction."
            logger.error(message)
            raise ValueError(message)
        for transaction in transactions:
            if transaction['Counter'] == counter:
                value = value if not field_name == 'Amount' else int(value * 100)
                transaction[field_name] = value
                logger.info(f"Value of {field_name} successfully updated into {value}")
                return
        message = f"No transaction with counter {counter} found."
        logger.error(message)
        raise ValueError(message)

    def _update_footer_field(self, footer, field_name, value) -> None:
        """Updates a field value in the footer record."""

        if field_name not in const.FOOTER_FIELDS:
            message = f"{field_name} is not a valid field for footer."
            logger.error(message)
            raise ValueError(message)
        footer[field_name] = value
        logger.info(f"Value of {field_name} successfully updated into {value}")

    def update_field(self, record_type, field_name, field_value, counter=None) -> None:
        """Updates a field value in header, transaction, or footer based on record type."""

        header, transactions, footer = self.read_file()

        if field_name == "Currency" and field_value not in const.CURRENCIES:
            raise ValueError(const.CURRENCY_ERROR)

        # Warn user about attempt of modifying auto fields
        if field_name in const.AUTO_FIELDS:
            logger.warning(f"Trying to update automatic measured or fixed field: '{field_name}'")

        # Attempt to convert value type to validate
        try:
            value = const.FIELD_TYPES[field_name](field_value)
        except ValueError:
            logger.error(f"Cannot convert {field_value} to {const.FIELD_TYPES[field_name]}.")
            raise

        match record_type:
            case 'header':
                self._update_header_field(header=header, field_name=field_name, value=value)
            case 'transaction':
                if counter is None:
                    raise ValueError("Counter is required for updating a transaction.")
                self._update_transaction_field(transactions=transactions,
                                               field_name=field_name,
                                               value=value,
                                               counter=counter)
            case 'footer':
                self._update_footer_field(footer=footer, field_name=field_name, value=value)
            case _:
                message = f"Unknown record type: {record_type}"
                logger.error(message)
                raise ValueError(message)
        self.write_file(header=header, transactions=transactions, footer=footer)

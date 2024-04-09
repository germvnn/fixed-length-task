from . import constants as const
from . import utils


class FixedWidthHandler:

    def __init__(self, filepath):
        self.filepath = filepath

    def read_file(self):
        header, transactions, footer = None, [], None
        with open(self.filepath, 'r', encoding='utf-8') as file:
            for line in file:
                field_id = line[0:2]
                if field_id == '01':  # Header
                    header = utils.get_values_as_dict(line, const.HEADER_SLICES)
                elif field_id == '02':  # Transaction
                    transaction = utils.get_values_as_dict(line, const.TRANSACTIONS_SLICES)
                    transaction.pop('Reserved', None)
                    transactions.append(transaction)
                elif field_id == '03':  # Footer
                    footer = utils.get_values_as_dict(line, const.FOOTER_SLICES)
                    footer.pop('Reserved', None)
        return header, transactions, footer

    def write_file(self, header, transactions, footer):
        pass

    def update_field(self, record_type, field_name, value):
        pass

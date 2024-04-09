import argparse
import json
from FixedFileIO.handler import FixedWidthHandler
from FixedFileIO import constants as const


def read_values(handler: FixedWidthHandler):
    header, transactions, footer = handler.read_file()
    print(header)

    currencies = set()

    for transaction in transactions:
        transaction.pop('Reserved', None)
        currencies.add(transaction['Currency'])
        print(transaction)
    footer.pop('Reserved', None)
    print(footer)

    if len(currencies) > 1:
        print(f"Control sum is not representative due to different currencies: {currencies}")


def add_transaction_cli(handler: FixedWidthHandler):
    while True:
        amount = input("Enter the transaction amount: ")
        try:
            amount = "{:.2f}".format(float(amount))
        except ValueError:
            print("Invalid amount. Please enter a numeric value.")
            continue

        currency = input("Enter the currency code: ").upper()
        if currency not in const.CURRENCIES:
            print(const.CURRENCY_ERROR)
            continue

        handler.add_transaction(amount=amount, currency=currency)
        break


def _load_field_permissions(filepath='configs/permissions.json'):
    with open(filepath, 'r') as file:
        return json.load(file)


def _save_field_permissions(settings, filepath='configs/permissions.json'):
    try:
        with open(filepath, 'w') as file:
            json.dump(settings, file, indent=4)
    except Exception as e:
        print(f"Saving configs failed due to: {e}")


def update_field_cli(handler: FixedWidthHandler):
    field_permissions = _load_field_permissions()

    record_type = input("Enter record to update (header|transaction): ")
    field_name = input("Enter field name: ").title()

    if not field_permissions.get(field_name, False):
        raise KeyError(f"Updating field '{field_name}' is not allowed.")

    field_value = input("Enter the new value: ")
    if field_name == "Currency" and field_value not in const.CURRENCIES:
        raise ValueError(const.CURRENCY_ERROR)
    counter = None
    if record_type == 'transaction':
        counter = input("Enter the transaction counter: ").zfill(6)
    try:
        handler.update_field(record_type=record_type,
                             field_name=field_name,
                             field_value=field_value if not field_name == "Currency" else field_value.upper(),
                             counter=counter)
    except KeyError:
        print(f"Field {field_name} does not exist in {record_type}.")
    except Exception as e:
        print(e)


def change_permissions():
    permissions = _load_field_permissions()
    print("Current field permissions:")
    for field, permission in permissions.items():
        print(f"{field}: {'Allowed' if permission else 'Blocked'}")
    field_to_change = input("Enter field name to change permission: ")
    if field_to_change in permissions:
        permissions[field_to_change] = not permissions[field_to_change]
        _save_field_permissions(permissions)
        print(f"Permission for {field_to_change} changed successfully.")
    else:
        print("Field name does not exist.")


def main():
    parser = argparse.ArgumentParser(description='CLI for Fixed File IO operations.')
    parser.add_argument('action', choices=['read', 'add', 'update', 'settings'], help='Action to perform.')
    parser.add_argument('filepath', help='Path to the fixed-width file.')

    args = parser.parse_args()
    handler = FixedWidthHandler(filepath=args.filepath)

    match args.action:
        case 'read':
            read_values(handler)
        case 'add':
            add_transaction_cli(handler)
        case 'update':
            update_field_cli(handler)
        case 'settings':
            change_permissions()


if __name__ == '__main__':
    main()

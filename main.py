import argparse
import json
import logging
import os
from datetime import datetime

from FixedFileIO.handler import FixedWidthHandler


logger = logging.getLogger(__name__)


def read_values(handler: FixedWidthHandler) -> None:
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


def add_transaction_cli(handler: FixedWidthHandler) -> None:
    amount = input("Enter the transaction amount: ")
    try:
        amount = "{:.2f}".format(float(amount))
    except ValueError:
        print("Invalid amount. Please enter a numeric value.")
        return

    currency = input("Enter the currency code: ").upper()

    handler.add_transaction(amount=amount, currency=currency)


def update_field_cli(handler: FixedWidthHandler) -> None:
    field_permissions = _load_field_permissions()

    record_type = input("Enter record to update: ")
    field_name = input("Enter field name: ").title()

    if field_permissions.get(field_name, False):
        raise KeyError(f"Updating field '{field_name}' is not allowed.")

    field_value = input("Enter the new value: ")
    counter = None
    if record_type == 'transaction':
        counter = input("Enter the transaction counter: ").zfill(6)
    handler.update_field(record_type=record_type,
                         field_name=field_name,
                         field_value=field_value if not field_name == "Currency" else field_value.upper(),
                         counter=counter)


def _load_field_permissions(filepath='configs/permissions.json') -> dict:
    with open(filepath, 'r') as file:
        return json.load(file)


def _save_field_permissions(settings, filepath='configs/permissions.json') -> None:
    try:
        with open(filepath, 'w') as file:
            json.dump(settings, file, indent=4)
    except Exception as e:
        print(f"Saving configs failed due to: {e}")


def change_permissions() -> None:
    permissions = _load_field_permissions()
    print("Current field permissions:")
    for field, permission in permissions.items():
        print(f"{field}: {'Blocked' if permission else 'Allowed'}")
    field_to_change = input("Enter field name to change permission: ")
    if field_to_change in permissions:
        permissions[field_to_change] = not permissions[field_to_change]
        _save_field_permissions(permissions)
        print(f"Permission for {field_to_change} changed successfully.")
    else:
        print("Field name does not exist.")


def setup_logger() -> None:
    # Create logs directory if not exists
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Set logs filename with current time
    current_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    log_filename = f"logs/processing_{current_time}.log"

    # Logger configs
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description='CLI for Fixed File IO operations.')
    parser.add_argument('action', choices=['read', 'add', 'update', 'settings'], help='Action to perform.')
    parser.add_argument('filepath', help='Path to the fixed-width file.')

    args = parser.parse_args()
    setup_logger()
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

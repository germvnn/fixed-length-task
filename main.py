import argparse
import json
import logging
import os
from datetime import datetime

from FixedFileIO.handler import FixedWidthHandler
from FixedFileIO.utils import ValidationExecutor


logger = logging.getLogger("main")


def read_values_cli(handler: FixedWidthHandler) -> None:
    """CLI function for display file's values"""
    header, transactions, footer = handler.read_file()
    print(header)

    # Initialize set of currencies
    currencies = set()

    # Popping 'Reserved' field
    for transaction in transactions:
        transaction.pop('Reserved', None)
        currencies.add(transaction['Currency'])
        print(transaction)
    footer.pop('Reserved', None)
    print(footer)

    # Display currency warning
    if len(currencies) > 1:
        logger.warning(f"Control sum is not representative due to different currencies: {currencies}")


def add_transaction_cli(handler: FixedWidthHandler) -> None:
    """CLI function for managing add transactions"""
    # Check whether amount is numeric
    try:
        amount = int(input("Enter the transaction amount (last two digits represent fractions eg. 100 -> 1.00): "))
    except ValueError:
        print("Invalid amount. Please enter a numeric value.")
        return

    currency = input("Enter the currency code: ").upper()  # Make currency insertion flexible
    handler.add_transaction(amount=amount, currency=currency)


def update_field_cli(handler: FixedWidthHandler) -> None:
    """CLI function for managing update file fields"""
    # Load permissions for updating fields
    field_permissions = _load_field_permissions()

    record_type = input("Enter record to update: ")
    field_name = input("Enter field name: ").title()

    if field_permissions.get(field_name, False):
        raise KeyError(f"Updating field '{field_name}' is not allowed.")

    field_value = input("Enter the new value: ")
    # Initialize counter as None for no transaction fields
    counter = None
    if record_type == 'transaction':
        counter = input("Enter the transaction counter: ").zfill(6)
    handler.update_field(record_type=record_type,
                         field_name=field_name,
                         field_value=field_value if not field_name == "Currency" else field_value.upper(),
                         counter=counter)


def _load_field_permissions(filepath: str = 'configs/permissions.json') -> dict:
    """Auxiliary function for load permissions"""
    with open(filepath, 'r') as file:
        return json.load(file)


def _save_field_permissions(settings: dict, filepath: str = 'configs/permissions.json') -> None:
    """Auxiliary function for save permissions"""
    try:
        with open(filepath, 'w') as file:
            json.dump(settings, file, indent=4)
    except Exception as e:
        print(f"Saving configs failed due to: {e}")


def change_permissions_cli() -> None:
    """CLI function for managing file fields permissions"""
    permissions = _load_field_permissions()
    print("Current field permissions:")

    # Display current permissions
    for field, permission in permissions.items():
        print(f"{field}: {'Blocked' if permission else 'Allowed'}")
    decision = input("Do you want to change settings? (y/n) ")
    if decision == 'y':
        field_to_change = input("Enter field name to change permission: ")
        if field_to_change in permissions:
            permissions[field_to_change] = not permissions[field_to_change]
            _save_field_permissions(permissions)
            print(f"Permission for {field_to_change} changed successfully.")
        else:
            print("Field name does not exist.")
    elif decision == 'n':
        return
    else:
        print("Invalid response")


def setup_logger(filepath: str) -> None:
    # Create logs directory if not exists
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Set logs filename with current time
    current_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    log_filename = f"logs/{os.path.basename(filepath)}_{current_time}.log"

    # Logger configs
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s - %(name)s - {filepath} -%(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )


def main() -> None:
    # Parser configs
    parser = argparse.ArgumentParser(description='CLI for Fixed File IO operations.')
    parser.add_argument('action', choices=['read', 'add', 'update', 'settings'], help='Action to perform.')
    parser.add_argument('filepath', help='Path to the fixed-width file.')

    # Initializations
    args = parser.parse_args()

    # Validation not needed for changing settings
    if args.action == 'settings':
        change_permissions_cli()
        return

    setup_logger(filepath=args.filepath)
    handler = FixedWidthHandler(filepath=args.filepath)
    validation = ValidationExecutor(filepath=args.filepath)

    # Validation check
    status, _ = validation.run()
    if not status:
        return

    # Main
    match args.action:
        case 'read':
            read_values_cli(handler)
        case 'add':
            add_transaction_cli(handler)
        case 'update':
            update_field_cli(handler)


if __name__ == '__main__':
    main()

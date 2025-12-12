import argparse
from lib.utils import welcome_cli, display_item_cli, add_item_cli, update_item_cli, delete_item_cli, fetch_inventory_cli

def main():
    parser = argparse.ArgumentParser(description="Inventory Manager CLI")
    subparsers = parser.add_subparsers()

    add_item_parser = subparsers.add_parser("add-item", help="Add a new item to inventory")
    add_item_parser.add_argument("name")
    add_item_parser.add_argument("price")
    add_item_parser.add_argument("stock")
    add_item_parser.set_defaults(func=add_item_cli)

    display_all_parser = subparsers.add_parser("display-inventory", help="Display all items in the inventory")
    display_all_parser.set_defaults(func=welcome_cli)

    show_item_parser = subparsers.add_parser("display-item", help="Display one item from the inventory")
    show_item_parser.add_argument("id")
    show_item_parser.set_defaults(func=display_item_cli)

    update_item_parser = subparsers.add_parser("update-item", help="Update an item's price and stock")
    update_item_parser.add_argument("id")
    update_item_parser.add_argument("price")
    update_item_parser.add_argument("stock")
    update_item_parser.set_defaults(func=update_item_cli)

    delete_item_parser = subparsers.add_parser("delete-item", help="Delete an item from the inventory")
    delete_item_parser.add_argument("id")
    delete_item_parser.set_defaults(func=delete_item_cli)

    item_api_parser = subparsers.add_parser("find-item", help="Find an item from the OpenFoodFacts API")
    item_api_parser.add_argument("barcode")
    item_api_parser.set_defaults(func=fetch_inventory_cli)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
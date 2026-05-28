import argparse
import json
import sys


def main(argv: list[str] | None = None) -> int:
    """
    Parses command line arguments and executes the requested action on a JSONL file.

    Supported commands:
    - list: Lists all action receipts in the file.
    - show <id>: Displays the full details of a specific receipt by its ID.

    Required flag:
    - -f, --file: Path to the JSONL file containing action receipts.
    """
    parser = argparse.ArgumentParser(description="AI Agent Action Receipt Viewer")
    parser.add_argument("-f", "--file", type=str, help="Path to the JSONL file")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List command
    subparsers.add_parser("list", help="List all action receipts")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show a specific action receipt")
    show_parser.add_argument("id", type=str, help="The ID of the receipt to show")

    try:
        args = parser.parse_args(argv)
    except SystemExit:
        # Handle argparse exit (e.g. -h) gracefully for the return code
        return 0

    if not args.command:
        parser.print_help()
        return 0

    # Determine input source
    file_path = args.file

    try:
        if file_path:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()
        else:
            # Read from stdin if -f is absent
            lines = sys.stdin.readlines()
    except OSError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    # Parse JSONL lines
    receipts = []
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        try:
            receipts.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"Error: Malformed JSON on line {i}", file=sys.stderr)
            return 1

    if args.command == "list":
        if not receipts:
            print("No receipts found.")
            return 0

        print(f"{'ID':<20} | {'Action':<20} | {'Status':<10}")
        print("-" * 55)
        for r in receipts:
            rid = r.get("id", "N/A")
            action = r.get("action", "N/A")
            status = r.get("status", "N/A")
            print(f"{rid:<20} | {action:<20} | {status:<10}")
        return 0

    elif args.command == "show":
        target_id = args.id
        found = False
        for r in receipts:
            if r.get("id") == target_id:
                print(json.dumps(r, indent=2))
                found = True
                break

        if not found:
            print(f"Error: Receipt with ID '{target_id}' not found.", file=sys.stderr)
            return 1
        return 0

    return 0

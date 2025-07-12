#!/usr/bin/env python3

import sys
import subprocess  # Added explicitly to avoid NameError
from src.parser import create_parser
from src.utils import check_root_permissions
from src.handlers import handle_search, handle_install, handle_remove
from src.copr import search_copr

def main():
    parser = create_parser()
    args = parser.parse_args()

    # Handle help options
    if args.help and not args.command:
        parser.print_help()
        sys.exit(0)
    elif args.help_dnf:
        subprocess.run(["dnf5", "--help"], check=False)
        sys.exit(0)
    elif not args.command:
        subprocess.run(["dnf5"] + sys.argv[1:], check=False)
        return

    # Handle specific commands
    if args.command == "search":
        handle_search(args.args[0] if args.args else "")
    elif args.command == "copr" and args.args and args.args[0] == "search":
        search_copr(args.args[1] if len(args.args) > 1 else "")
    elif args.command in ["install", "i", "in"]:
        handle_install(args.args)
    elif args.command in ["remove", "rm"]:
        force = "--force" in args.args or "-f" in args.args
        packages = [arg for arg in args.args if arg not in ["--force", "-f"]]
        handle_remove(packages, force)
    elif args.command in ["upgrade", "ug", "upg"]:
        subprocess.run(["dnf5", "upgrade"] + args.args, check=True)
    elif args.command in ["list", "ls"]:
        subprocess.run(["dnf5", "list"] + args.args, check=True)
    elif args.command in ["download", "dw"]:
        cmd = ["dnf5", "download"] + args.args
        subprocess.run(cmd, check=True)
    elif args.command == "cl":
        subprocess.run(["dnf5", "clean", "all"], check=True)
    else:
        # Pass unrecognized commands and their arguments to dnf5
        subprocess.run(["dnf5", args.command] + args.args, check=False)

if __name__ == "__main__":
    # Check and handle root permissions before parsing arguments
    check_root_permissions(sys.argv)
    try:
        main()
    except KeyboardInterrupt:
        print("\nCommand cancelled by user.")
        sys.exit(0)

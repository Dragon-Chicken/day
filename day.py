#!/usr/bin/env python3

import sys
import subprocess
from src.parser import create_parser
from src.utils import check_root
from src.handlers import search, install, remove
from src.copr import search_copr

def _run_dnf_passthrough(command, args):
    subprocess.run(["dnf5", command] + args, check=False)

def main():
    parser = create_parser()
    args = parser.parse_args()

    if not args.command or args.help:
        parser.print_help() if args.help else _run_dnf_passthrough("", sys.argv[1:])
        sys.exit(0)
    if args.help_dnf:
        subprocess.run(["dnf5", "--help"], check=False)
        sys.exit(0)

    match args.command:
        case "search":
            search(args.args[0] if args.args else "")
        case "copr" if args.args and args.args[0] == "search":
            search_copr(args.args[1] if len(args.args) > 1 else "")
        case cmd if cmd in {"install", "i", "in"}:
            install(args.args)
        case cmd if cmd in {"remove", "rm"}:
            force = "--force" in args.args or "-f" in args.args
            packages = [arg for arg in args.args if arg not in {"--force", "-f"}]
            remove(packages, force)
        case cmd if cmd in {"upgrade", "ug", "upg", "list", "ls", "download", "dw"}:
            subprocess.run(["dnf5", cmd] + args.args, check=True)
        case "cl":
            subprocess.run(["dnf5", "clean", "all"], check=True)
        case cmd:
            _run_dnf_passthrough(cmd, args.args)

if __name__ == "__main__":
    check_root(sys.argv)
    try:
        main()
    except KeyboardInterrupt:
        print("\nCommand cancelled by user.")
        sys.exit(0)

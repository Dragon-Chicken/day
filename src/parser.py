import argparse

def create_parser():
    parser = argparse.ArgumentParser(
        description="Day - A DNF wrapper with extra features",
        epilog="Commands: search, copr search, install (i, in), remove (rm, -f/--force), "
               "upgrade (ug, upg), list (ls), download (dw), cl, advisory <subcommand>, "
               "copr <subcommand>, history <subcommand>, or any dnf5 command. "
               "Use 'day --help-dnf' for DNF5 help.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False
    )
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message")
    parser.add_argument("--help-dnf", action="store_true", help="Show DNF5 help")
    parser.add_argument("command", nargs="?", help="Command to execute")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Additional arguments")
    return parser

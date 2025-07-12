import argparse

def create_parser():
    parser = argparse.ArgumentParser(
        description="Day - A DNF wrapper with extra features",
        epilog="""
Available commands:
  search                Search for packages (falls back to COPR if no matches)
  copr search           Search COPR repositories
  install, i, in        Install packages (supports COPR projects)
  remove, rm            Remove packages (-f/--force for rpm -e --nodeps)
  upgrade, ug, upg      Upgrade packages
  list, ls              List packages
  download, dw          Download packages
  cl                    Clean all cached data
  advisory <subcommand> Manage advisories (e.g., summary, list, info)
  copr <subcommand>     Manage COPR repositories (e.g., enable, add, remove)
  history <subcommand>  Manage transaction history (e.g., list, info, undo)
  <other dnf5 commands> Pass through to dnf5 (e.g., group, module, check)

For DNF5 help, use: day --help-dnf
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False
    )
    parser.add_argument("--help", "-h", action="store_true", help="Show this help message and exit")
    parser.add_argument("--help-dnf", action="store_true", help="Show DNF5 help message")
    parser.add_argument("command", nargs="?", help="Command to execute")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Additional arguments")
    return parser

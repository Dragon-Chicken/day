#!/usr/bin/env python3

import argparse
import subprocess
import sys
import requests
from bs4 import BeautifulSoup
from termcolor import colored
import os
import time

# there wont be much comments
# in this codebase since it should all be
# self explanatory


def search_copr(query):
    base_url = "https://copr.fedorainfracloud.org/coprs/fulltext/?projectname="
    url = base_url + query
    print(f"Fetching {url}...")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.ConnectionError:
        print("Error: Failed to connect to the server. Please check your internet connection.")
        return
    except requests.Timeout:
        print("Error: Request timed out. Please try again later.")
        return
    except requests.HTTPError as e:
        print(f"Error: HTTP error occurred - {e.response.status_code} {e.response.reason}")
        return
    except requests.RequestException as e:
        print(f"Error: Failed to fetch URL - {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    projects = [p for p in soup.find_all('a', class_='list-group-item') 
                if p.get('href', '').startswith('/coprs/') and p.find('h3')]

    print(f"Search results of {colored(query, 'green')}:")
    if not projects:
        print("No projects found.")
        return

    for project in projects:
        name = project.find('h3').text.strip()
        name_highlighted = name.replace(query, colored(query, 'green'))

        description_span = project.find('span', class_='list-group-item-text')
        description = description_span.text.strip() if description_span else "No description available."
        description_words = description.split()[:10]
        description = ' '.join(description_words) + '...'

        ul = project.find('ul', class_='list-inline')
        archs = set()
        if ul:
            small_tags = ul.find_all('small')
            for small in small_tags:
                for arch in small.text.split(','):
                    arch = arch.strip()
                    if arch:
                        archs.add(arch)
            archs_str = ', '.join(sorted(archs))
            archs_formatted = f"( {archs_str} )" if archs else "( )"
        else:
            archs_formatted = "( )"

        print("--------------------------------------------")
        print(f"   {name_highlighted} {archs_formatted} : {description}")
    print("--------------------------------------------")

def handle_search(query):
    try:
        result = subprocess.run(["dnf5", "search", query], check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        if "No match for argument:" in e.stderr:
            print("No packages found in standard repositories.")
            response = input("Would you like to search COPR repositories? (Y/n): ").strip().lower()
            if response in ("y", ""):
                search_copr(query)
        else:
            print(f"Error during search: {e.stderr}")

def handle_install(packages):
    copr_projects = []
    install_list = []

    for pkg in packages:
        if '/' in pkg:
            copr_projects.append(pkg)
            package_name = pkg.split('/')[-1]
            install_list.append(package_name)
        else:
            install_list.append(pkg)

    for project in copr_projects:
        try:
            print(f"Enabling COPR project {project}...")
            subprocess.run(["dnf5", "copr", "enable", project, "-y"], check=True, capture_output=True, text=True, timeout=30)
        except subprocess.CalledProcessError as e:
            print(f"Error enabling COPR project {project}: {e.stderr}")
            return
        except subprocess.TimeoutExpired:
            print(f"Error: Timed out enabling COPR project {project}.")
            return

    try:
        print(f"Installing packages: {' '.join(install_list)}...")
        subprocess.run(["dnf5", "install"] + install_list + ["-y"], check=True, capture_output=True, text=True, timeout=300)
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e.stderr}")
    except subprocess.TimeoutExpired:
        print("Error: Package installation timed out.")

def handle_remove(packages, force):
    # Check for DNF database lock
    lock_file = "/var/lib/dnf/rpm.lock"
    if not force and os.path.exists(lock_file):
        print(f"Error: DNF database is locked ({lock_file}). Another process may be using DNF.")
        print("Try waiting a moment or run 'sudo rm -f /var/lib/dnf/rpm.lock' if you're sure no other DNF process is running.")
        return

    try:
        if force:
            print(f"Forcing removal of packages: {' '.join(packages)}...")
            # Verify packages exist before running rpm -e
            for pkg in packages:
                result = subprocess.run(["rpm", "-q", pkg], capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Error: Package {pkg} is not installed.")
                    return
            subprocess.run(["rpm", "-e", "--nodeps"] + packages, check=True, capture_output=True, text=True, timeout=30)
        else:
            print(f"Removing packages with DNF: {' '.join(packages)}...")
            subprocess.run(["dnf5", "remove", "-y"] + packages, check=True, text=True, timeout=300)
    except subprocess.CalledProcessError as e:
        print(f"Error removing packages: {e.stderr}")
    except subprocess.TimeoutExpired:
        print("Error: Package removal timed out. Try running 'sudo dnf5 remove' manually or check for system issues.")
    except PermissionError:
        print("Error: Permission denied. Run 'day remove' with sudo (e.g., 'sudo day remove <package>').")

def main():
    parser = argparse.ArgumentParser(description="Day - A DNF wrapper with extra features",
                                     add_help=False)
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    search_parser = subparsers.add_parser("search", help="Search for packages")
    search_parser.add_argument("query", help="Search query")

    copr_parser = subparsers.add_parser("copr", help="COPR commands")
    copr_subparsers = copr_parser.add_subparsers(dest="copr_command")
    copr_search_parser = copr_subparsers.add_parser("search", help="Search COPR repositories")
    copr_search_parser.add_argument("query", help="Search query")

    install_parser = subparsers.add_parser("install", aliases=["i", "in"], help="Install packages")
    install_parser.add_argument("packages", nargs="+", help="Packages to install")

    remove_parser = subparsers.add_parser("remove", aliases=["rm"], help="Remove packages")
    remove_parser.add_argument("packages", nargs="+", help="Packages to remove")
    remove_parser.add_argument("-f", "--force", action="store_true", help="Force remove without checking dependencies")

    upgrade_parser = subparsers.add_parser("upgrade", aliases=["ug", "upg"], help="Upgrade packages")
    upgrade_parser.add_argument("packages", nargs="*", help="Packages to upgrade")

    list_parser = subparsers.add_parser("list", aliases=["ls"], help="List packages")
    list_parser.add_argument("options", nargs="*", help="Options for list command")

    download_parser = subparsers.add_parser("download", aliases=["dw"], help="Download packages")
    download_parser.add_argument("packages", nargs="+", help="Packages to download")
    download_parser.add_argument("--srpm", action="store_true", help="Download source RPMs")
    download_parser.add_argument("--debuginfo", action="store_true", help="Download debuginfo RPMs")

    cl_parser = subparsers.add_parser("cl", help="Clean all cached data")

    args, unknown_args = parser.parse_known_args()

    try:
        if not args.command:
            subprocess.run(["dnf5"] + sys.argv[1:], check=False)
            return

        if args.command == "search":
            handle_search(args.query)
        elif args.command == "copr" and args.copr_command == "search":
            search_copr(args.query)
        elif args.command in ["install", "i", "in"]:
            handle_install(args.packages)
        elif args.command in ["remove", "rm"]:
            handle_remove(args.packages, args.force)
        elif args.command in ["upgrade", "ug", "upg"]:
            subprocess.run(["dnf5", "upgrade"] + args.packages + unknown_args, check=True)
        elif args.command in ["list", "ls"]:
            subprocess.run(["dnf5", "list"] + args.options + unknown_args, check=True)
        elif args.command in ["download", "dw"]:
            cmd = ["dnf5", "download"] + args.packages + unknown_args
            if args.srpm:
                cmd.append("--srpm")
            if args.debuginfo:
                cmd.append("--debuginfo")
            subprocess.run(cmd, check=True)
        elif args.command == "cl":
            subprocess.run(["dnf5", "clean", "all"], check=True)
        else:
            subprocess.run(["dnf5", args.command] + unknown_args, check=False)
    except KeyboardInterrupt:
        print("\nCommand cancelled by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()

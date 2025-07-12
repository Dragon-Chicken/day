import subprocess
import os
from .copr import search_copr

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
    lock_file = "/var/lib/dnf/rpm.lock"
    if not force and os.path.exists(lock_file):
        print(f"Error: DNF database is locked ({lock_file}). Another process may be using DNF.")
        print("Try waiting a moment or run 'sudo rm -f /var/lib/dnf/rpm.lock' if you're sure no other DNF process is running.")
        return

    try:
        if force:
            print(f"Forcing removal of packages: {' '.join(packages)}...")
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

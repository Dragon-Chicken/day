import subprocess
import os
import configparser
from .copr import search_copr

def get_default_yes():
    """Read defaultyes from /etc/dnf/dnf.conf and return True if set to 'True'."""
    config = configparser.ConfigParser()
    try:
        config.read('/etc/dnf/dnf.conf')
        return config.getboolean('main', 'defaultyes', fallback=False)
    except (configparser.Error, FileNotFoundError):
        return False

def confirm_action(prompt, default_yes=False):
    """Prompt user for confirmation with (Y/n) or (y/N) based on default_yes."""
    suffix = "(Y/n)" if default_yes else "(y/N)"
    response = input(f"{prompt} {suffix}: ").strip().lower()
    if default_yes:
        return response in ("y", "")  # Default to Yes
    return response == "y"  # Default to No

def handle_search(query):
    try:
        result = subprocess.run(
            ["dnf5", "search", "--color=always", query],
            check=True,
            capture_output=True,
            text=True
        )
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
    default_yes = get_default_yes()
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
        if not confirm_action(f"Enable COPR project {project}?", default_yes):
            print(f"Skipped enabling COPR project {project}.")
            return
        try:
            print(f"Enabling COPR project {project}...")
            process = subprocess.Popen(
                ["dnf5", "copr", "enable", "--color=always", project, "-y"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, "PYTHONUNBUFFERED": "1"}
            )
            while True:
                stdout_line = process.stdout.readline()
                stderr_line = process.stderr.readline()
                if stdout_line:
                    print(stdout_line, end='', flush=True)
                if stderr_line:
                    print(stderr_line, end='', flush=True)
                if process.poll() is not None and not stdout_line and not stderr_line:
                    break
            stdout, stderr = process.communicate()
            if stdout:
                print(stdout, end='', flush=True)
            if stderr:
                print(stderr, end='', flush=True)
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, process.args, stdout, stderr)
        except subprocess.CalledProcessError as e:
            print(f"Error enabling COPR project {project}: {e.stderr}")
            return
        except subprocess.TimeoutExpired:
            print(f"Error: Timed out enabling COPR project {project}.")
            return

    if not confirm_action(f"Install packages: {' '.join(install_list)}?", default_yes):
        print("Installation cancelled.")
        return

    try:
        print(f"Installing packages: {' '.join(install_list)}...")
        process = subprocess.Popen(
            ["dnf5", "install", "--color=always"] + install_list + ["-y"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "PYTHONUNBUFFERED": "1"}
        )
        while True:
            stdout_line = process.stdout.readline()
            stderr_line = process.stderr.readline()
            if stdout_line:
                print(stdout_line, end='', flush=True)
            if stderr_line:
                print(stderr_line, end='', flush=True)
            if process.poll() is not None and not stdout_line and not stderr_line:
                break
        stdout, stderr = process.communicate()
        if stdout:
            print(stdout, end='', flush=True)
        if stderr:
            print(stderr, end='', flush=True)
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args, stdout, stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e.stderr}")
    except subprocess.TimeoutExpired:
        print("Error: Package installation timed out.")

def handle_remove(packages, force):
    default_yes = get_default_yes()
    lock_file = "/var/lib/dnf/rpm.lock"
    if not force and os.path.exists(lock_file):
        print(f"Error: DNF database is locked ({lock_file}). Another process may be using DNF.")
        print("Try waiting a moment or run 'sudo rm -f /var/lib/dnf/rpm.lock' if you're sure no other DNF process is running.")
        return

    if not confirm_action(f"Remove packages: {' '.join(packages)}?", default_yes):
        print("Removal cancelled.")
        return

    try:
        if force:
            print(f"Forcing removal of packages: {' '.join(packages)}...")
            for pkg in packages:
                result = subprocess.run(["rpm", "-q", pkg], capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Error: Package {pkg} is not installed.")
                    return
            process = subprocess.Popen(
                ["rpm", "-e", "--nodeps"] + packages,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(timeout=30)
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, process.args, stdout, stderr)
        else:
            print(f"Removing packages with DNF: {' '.join(packages)}...")
            process = subprocess.Popen(
                ["dnf5", "remove", "--color=always", "-y"] + packages,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, "PYTHONUNBUFFERED": "1"}
            )
            while True:
                stdout_line = process.stdout.readline()
                stderr_line = process.stderr.readline()
                if stdout_line:
                    print(stdout_line, end='', flush=True)
                if stderr_line:
                    print(stderr_line, end='', flush=True)
                if process.poll() is not None and not stdout_line and not stderr_line:
                    break
            stdout, stderr = process.communicate()
            if stdout:
                print(stdout, end='', flush=True)
            if stderr:
                print(stderr, end='', flush=True)
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, process.args, stdout, stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error removing packages: {e.stderr}")
    except subprocess.TimeoutExpired:
        print("Error: Package removal timed out. Try running 'sudo dnf5 remove' manually or check for system issues.")
    except PermissionError:
        print("Error: Permission denied. Run 'day remove' with sudo (e.g., 'sudo day remove <package>').")

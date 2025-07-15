import subprocess
import os
import configparser
from .copr import search_copr

def defaultyes():
    config = configparser.ConfigParser()
    try:
        config.read('/etc/dnf/dnf.conf')
        return config.getboolean('main', 'defaultyes', fallback=False)
    except (configparser.Error, FileNotFoundError):
        return False

def prompt(message, default_yes=False):
    suffix = "(Y/n)" if default_yes else "(y/N)"
    response = input(f"{message} {suffix}: ").strip().lower()
    return response in ("y", "") if default_yes else response == "y"

def _run_dnf_command(command, timeout=300):
    process = subprocess.Popen(
        command,
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
        raise subprocess.CalledProcessError(process.returncode, command, stdout, stderr)

def search(query):
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
            if prompt("Search COPR repositories?", default_yes=True):
                search_copr(query)
        else:
            print(f"Search failed: {e.stderr}")

def install(packages):
    default_yes = defaultyes()
    copr_projects = []
    install_list = []

    for pkg in packages:
        if '/' in pkg:
            copr_projects.append(pkg)
            install_list.append(pkg.split('/')[-1])
        else:
            install_list.append(pkg)

    for project in copr_projects:
        if not prompt(f"Enable COPR project {project}?", default_yes):
            print(f"Skipped COPR project {project}.")
            return
        try:
            print(f"Enabling COPR project {project}...")
            _run_dnf_command(["dnf5", "copr", "enable", "--color=always", project, "-y"], timeout=30)
        except subprocess.CalledProcessError as e:
            print(f"Failed to enable COPR project {project}: {e.stderr}")
            return
        except subprocess.TimeoutExpired:
            print(f"Timed out enabling COPR project {project}.")
            return

    if not prompt(f"Install packages: {' '.join(install_list)}?", default_yes):
        print("Installation cancelled.")
        return

    try:
        print(f"Installing packages: {' '.join(install_list)}...")
        _run_dnf_command(["dnf5", "install", "--color=always"] + install_list + ["-y"])
    except subprocess.CalledProcessError as e:
        print(f"Installation failed: {e.stderr}")
    except subprocess.TimeoutExpired:
        print("Installation timed out.")

def remove(packages, force):
    default_yes = defaultyes()
    lock_file = "/var/lib/dnf/rpm.lock"
    if not force and os.path.exists(lock_file):
        print(f"DNF database locked at {lock_file}. Another process may be using DNF.")
        print("Wait a moment or run 'sudo rm -f /var/lib/dnf/rpm.lock' if safe.")
        return

    if not prompt(f"Remove packages: {' '.join(packages)}?", default_yes):
        print("Removal cancelled.")
        return

    try:
        if force:
            print(f"Forcing removal of packages: {' '.join(packages)}...")
            for pkg in packages:
                result = subprocess.run(["rpm", "-q", pkg], capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Package {pkg} is not installed.")
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
            _run_dnf_command(["dnf5", "remove", "--color=always", "-y"] + packages)
    except subprocess.CalledProcessError as e:
        print(f"Removal failed: {e.stderr}")
    except subprocess.TimeoutExpired:
        print("Removal timed out. Try 'sudo dnf5 remove' manually.")
    except PermissionError:
        print("Permission denied. Run 'day remove' with sudo (e.g., 'sudo day remove <package>').")

import os
import sys

# Commands that require root privileges (modify system state)
root_required_commands = [
    "install", "i", "in", "remove", "rm", "upgrade", "ug", "upg", "downgrade",
    "reinstall", "swap", "clean", "cl", "makecache", "distro-sync", "autoremove",
    "group", "module", "mark", "repo", "copr", "advisory"
]

def check_root_permissions(argv):
    if len(argv) > 1:
        cmd = argv[1]
        # Require root for root_required_commands, but exclude 'copr search'
        if cmd in root_required_commands and (cmd != "copr" or (len(argv) > 2 and argv[2] != "search")):
            if os.geteuid() != 0:
                print("This command requires root permissions. Re-running with sudo...")
                os.execvp("sudo", ["sudo"] + argv)

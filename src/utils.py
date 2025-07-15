import os
import sys

need_root = {
    "install", "i", "in", "remove", "rm", "upgrade", "ug", "upg", "downgrade",
    "reinstall", "swap", "clean", "cl", "makecache", "distro-sync", "autoremove",
    "group", "module", "mark", "repo", "copr", "advisory"
}

def check_root(argv):
    if len(argv) > 1 and argv[1] in need_root and (argv[1] != "copr" or len(argv) > 2 and argv[2] != "search"):
        if os.geteuid() != 0:
            print("Root permissions required. Re-running with sudo...")
            os.execvp("sudo", ["sudo"] + argv)

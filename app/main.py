import argparse
import sys
from .installer import add, remove
from .rebuild import rebuild
from .settings import initialize_settings
from .edit_settings import edit_settings

def main():
    initialize_settings()
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["add", "remove", "rebuild", "settings"])
    parser.add_argument("package", nargs="?")
    parser.add_argument("--method", choices=["nix_environment", "flatpak", "home_manager"], default=None)
    args = parser.parse_args()

    if args.action == "add":
        if not args.package:
            sys.stderr.write("Error: You must specify a package to install.\n")
            sys.exit(1)
        add(args.package, args.method)

    elif args.action == "remove":
        if not args.package:
            sys.stderr.write("Error: You must specify a package to uninstall.\n")
            sys.exit(1)
        remove(args.package, args.method)

    elif args.action == "rebuild":
        rebuild()

    elif args.action == "settings":
        edit_settings()


if __name__ == "__main__":
    main()

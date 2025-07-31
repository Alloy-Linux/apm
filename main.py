import argparse
import sys
from app import install, uninstall
from app.rebuild import rebuild_system
from app.settings import initialize_settings
from app.edit_settings import edit_settings

def main():
    initialize_settings()
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["install", "uninstall", "update", "settings"])
    parser.add_argument("package", nargs="?")
    parser.add_argument("--method", choices=["nix_environment", "flatpak", "home_manager"], default=None)
    args = parser.parse_args()

    if args.action == "install":
        if not args.package:
            sys.stderr.write("Error: You must specify a package to install.\n")
            sys.exit(1)
        install(args.package, args.method)
        rebuild_system(args.method)

    elif args.action == "uninstall":
        if not args.package:
            sys.stderr.write("Error: You must specify a package to uninstall.\n")
            sys.exit(1)
        uninstall(args.package, args.method)
        rebuild_system(args.method)

    elif args.action == "update":
        sys.stderr.write("Coming soon\n")
        sys.exit(1)
    
    elif args.action == "settings":
        edit_settings()


if __name__ == "__main__":
    main()
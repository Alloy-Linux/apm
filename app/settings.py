import json
from pathlib import Path
import os
import sys
import pwd

SETTINGS_PATH = Path(__file__).parent.parent / "settings.json"

def get_user_home():
    if os.geteuid() == 0:

        sudo_uid = os.environ.get("SUDO_UID")
        if sudo_uid:
            return Path(pwd.getpwuid(int(sudo_uid)).pw_dir)

        sudo_user = os.environ.get("SUDO_USER")
        if sudo_user:
            return Path(f"/home/{sudo_user}")

    return Path.home()


DEFAULT_SETTINGS = {
    "flake_location": "~/Documents/nix-config",
    "installation_files": {
        "nix_environment": "~/Documents/nix-config/apps/nixos-packages.nix",
        "flatpak": "~/Documents/nix-config/apps/flatpak-packages.nix",
        "home_manager": "~/Documents/nix-config/apps/home-manager-packages.nix"
    },
    "default_install_method": "home_manager",
    "rebuild_command": "sudo nixos-rebuild switch --flake ~/Documents/nix-config"
    }


def initialize_settings():
    if not SETTINGS_PATH.exists():
        print(f"Creating default settings file at {SETTINGS_PATH}")
        with open(SETTINGS_PATH, "w") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)

    try:
        with open(SETTINGS_PATH, "r") as f:
            data = json.load(f)
        for key, value in DEFAULT_SETTINGS.items():
            if key not in data or (key == "default_install_method" and data[key] != value):
                data[key] = value
            elif key == "installation_files":
                for sub_key, sub_value in DEFAULT_SETTINGS["installation_files"].items():
                    if sub_key not in data[key] or data[key][sub_key] != sub_value:
                        data[key][sub_key] = sub_value

        if "flake_location" not in data:
            sys.stderr.write("Error: Missing 'flake_location' in settings.json\n")
            sys.exit(1)

        

        with open(SETTINGS_PATH, "w") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        sys.stderr.write(f"Error initializing settings: {e}\n")
        sys.exit(1)


def load_settings():
    with open(SETTINGS_PATH, "r") as f:
        return json.load(f)

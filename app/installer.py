import subprocess
import json
import sys
from pathlib import Path

from .settings import load_settings, get_user_home

def add(pkg_name: str, method: str = None):
    settings = load_settings()
    method = method or settings.get("default_install_method")
    user_home = get_user_home()

    if method not in ["nix_environment", "flatpak", "home_manager"]:
        sys.stderr.write(f"Installation method '{method}' is not supported.\n")
        sys.exit(1)

    matches = []
    if method in ["nix_environment", "home_manager"]:
        try:
            result = subprocess.run(
                ["nix", "search", "nixpkgs", pkg_name, "--json"],
                capture_output=True,
                text=True,
                check=True
            )
            packages = json.loads(result.stdout)
            for attr, pkg_info in packages.items():
                if "pname" in pkg_info and pkg_name.lower() in pkg_info["pname"].lower():
                    matches.append((attr, pkg_info))
        except subprocess.CalledProcessError as e:
            sys.stderr.write(f"Failed to search package: {e.stderr}\n")
            sys.exit(1)
    elif method == "flatpak":
        try:
            result = subprocess.run(
                ["flatpak", "search", pkg_name, "--user"],
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split('\t')
                if len(parts) >= 4 and (pkg_name.lower() in parts[0].lower() or pkg_name.lower() in parts[2].lower()):
                    matches.append((parts[2], {"pname": parts[0], "description": parts[1], "appId": parts[2], "origin": parts[5]}))
        except subprocess.CalledProcessError as e:
            sys.stderr.write(f"Failed to search package: {e.stderr}\n")
            sys.exit(1)

    if not matches:
        sys.stderr.write(f"No matches found for '{pkg_name}'\n")
        return

    print("Found:")
    for idx, (attr, pkg) in enumerate(matches):
        print(f"{idx + 1}: {pkg.get('pname', 'N/A')} - {pkg.get('description', '')[:80]}")
    try:
        choice = int(input("Pick a number (0 to cancel): "))
        if choice < 1 or choice > len(matches):
            print("Cancelled.")
            return
        selected_attr, selected_pkg = matches[choice - 1]
    except ValueError:
        sys.stderr.write("Invalid selection.\n")
        return

    if method == "nix_environment":
        nix_env_file_path = Path(settings["installation_files"]["nix_environment"].replace("~", str(user_home)))
        try:
            nix_env_content = nix_env_file_path.read_text()
        except FileNotFoundError:
            sys.stderr.write(f"Error: file not found at {nix_env_file_path}!\n")
            return
        except Exception as e:
            sys.stderr.write(f"Error reading Nix environment file: {e}\n")
            return

        package_name = selected_attr.split(".")[-1]

        lines = nix_env_content.splitlines(keepends=True)
        insert_line_str = "  environment.systemPackages = with pkgs; ["
        end_list_str = "  ];"
        found_insert_index = -1
        found_end_index = -1
        package_already_exists = False

        for i, line in enumerate(lines):
            if insert_line_str in line:
                found_insert_index = i
            if found_insert_index != -1 and end_list_str in line:
                found_end_index = i
                break

        if found_insert_index == -1 or found_end_index == -1:
            sys.stderr.write(
                f"Error: Could not find package list in {nix_env_file_path}\n"
                f"Expected to find:\n{insert_line_str}\n...\n{end_list_str}\n"
            )
            return

        for i in range(found_insert_index + 1, found_end_index):
            stripped_line = lines[i].strip()
            if stripped_line == package_name or stripped_line.startswith(f"{package_name} #"):
                package_already_exists = True
                break

        if package_already_exists:
            print(f"{package_name} already exists in {nix_env_file_path}, skipping addition.")
            return

        new_line = f"    {package_name}\n"
        lines.insert(found_end_index, new_line)

        try:
            backup_path = nix_env_file_path.with_suffix(".bak")
            backup_path.write_text(nix_env_content)

            nix_env_file_path.write_text("".join(lines))
            print(f"Successfully added {package_name} to {nix_env_file_path}")

            return
        except Exception as e:
            sys.stderr.write(f"Failed to write changes to {nix_env_file_path}: {e}\n")
            return

    elif method == "home_manager":
        hm_file_path = Path(settings["installation_files"]["home_manager"].replace("~", str(user_home)))
        try:
            hm_content = hm_file_path.read_text()
        except FileNotFoundError:
            sys.stderr.write(f"Error: file not found at {hm_file_path}\n")
            return
        except Exception as e:
            sys.stderr.write(f"Error reading home-manager file: {e}\n")
            return

        package_name = selected_attr.split(".")[-1]

        lines = hm_content.splitlines(keepends=True)
        insert_line_str = "  home.packages = with pkgs; ["
        end_list_str = "  ];"
        found_insert_index = -1
        found_end_index = -1
        package_already_exists = False

        for i, line in enumerate(lines):
            if insert_line_str in line:
                found_insert_index = i
            if found_insert_index != -1 and end_list_str in line:
                found_end_index = i
                break

        if found_insert_index == -1 or found_end_index == -1:
            sys.stderr.write(
                f"Error: Could not find package list in {hm_file_path}\n"
                f"Expected to find:\n{insert_line_str}\n...\n{end_list_str}\n"
            )
            return

        for i in range(found_insert_index + 1, found_end_index):
            stripped_line = lines[i].strip()
            if stripped_line == package_name or stripped_line.startswith(f"{package_name} #"):
                package_already_exists = True
                break

        if package_already_exists:
            print(f"{package_name} already exists in {hm_file_path}, skipping addition.")
            return

        new_line = f"    {package_name}\n"
        lines.insert(found_end_index, new_line)

        try:
            backup_path = hm_file_path.with_suffix(".bak")
            backup_path.write_text(hm_content)

            hm_file_path.write_text("".join(lines))
            print(f"Successfully added {package_name} to {hm_file_path}")

            return
        except Exception as e:
            sys.stderr.write(f"Failed to write changes to {hm_file_path}: {e}\n")
            return
    elif method == "flatpak":
        flatpak_file_path = Path(settings["installation_files"]["flatpak"].replace("~", str(user_home)))
        try:
            flatpak_content = flatpak_file_path.read_text()
        except FileNotFoundError:
            sys.stderr.write(f"Error: Flatpak configuration file not found at {flatpak_file_path}\n")
            return
        except Exception as e:
            sys.stderr.write(f"Error reading Flatpak file: {e}\n")
            return

        app_id = selected_attr
        origin = selected_pkg.get("origin", "flathub")

        if f'appId = "{app_id}"' in flatpak_content:
            print(f"{app_id} already exists in {flatpak_file_path}, skipping addition.")
            return

        new_package_line = f'    {{ appId = "{app_id}"; origin = "{origin}"; }}\n'

        lines = flatpak_content.splitlines(keepends=True)
        insert_line_str = "  services.flatpak.packages = ["
        end_list_str = "  ];"
        found_insert_index = -1
        found_end_index = -1

        for i, line in enumerate(lines):
            if insert_line_str in line:
                found_insert_index = i
            if found_insert_index != -1 and end_list_str in line:
                found_end_index = i
                break
        
        if found_insert_index == -1 or found_end_index == -1:
            sys.stderr.write(
                f"Error: Could not find package list in {flatpak_file_path}\n"
                f"Expected to find:\n{insert_line_str}\n...\n{end_list_str}\n"
            )
            return

        lines.insert(found_end_index, new_package_line)

        try:
            backup_path = flatpak_file_path.with_suffix(".bak")
            backup_path.write_text(flatpak_content)

            flatpak_file_path.write_text("".join(lines))
            print(f"Successfully added {app_id} to {flatpak_file_path}")

            return
        except Exception as e:
            sys.stderr.write(f"Failed to write changes to {flatpak_file_path}: {e}\n")
            return

def remove(pkg_name: str, method: str = None):
    settings = load_settings()
    method = method or settings.get("default_install_method")
    user_home = get_user_home()

    if method not in ["nix_environment", "flatpak", "home_manager"]:
        sys.stderr.write(f"Removal method '{method}' is not supported.\n")
        sys.exit(1)

    if method == "nix_environment":
        nix_env_file_path = Path(settings["installation_files"]["nix_environment"].replace("~", str(user_home)))
        try:
            nix_env_content = nix_env_file_path.read_text()
        except FileNotFoundError:
            sys.stderr.write(f"Error: file not found at {nix_env_file_path}\n")
            return
        except Exception as e:
            sys.stderr.write(f"Error reading file at: {e}\n")
            return

        lines = nix_env_content.splitlines(keepends=True)
        package_found = False
        new_lines = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line == pkg_name or stripped_line.startswith(f"{pkg_name} #"):
                package_found = True
                continue
            new_lines.append(line)

        if not package_found:
            print(f"{pkg_name} not found in {nix_env_file_path}, nothing to do.")
            return

        try:
            backup_path = nix_env_file_path.with_suffix(".bak")
            backup_path.write_text(nix_env_content)

            nix_env_file_path.write_text("".join(new_lines))
            print(f"Successfully removed {pkg_name} from {nix_env_file_path}")
            return
        except Exception as e:
            sys.stderr.write(f"Failed to write changes to {nix_env_file_path}: {e}\n")
            return

    elif method == "home_manager":
        hm_file_path = Path(settings["installation_files"]["home_manager"].replace("~", str(user_home)))
        try:
            hm_content = hm_file_path.read_text()
        except FileNotFoundError:
            sys.stderr.write(f"Error: file not found at {hm_file_path}\n")
            return
        except Exception as e:
            sys.stderr.write(f"Error reading file: {e}\n")
            return

        lines = hm_content.splitlines(keepends=True)
        package_found = False
        new_lines = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line == pkg_name or stripped_line.startswith(f"{pkg_name} #"):
                package_found = True
                continue
            new_lines.append(line)

        if not package_found:
            print(f"{pkg_name} not found in {hm_file_path}, nothing to do.")
            return

        try:
            backup_path = hm_file_path.with_suffix(".bak")
            backup_path.write_text(hm_content)

            hm_file_path.write_text("".join(new_lines))
            print(f"Successfully removed {pkg_name} from {hm_file_path}")
            return
        except Exception as e:
            sys.stderr.write(f"Failed to write changes to {hm_file_path}: {e}\n")
            return
    elif method == "flatpak":
        flatpak_file_path = Path(settings["installation_files"]["flatpak"].replace("~", str(user_home)))
        try:
            flatpak_content = flatpak_file_path.read_text()
        except FileNotFoundError:
            sys.stderr.write(f"Error: file not found at {flatpak_file_path}\n")
            return
        except Exception as e:
            sys.stderr.write(f"Error reading file: {e}\n")
            return

        lines = flatpak_content.splitlines(keepends=True)
        package_found = False
        new_lines = []
        for line in lines:
            if f'appId = "{pkg_name}"' in line:
                package_found = True
                continue
            new_lines.append(line)

        if not package_found:
            print(f"{pkg_name} not found in {flatpak_file_path}, nothing to do.")
            return

        try:
            backup_path = flatpak_file_path.with_suffix(".bak")
            backup_path.write_text(flatpak_content)

            flatpak_file_path.write_text("".join(new_lines))
            print(f"Successfully removed {pkg_name} from {flatpak_file_path}")

            return
        except Exception as e:
            sys.stderr.write(f"Failed to write changes to {flatpak_file_path}: {e}\n")
            return
# APM - Alloy Package Manager

APM is a simple tool that helps you install software through the command line, but still get the benefits of declarative config files.

## License

This project is free to use and share. It's covered by the GNU General Public License v3.0. You can read the full details in the [LICENSE](LICENSE) file.

## What It Does

*   **Simple Commands:** Use one command to install, remove, or update your apps. No more editing config files.
*   **Works with Your Setup:** Connects with different package managers like Nix (`nix-environment`, `home-manager`) and Flatpak.
*   **Automatic Updates:** After you install or remove a program, APM automatically updates your system to apply the changes.
*   **Smart Search:** If you search for a program and APM finds a few with similar names, it will show you a list so you can pick the correct one.

## Settings

To change your settings, you can either edit the `settings.json` file directly or use the `settings` command:

```bash
python main.py settings
```


**Settings Explained:**

*   `flake_location`: The path to your Nix flake configuration.
*   `installation_files`: The paths to the configuration files for your package managers.
*   `default_install_method`: The main way you want to install software (e.g., `home_manager`).
*   `rebuild_command`: The command APM should run to update your system after you make changes.

## How to Use APM

### Add a Program

To install a new program, just tell APM to `install` it:

```bash
python main.py install <package-name>
```

If you want to use a specific method (like `flatpak` instead of your default), you can do this:

```bash
python main.py install <package-name> --method flatpak
```

### Remove a Program

To get rid of a program, use the `uninstall` command:

```bash
python main.py uninstall <package-name>
```

## How to Help

Want to help make APM better? You can report bugs or suggest new ideas by opening an issue on the GitHub page.

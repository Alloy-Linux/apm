import json

from app.settings import load_settings, SETTINGS_PATH


def edit_settings():
    settings = load_settings()

    while True:
        print("\nSelect a setting to edit:")
        for i, (key, value) in enumerate(settings.items()):
            if isinstance(value, dict):
                print(f"{i+1}. {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    - {sub_key}: {sub_value}")
            else:
                print(f"{i+1}. {key}: {value}")

        print(f"{len(settings) + 1}. Exit")

        try:
            choice = int(input("Enter your choice: "))
            if choice == len(settings) + 1:
                break
            elif 1 <= choice <= len(settings):
                key_to_edit = list(settings.keys())[choice - 1]
                if isinstance(settings[key_to_edit], dict):
                    print(f"\nSelect a sub-setting of '{key_to_edit}' to edit:")
                    sub_keys = list(settings[key_to_edit].keys())
                    for i, sub_key in enumerate(sub_keys):
                        print(f"{i+1}. {sub_key}")
                    print(f"{len(sub_keys) + 1}. Back")
                    sub_choice = int(input("Enter your choice: "))
                    if sub_choice == len(sub_keys) + 1:
                        continue
                    elif 1 <= sub_choice <= len(sub_keys):
                        sub_key_to_edit = sub_keys[sub_choice - 1]
                        new_value = input(f"Enter new value for {sub_key_to_edit}: ")
                        settings[key_to_edit][sub_key_to_edit] = new_value
                else:
                    new_value = input(f"Enter new value for {key_to_edit}: ")
                    settings[key_to_edit] = new_value
                
                with open(SETTINGS_PATH, "w") as f:
                    json.dump(settings, f, indent=4)
                print("Settings updated successfully!")
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

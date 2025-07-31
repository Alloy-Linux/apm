import subprocess
import sys
from .settings import load_settings, get_user_home

def rebuild_system(method: str = None):
    settings = load_settings()
    method = method or settings.get("default_install_method")
    rebuild_command = settings.get("rebuild_command")

    if not rebuild_command:
        print("No rebuild command specified in settings. Skipping rebuild.")
        return

    user_home = get_user_home()
    rebuild_command = rebuild_command.replace("~", str(user_home))

    print(f"Executing rebuild command: {rebuild_command}")
    try:
        process = subprocess.Popen(rebuild_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break
            if output:
                print(output.strip().decode())

        while True:
            error_output = process.stderr.readline()
            if error_output == b'' and process.poll() is not None:
                break
            if error_output:
                sys.stderr.write(error_output.strip().decode() + '\n')

        rc = process.poll()
        if rc == 0:
            print("Rebuild completed successfully.")
        else:
            sys.stderr.write(f"Rebuild command failed with exit code {rc}\n")
            sys.exit(1)
            
    except Exception as e:
        sys.stderr.write(f"An error occurred during rebuild: {e}\n")
        sys.exit(1)

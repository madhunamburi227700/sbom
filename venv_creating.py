import subprocess
import sys
import platform
import shutil
from dependency import install_dependencies

def setup(env_name="sbom-env", project_path=None):

    venv_path = env_name
    print(f"\nCreating venv for project at: {project_path}")

    # Step 1: Check Python version
    print("\nStep 1: Check Python version")
    subprocess.run([sys.executable, "--version"], check=True)

    # Step 2: Create venv in current folder
    print(f"\nStep 2: Creating venv '{env_name}' in current folder")
    subprocess.run(["uv", "venv", env_name], check=True)

    # Step 3: Install dependencies from project path
    if project_path:
        install_dependencies(env_name, project_path)

    # Step 4: Show activation instructions
    system = platform.system()
    if system == "Windows":
        print(f"\nTo activate venv: {env_name}\\Scripts\\activate")
    else:
        print(f"\nTo activate venv: source {env_name}/bin/activate")

    # **Return the venv path so main.py can use it**
    return venv_path


def remove_venv(venv_path):
    print(f"\nRemoving virtual environment folder: {venv_path}")
    shutil.rmtree(venv_path, ignore_errors=True)
    print("Virtual environment removed successfully.")
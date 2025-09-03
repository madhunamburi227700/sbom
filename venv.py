import subprocess
import sys
import shutil
import os
import platform

def setup(env_name="sbom-env", project_path=None):
    venv_path = env_name
    print(f"\nCreating venv for project at: {project_path}")

    # Step 1: Check Python version
    print("\nStep 1: Check Python version")
    subprocess.run([sys.executable, "--version"], check=True)

    # Step 2: Create venv in current folder
    print(f"\nStep 2: Creating venv '{env_name}' in current folder")
    subprocess.run(["uv", "venv", env_name], check=True)

    # Step 3: Find the Python executable inside the venv
    system = platform.system()
    python_exec = os.path.join(
        venv_path,
        "Scripts" if system == "Windows" else "bin",
        "python.exe" if system == "Windows" else "python"
    )

    # Step 4: Ensure pip is installed
    print("\nStep 3: Ensuring pip is available")
    subprocess.run([python_exec, "-m", "ensurepip", "--upgrade"], check=True)

    # Step 5: Upgrade pip, setuptools, and wheel inside venv
    print("\nStep 4: Upgrading pip, setuptools, and wheel")
    subprocess.run([python_exec, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], check=True)

    # Step 6: Show pip version
    print("\nStep 5: Checking pip version")
    subprocess.run([python_exec, "-m", "pip", "--version"], check=True)

    return venv_path

def remove_venv(venv_path):
    print(f"\nRemoving virtual environment folder: {venv_path}")
    shutil.rmtree(venv_path, ignore_errors=True)
    print("Virtual environment removed successfully.")

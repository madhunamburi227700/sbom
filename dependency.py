import os
import subprocess
import platform

def install_dependencies(env_name, project_path):
    """
    Recursively search for pyproject.toml or requirements.txt in the given project folder,
    ignoring virtual environments and site-packages, and install dependencies into the
    venv in the current working folder.
    """
    system = platform.system()
    python_exec = os.path.join(
        os.getcwd(),
        env_name,
        "Scripts" if system == "Windows" else "bin",
        "python.exe" if system == "Windows" else "python"
    )

    # Common venv folder names to skip
    venv_dirs = {"venv", ".venv", "env", ".env"}
    site_packages_dirs = {"Lib", "lib", "site-packages"}

    pyproject_files = []
    requirements_files = []

    for root, dirs, files in os.walk(project_path):
        # Skip virtual env and site-packages folders
        dirs[:] = [d for d in dirs if d not in venv_dirs and not any(sp in root for sp in site_packages_dirs)]

        if "pyproject.toml" in files:
            pyproject_files.append(os.path.join(root, "pyproject.toml"))
        if "requirements.txt" in files:
            requirements_files.append(os.path.join(root, "requirements.txt"))

    if pyproject_files:
        for pyproject in pyproject_files:
            print(f"Found pyproject.toml → {pyproject}, compiling and installing dependencies...")
            subprocess.run([
                "uv", "pip", "compile", "--all-extras", pyproject, "-o", "all-dep.txt"
            ], check=True)
            subprocess.run([
                "uv", "pip", "install", "--requirements", "all-dep.txt", "--python", python_exec
            ], check=True)

    elif requirements_files:
        for req_file in requirements_files:
            print(f"Found requirements.txt → {req_file}, installing dependencies...")
            subprocess.run([
                "uv", "pip", "install", "--requirements", req_file, "--python", python_exec
            ], check=True)

    else:
        print(f"No pyproject.toml or requirements.txt found in {project_path} (excluding venvs and site-packages). Skipping dependencies.")

    # Always install pipdeptree
    print("\nInstalling pipdeptree...")
    subprocess.run([
        "uv", "pip", "install", "pipdeptree", "--python", python_exec
    ], check=True)
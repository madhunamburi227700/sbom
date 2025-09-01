import os
import subprocess
import platform

def generate_dependency_tree(env_path, output_file="deps.json"):
    """Generate a dependency tree in JSON format using pipdeptree."""
    system = platform.system()
    python_exec = os.path.join(
        env_path,
        "Scripts" if system == "Windows" else "bin",
        "python.exe" if system == "Windows" else "python"
    )

    print(f"\nGenerating dependency tree into {output_file}...")
    with open(output_file, "w") as f:
        subprocess.run(
            [python_exec, "-m", "pipdeptree", "--json"],
            stdout=f,
            check=True
        )
    print(f"Dependency tree saved to {output_file}")

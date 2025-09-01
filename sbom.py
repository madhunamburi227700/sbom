import os
import subprocess
import platform

def generate_sbom(env_path, output_file="sbom_p.json"):
    """Install cyclonedx-bom and generate SBOM from the virtual environment."""
    system = platform.system()
    python_exec = os.path.join(
        env_path,
        "Scripts" if system == "Windows" else "bin",
        "python.exe" if system == "Windows" else "python"
    )

    print("\nInstalling cyclonedx-bom...")
    subprocess.run([
        "uv", "pip", "install", "cyclonedx-bom", "--python", python_exec
    ], check=True)

    print(f"\nGenerating SBOM into {output_file}...")
    # Run cyclonedx-py from inside the venv
    subprocess.run([
        python_exec, "-m", "cyclonedx_py", "venv", "-o", output_file
    ], check=True)

    print(f"SBOM saved to {output_file}")

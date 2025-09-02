import os
import subprocess
import platform

def get_python_exec(env_name):
    system = platform.system()
    return os.path.join(
        os.getcwd(),
        env_name,
        "Scripts" if system == "Windows" else "bin",
        "python.exe" if system == "Windows" else "python"
    )

def generate_sbom(env_name, requirements_file, output_file):
    python_exec = get_python_exec(env_name)

    print("\n🔧 Installing cyclonedx-bom in virtual environment...")
    subprocess.run([
        "uv", "pip", "install", "cyclonedx-bom", "--python", python_exec
    ], check=True)

    print(f"\n📦 Generating SBOM from '{requirements_file}' → '{output_file}'...")
    subprocess.run([
        python_exec, "-m", "cyclonedx_py", "requirements",
        requirements_file,
        "--output-file", output_file
    ], check=True)

    print(f"\n✅ SBOM successfully saved to '{output_file}'")

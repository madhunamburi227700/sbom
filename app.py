import os
import sys
import json
import re
import subprocess
import time
import shutil
import tempfile
import platform

# ----------------------------
# Utility Functions
# ----------------------------
def normalize_name_auto(name):
    name = name.lower().replace("_", ".").replace("-", ".")
    return re.sub(r"\.+", ".", name).strip(".")

def is_python_project(path):
    return any(os.path.exists(os.path.join(path, f)) for f in ["pyproject.toml", "requirements.txt", "setup.py"])

def cleanup_temp_dir():
    temp_dirs = [os.path.join(tempfile.gettempdir(), d) for d in os.listdir(tempfile.gettempdir()) if d.startswith("pip-")]
    for d in temp_dirs:
        try:
            shutil.rmtree(d, ignore_errors=True)
        except Exception:
            pass

def run_with_retry(cmd, cwd=None, retries=3, delay=5, env=None, show_output=False, capture_output=False):
    for attempt in range(1, retries + 1):
        try:
            cleanup_temp_dir()
            print(f"\n🔹 Running command: {' '.join(cmd)} (attempt {attempt}/{retries})")
            result = subprocess.run(
                cmd,
                cwd=cwd,
                check=True,
                env=env,
                stdout=subprocess.PIPE if capture_output else None,
                stderr=subprocess.PIPE if capture_output else None,
                text=True
            )
            if capture_output:
                print(f"✅ Command output captured ({len(result.stdout.splitlines())} lines)")
                return result.stdout
            print("✅ Command succeeded")
            return None
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Command failed (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                print(f"Retrying in {delay}s...")
                time.sleep(delay)
            else:
                print(f"❌ Command failed after {retries} attempts: {' '.join(cmd)}")
                if capture_output:
                    print("Output:", e.output)
                    print("Error:", e.stderr)
                raise

def validate_file(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        raise ValueError(f"File '{path}' is missing or empty.")
    print(f"✅ Validated file: {path}")

# ----------------------------
# Python Version Selection
# ----------------------------
PYTHON_ORDER = ["3.11", "3.10", "3.13"]

def find_python_in_order():
    for ver in PYTHON_ORDER:
        candidates = [f"python{ver}", f"python{ver[0]}"]
        for exe in candidates:
            try:
                output = subprocess.check_output([exe, "--version"], stderr=subprocess.STDOUT, text=True)
                if output.startswith(f"Python {ver}"):
                    print(f"✅ Using Python {ver} at {exe}")
                    return exe
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
    print(f"⚠️ None of the preferred versions found, using current Python {sys.version_info.major}.{sys.version_info.minor}")
    return sys.executable

# ----------------------------
# Virtual Environment
# ----------------------------
def create_venv(venv_name=".sbom-env"):
    python_exe = find_python_in_order()
    run_with_retry([python_exe, "-m", "venv", venv_name], show_output=True)
    print(f"✅ Virtual environment created at: {venv_name} using {python_exe}")
    return venv_name

def remove_venv(venv_path):
    try:
        shutil.rmtree(venv_path)
        print(f"🗑️  Virtual environment '{venv_path}' removed")
    except Exception:
        print(f"⚠️ Failed to remove virtual environment '{venv_path}'")

def get_python_bin(venv_path):
    if os.name == "nt":
        return os.path.join(venv_path, "Scripts", "python.exe")
    else:
        return os.path.join(venv_path, "bin", "python")

# ----------------------------
# Dependency Installation
# ----------------------------
def install_dependencies(project_path, venv_path=".sbom-env"):
    python_bin = get_python_bin(venv_path)

    print("\n📦 Upgrading pip, setuptools, wheel...")
    run_with_retry([python_bin, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel", "--no-cache-dir"], show_output=True)

    pyproject = os.path.join(project_path, "pyproject.toml")
    reqs_txt = os.path.join(project_path, "requirements.txt")

    if os.path.exists(pyproject):
        print("📦 Found pyproject.toml - using pip-tools...")
        run_with_retry([python_bin, "-m", "pip", "install", "pip-tools", "--no-cache-dir"], show_output=True)
        all_deps = os.path.join(project_path, "all-deps.txt")
        try:
            run_with_retry([python_bin, "-m", "piptools", "compile",
                            "--all-extras", "pyproject.toml",
                            "-o", "all-deps.txt"], cwd=project_path, show_output=True)
        except Exception:
            print("⚠️ Failed to compile dependencies from pyproject.toml. Trying direct pip install...")
            run_with_retry([python_bin, "-m", "pip", "install", "--upgrade", "pip", "--no-cache-dir"], show_output=True)
        if os.path.exists(all_deps):
            validate_file(all_deps)
            print("📦 Installing dependencies from all-deps.txt...")
            run_with_retry([python_bin, "-m", "pip", "install", "--requirement", all_deps, "--no-cache-dir"], show_output=True)
        else:
            print("⚠️ all-deps.txt not found, skipping pip-tools install.")
    elif os.path.exists(reqs_txt):
        print("📦 Found requirements.txt - installing dependencies...")
        run_with_retry([python_bin, "-m", "pip", "install", "--requirement", reqs_txt, "--no-cache-dir"], show_output=True)
    else:
        raise FileNotFoundError("❌ No pyproject.toml or requirements.txt found.")

# ----------------------------
# Generate dependency tree
# ----------------------------
def generate_deps_json(venv_path=".sbom-env"):
    python_bin = get_python_bin(venv_path)
    print("\n📦 Installing pipdeptree...")
    run_with_retry([python_bin, "-m", "pip", "install", "pipdeptree", "--no-cache-dir"], show_output=True)
    print("📊 Generating dependency tree (deps.json)...")
    deps_json = run_with_retry([python_bin, "-m", "pipdeptree", "--json"], capture_output=True)
    with open("deps.json", "w", encoding="utf-8") as f:
        f.write(deps_json)
    print("✅ Dependency tree saved to deps.json")

# ----------------------------
# Generate SBOM
# ----------------------------
def generate_sbom(venv_path=".sbom-env"):
    python_bin = get_python_bin(venv_path)
    print("\n📦 Installing cyclonedx-bom...")
    run_with_retry([python_bin, "-m", "pip", "install", "cyclonedx-bom", "--no-cache-dir"], show_output=True)
    print("📊 Generating SBOM (sbom-p.json)...")
    run_with_retry([python_bin, "-m", "cyclonedx_py", "venv", "-o", "sbom-p.json"], show_output=True)
    print("✅ SBOM saved to sbom-p.json")

# ----------------------------
# Run Trivy SBOM scan
# ----------------------------
def run_trivy_scan():
    print("\n🔍 Running Trivy SBOM scan...")
    run_with_retry(["trivy", "sbom", "sbom-p.json", "--format", "cyclonedx", "-o", "sbom.json"], show_output=True)
    print("✅ Trivy scan results saved to sbom.json")

# ----------------------------
# Compare SBOM vs Dependency Tree
# ----------------------------
def compare(sbom_file="sbom.json", deps_file="deps.json", output_file="comparison.txt"):
    print("\n📊 Comparing SBOM vs Dependency Tree...")
    sbom = load_sbom(sbom_file)
    deps = load_deps(deps_file)

    missing_in_sbom = []
    version_mismatches = []
    exact_matches = []
    present_in_both = []

    for pkg, dep_version in deps.items():
        sbom_version = sbom.get(pkg)
        if sbom_version is None:
            missing_in_sbom.append(pkg)
        else:
            present_in_both.append(pkg)
            if dep_version != sbom_version:
                version_mismatches.append((pkg, dep_version, sbom_version))
            else:
                exact_matches.append((pkg, dep_version))

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("====== Missing in SBOM ========\n")
        f.writelines(f"- {m}\n" for m in missing_in_sbom or ["None"])
        f.write("\n====== Present in both ========\n")
        f.writelines(f"- {pkg}\n" for pkg in present_in_both or ["None"])
        f.write("\n====== Version mismatches ========\n")
        f.writelines(f"- {pkg}: deps={dep_v}, sbom={sbom_v}\n" for pkg, dep_v, sbom_v in version_mismatches or [("None","","")])
        f.write("\n====== Exact matches ========\n")
        f.writelines(f"- {pkg}: {ver}\n" for pkg, ver in exact_matches or [("None","")])

    print(f"✅ Comparison saved in {output_file}")

# ----------------------------
# Loaders
# ----------------------------
def load_sbom(file):
    with open(file, encoding="utf-8") as f:
        data = json.load(f)
    return {normalize_name_auto(c["name"]): c.get("version") for c in data.get("components", [])}

def load_deps(file):
    with open(file, encoding="utf-8") as f:
        deps = json.load(f)
    result = {}
    def walk(dep_list):
        for d in dep_list:
            pkg_info = d.get("package", d)
            name = pkg_info.get("key", pkg_info.get("package_name", pkg_info.get("name", "unknown")))
            version = pkg_info.get("installed_version", pkg_info.get("version"))
            result[normalize_name_auto(name)] = version
            if "dependencies" in d and d["dependencies"]:
                walk(d["dependencies"])
    walk(deps)
    return result

# ----------------------------
# Main
# ----------------------------
def main():
    print(f"🔧 Detected OS: {platform.system()} ({platform.machine()})")
    project_path = input("📂 Enter Python project path: ").strip()
    if not os.path.exists(project_path):
        print("❌ Project path does not exist.")
        return

    if not is_python_project(project_path):
        print("❌ Not a Python project.")
        return

    files_found = [f for f in os.listdir(project_path) if f in ["pyproject.toml","requirements.txt","setup.py"]]
    print(f"📑 Project files detected: {', '.join(files_found)}")

    print("\n🚀 Creating virtual environment...")
    venv_path = create_venv()

    try:
        print("\n🚀 Installing dependencies...")
        install_dependencies(project_path, venv_path)

        print("\n🚀 Generating dependency tree...")
        generate_deps_json(venv_path)

        print("\n🚀 Generating SBOM...")
        generate_sbom(venv_path)

        print("\n🚀 Running Trivy scan...")
        run_trivy_scan()

        print("\n🚀 Comparing SBOM vs Dependency Tree...")
        compare()

    finally:
        print("\n🧹 Cleaning up...")
        remove_venv(venv_path)

if __name__ == "__main__":
    main()

from os_detect import detect_os
from venv import setup, remove_venv
from dep import install_dependencies
from dep_convert import convert_txt_to_json
import os
from cyclo import generate_sbom,get_python_exec
from trivy import scan_sbom
from compare_trivy_dep import compare,normalize_name,load_sbom,load_deps

def main():
    env_name = "sbom-env"

    # Step 0: Ask for project folder path
    project_path = input("Enter the full path of the project folder: ").strip()
    if not os.path.exists(project_path):
        print(f"Path '{project_path}' does not exist.")
        return

    # Step 1: Detect OS
    system = detect_os()

    # Step 2: Setup virtual environment
    venv_path = setup(env_name, project_path=project_path)
    print(f"\nVirtual environment '{env_name}' created successfully on {system}.")

    # Step 3: Install dependencies and generate dets.txt
    install_dependencies(env_name, project_path)

    # Step 4: Convert dets.txt to dets.json
    convert_txt_to_json("dets.txt", "dets.json")

    # Step 5: Generate SBOM from all-dep.txt or requirements.txt
    if os.path.exists("all-dep.txt"):
        generate_sbom(env_name, "all-dep.txt", "sbom.json")
    elif os.path.exists("a.txt"):
        generate_sbom(env_name, "a.txt", "sbom.json")
    else:
        print("⚠️ No dependency file found for SBOM generation.")

    # Step 6: Scan SBOM with Trivy
    scan_sbom("sbom.json", "sbom_p.json")
    
    # Step 7: Compare Trivy results with dets.json
    compare("sbom_p.json", "dets.json")

    # Step 8: Optionally remove the virtual environment
    remove_venv(venv_path)
    

if __name__ == "__main__":
    main()

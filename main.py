from os_detect import detect_os
from venv_creating import setup, remove_venv
from generate_dep_tree import generate_dependency_tree
from sbom import generate_sbom
from trivy_sbom import scan_sbom
from compare_sbom import compare

def main():
    env_name = "sbom-env"
    
    # Step 0: Ask user for project folder path
    project_path = input("Enter the full path of the project folder: ").strip()

    # Step 1: Detect OS
    system = detect_os()

    # Step 2: Setup virtual environment & install dependencies
    venv_path = setup(env_name, project_path=project_path)

    # Step 3: Generate dependency tree
    dep_file = "deps.json"
    generate_dependency_tree(env_name, output_file=dep_file)

    # Step 4: Generate SBOM
    sbom_file = "sbom_p.json"
    generate_sbom(env_name, output_file=sbom_file)

    # Step 5: Scan SBOM with Trivy
    scan_sbom(sbom_input=sbom_file, sbom_output="sbom.json")
    
    # Step 6: Compare dependency tree vs SBOM
    compare(sbom_file=sbom_file, deps_file=dep_file, output_file="comparison.txt")

    print("\nDependency vs SBOM comparison completed → comparison.txt")

    # Step 7: Remove the virtual environment folder
    remove_venv(venv_path)

if __name__ == "__main__":
    main()

import json
import re

def normalize_name_auto(name):
    """Normalize package names for comparison."""
    name = name.lower().replace("_", ".").replace("-", ".")
    return re.sub(r"\.+", ".", name).strip(".")

def load_sbom(file):
    """Load SBOM JSON and return dict: package -> version"""
    with open(file, encoding="utf-8") as f:
        data = json.load(f)
    return {normalize_name_auto(c["name"]): c.get("version") for c in data.get("components", [])}

def load_deps(file):
    """Load pipdeptree output and return dict: package -> version"""
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

def compare(sbom_file, deps_file, output_file="comparison.txt"):
    """Compare pipdeptree with SBOM."""
    sbom = load_sbom(sbom_file)
    deps = load_deps(deps_file)

    missing_in_sbom = []
    version_mismatches = []
    exact_matches = []

    for pkg, dep_version in deps.items():
        sbom_version = sbom.get(pkg)
        if sbom_version is None:
            missing_in_sbom.append(pkg)
        elif sbom_version != dep_version:
            version_mismatches.append((pkg, dep_version, sbom_version))
        else:
            exact_matches.append((pkg, dep_version))

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Comparison of dependencies vs SBOM\n")
        f.write("====== Missing in SBOM ========\n")
        f.write("\n".join(f"- {pkg}" for pkg in missing_in_sbom) or "None")
        f.write("\n\n====== Version mismatches ========\n")
        f.write("\n".join(f"- {pkg}: deps={dep_v}, sbom={sbom_v}" for pkg, dep_v, sbom_v in version_mismatches) or "None")
        f.write("\n\n====== Exact matches ========\n")
        f.write("\n".join(f"- {pkg}: {ver}" for pkg, ver in exact_matches) or "None")

    print(f"Comparison saved in {output_file}")

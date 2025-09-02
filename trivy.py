import subprocess
import os

def scan_sbom(sbom_input="sbom.json", sbom_output="sbom_p.json"):
    if not os.path.exists(sbom_input):
        print(f"❌ SBOM file '{sbom_input}' not found.")
        return

    print(f"\n🔍 Scanning SBOM for vulnerabilities using Trivy...")
    subprocess.run([
        "trivy", "sbom", sbom_input,
        "--format", "cyclonedx",
        "--scanners", "vuln",
        "-o", sbom_output
    ], check=True)

    print(f"\n✅ Vulnerability scan complete. Results saved to '{sbom_output}'")

import subprocess

def scan_sbom(sbom_input="sbom_p.json", sbom_output="sbom.json"):
    """Scan SBOM with Trivy and output CycloneDX JSON."""
    print(f"\nScanning SBOM {sbom_input} with Trivy...")
    subprocess.run([
        "trivy", "sbom", sbom_input, "--format", "cyclonedx","--scanners","vuln","-o", sbom_output
    ], check=True)
    print(f"Trivy scan completed → {sbom_output}")


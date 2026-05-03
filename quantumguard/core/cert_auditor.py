import logging
from typing import Dict, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CertAuditor:
    """
    TLS Certificate Quantum Auditor
    Real use case: check domains for quantum-safe certificates
    """
    
    def __init__(self):
        self.mock_certs = {
            "google.com": {
                "subject": "CN=google.com",
                "issuer": "Google Trust Services",
                "key_algorithm": "RSA",
                "key_size": 2048,
                "signature_hash": "SHA256",
                "valid_from": "2024-01-01",
                "valid_to": "2025-01-01"
            },
            "localhost": {
                "subject": "CN=localhost",
                "issuer": "Self-signed",
                "key_algorithm": "ECDSA",
                "key_size": 256,
                "signature_hash": "SHA256",
                "valid_from": "2024-01-01",
                "valid_to": "2026-01-01"
            },
            "insecure.example.com": {
                "subject": "CN=insecure.example.com",
                "issuer": "Old CA",
                "key_algorithm": "RSA",
                "key_size": 1024,
                "signature_hash": "MD5",
                "valid_from": "2020-01-01",
                "valid_to": "2024-12-31"
            }
        }
    
    def audit_certificate(self, domain: str) -> Dict:
        """Audit a single certificate"""
        logger.info(f"🔍 Auditing certificate for {domain}...")
        
        if domain not in self.mock_certs:
            logger.warning(f"⚠️  Certificate not found for {domain}")
            return {
                "domain": domain,
                "status": "NOT_FOUND",
                "quantum_ready": False
            }
        
        cert = self.mock_certs[domain]
        issues = []
        quantum_ready = True
        
        # Check key algorithm
        if cert["key_algorithm"] == "RSA" and cert["key_size"] < 2048:
            issues.append(f"Weak RSA key: {cert['key_size']} bits (vulnerable to Shor)")
            quantum_ready = False
        
        if cert["key_algorithm"] == "RSA":
            issues.append("RSA is vulnerable to Shor's algorithm")
            quantum_ready = False
        
        # Check signature hash
        if cert["signature_hash"] == "MD5":
            issues.append("MD5 signature (deprecated, vulnerable to Grover)")
            quantum_ready = False
        elif cert["signature_hash"] == "SHA1":
            issues.append("SHA1 signature (weak, vulnerable to Grover)")
            quantum_ready = False
        
        # Check expiration
        valid_to = datetime.fromisoformat(cert["valid_to"])
        if valid_to < datetime.now():
            issues.append("Certificate expired")
            quantum_ready = False
        
        severity = "CRITICAL" if not quantum_ready else "PASS"
        
        if quantum_ready:
            logger.info(f"✅ {domain}: Quantum-safe certificate")
        else:
            logger.warning(f"🚨 {domain}: NOT quantum-ready")
        
        return {
            "domain": domain,
            "key_algorithm": cert["key_algorithm"],
            "key_size": cert["key_size"],
            "signature_hash": cert["signature_hash"],
            "issuer": cert["issuer"],
            "valid_from": cert["valid_from"],
            "valid_to": cert["valid_to"],
            "quantum_ready": quantum_ready,
            "issues": issues,
            "severity": severity,
            "recommendation": self._get_recommendation(cert, quantum_ready)
        }
    
    def _get_recommendation(self, cert: Dict, quantum_ready: bool) -> str:
        """Get remediation recommendation"""
        if quantum_ready:
            return "Certificate is quantum-safe. Continue monitoring."
        
        recommendations = []
        
        if cert["key_algorithm"] == "RSA":
            recommendations.append("Migrate to post-quantum algorithm (Kyber-1024)")
        
        if cert["signature_hash"] in ["MD5", "SHA1"]:
            recommendations.append("Update signature digest to SHA-256 or SHA-384")
        
        if cert["key_size"] < 2048:
            recommendations.append(f"Increase key size from {cert['key_size']} to 2048+ bits")
        
        return " | ".join(recommendations) if recommendations else "Certificate needs update"
    
    def audit_domains(self, domains: List[str]) -> Dict:
        """Audit multiple domains"""
        logger.info(f"🔍 Auditing {len(domains)} domains...")
        
        results = []
        quantum_ready_count = 0
        
        for domain in domains:
            result = self.audit_certificate(domain)
            results.append(result)
            if result.get("quantum_ready"):
                quantum_ready_count += 1
        
        return {
            "total_domains": len(domains),
            "quantum_ready": quantum_ready_count,
            "not_quantum_ready": len(domains) - quantum_ready_count,
            "compliance_percentage": f"{(quantum_ready_count / len(domains) * 100):.1f}%",
            "scan_date": datetime.now().isoformat(),
            "results": results
        }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TEST 1: Single Certificate Audit")
    print("="*60)
    auditor = CertAuditor()
    result = auditor.audit_certificate("google.com")
    print(f"Domain: {result['domain']}")
    print(f"Quantum Ready: {result['quantum_ready']}")
    print(f"Issues: {result['issues']}")
    
    print("\n" + "="*60)
    print("TEST 2: Batch Domain Audit")
    print("="*60)
    domains = ["google.com", "localhost", "insecure.example.com"]
    report = auditor.audit_domains(domains)
    print(f"Total: {report['total_domains']}")
    print(f"Quantum-Ready: {report['quantum_ready']}")
    print(f"Compliance: {report['compliance_percentage']}")
import logging
from typing import Dict, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatScorer:
    """
    CVE Quantum Risk Scorer - scores CVEs for quantum exploitability
    Real use case: NIST NVD integration for quantum urgency assessment
    """
    
    def __init__(self):
        self.quantum_algorithms = {
            "RSA": {"shor": True, "grover": False},
            "ECC": {"shor": True, "grover": False},
            "DSA": {"shor": True, "grover": False},
            "MD5": {"shor": False, "grover": True},
            "SHA1": {"shor": False, "grover": True},
            "SHA256": {"shor": False, "grover": False},
            "AES-128": {"shor": False, "grover": True, "strength_reduction": "64-bit"},
            "AES-256": {"shor": False, "grover": False},
            "DES": {"shor": False, "grover": True},
            "3DES": {"shor": False, "grover": True},
        }
        
        self.mock_nvd_data = [
            {
                "cve_id": "CVE-2024-1001",
                "description": "RSA-1024 key generation vulnerability",
                "affected_crypto": "RSA-1024",
                "cvss": 9.8,
                "published": "2024-01-15"
            },
            {
                "cve_id": "CVE-2024-1002",
                "description": "MD5 collision in SSL certificates",
                "affected_crypto": "MD5",
                "cvss": 8.1,
                "published": "2024-02-20"
            },
            {
                "cve_id": "CVE-2024-1003",
                "description": "DES encryption weakness exposure",
                "affected_crypto": "DES",
                "cvss": 7.5,
                "published": "2024-03-10"
            }
        ]
    
    def calculate_quantum_urgency_score(self, cve_id: str, crypto_algo: str, key_bits: int = 2048) -> Dict:
        """
        Calculate Quantum Urgency Score (QUS) 0-100
        Based on: Shor/Grover vulnerability + key size + time-to-quantum
        """
        
        if crypto_algo not in self.quantum_algorithms:
            logger.warning(f"⚠️  Unknown algorithm: {crypto_algo}")
            return {
                "cve_id": cve_id,
                "status": "UNKNOWN",
                "qus": 0
            }
        
        algo_info = self.quantum_algorithms[crypto_algo]
        qus = 0
        factors = {}
        
        # Shor's algorithm impact (breaks asymmetric crypto)
        if algo_info.get("shor"):
            qus += 60
            factors["shor_vulnerable"] = True
        
        # Grover's algorithm impact (halves key strength)
        if algo_info.get("grover"):
            qus += 35
            factors["grover_vulnerable"] = True
        
            # Strength reduction penalty
            if algo_info.get("strength_reduction"):
                qus += 10
                factors["strength_reduction"] = algo_info["strength_reduction"]
        
        # Key size impact
        if key_bits < 2048:
            qus += 10
            factors["weak_key_size"] = key_bits
        
        # Harvest-now-decrypt-later risk for asymmetric algorithms
        if algo_info.get("shor") and key_bits <= 2048:
            qus += 10
            factors["harvest_now_risk"] = True
        
        # Cap at 100
        qus = min(qus, 100)
        
        # Determine urgency level
        if qus >= 80:
            urgency = "CRITICAL"
        elif qus >= 60:
            urgency = "HIGH"
        elif qus >= 40:
            urgency = "MEDIUM"
        else:
            urgency = "LOW"
        
        logger.info(f"📊 {cve_id}: QUS={qus} ({urgency})")
        
        return {
            "cve_id": cve_id,
            "algorithm": crypto_algo,
            "key_bits": key_bits,
            "quantum_urgency_score": qus,
            "urgency_level": urgency,
            "factors": factors,
            "recommendation": self._get_recommendation(urgency, crypto_algo)
        }
    
    def _get_recommendation(self, urgency: str, algo: str) -> str:
        """Get mitigation recommendation"""
        recommendations = {
            "RSA": "Migrate to Kyber-1024 (KEM) + Dilithium-3 (signatures)",
            "ECC": "Migrate to Kyber-1024",
            "DSA": "Migrate to Dilithium-3",
            "MD5": "Migration to SHA-256 (immediate)",
            "SHA1": "Migration to SHA-256+",
            "AES-128": "Upgrade to AES-256",
            "DES": "Deprecated - replace with AES-256-GCM",
            "3DES": "Deprecated - replace with AES-256-GCM"
        }
        
        base_rec = recommendations.get(algo, "Evaluate PQC alternatives")
        
        if urgency == "CRITICAL":
            return f"[CRITICAL] {base_rec} - IMMEDIATE ACTION REQUIRED"
        elif urgency == "HIGH":
            return f"[HIGH] {base_rec} - Plan migration within 6 months"
        else:
            return f"{base_rec}"
    
    def score_cve_batch(self, cves: List[Dict]) -> List[Dict]:
        """Score multiple CVEs"""
        results = []
        for cve in cves:
            result = self.calculate_quantum_urgency_score(
                cve["cve_id"],
                cve.get("crypto_algo", "RSA"),
                cve.get("key_bits", 2048)
            )
            results.append(result)
        return results
    
    def get_threat_summary(self) -> Dict:
        """Get summary of all known CVEs"""
        logger.info("📋 Scanning NIST NVD Mock Database...")
        
        critical_count = 0
        high_count = 0
        medium_count = 0
        
        for cve in self.mock_nvd_data:
            # Extract base algorithm (e.g., "RSA-1024" -> "RSA")
            affected_crypto = cve["affected_crypto"]
            base_algo = affected_crypto.split("-")[0] if affected_crypto not in self.quantum_algorithms else affected_crypto
            
            result = self.calculate_quantum_urgency_score(
                cve["cve_id"],
                base_algo
            )
            
            if result.get("urgency_level") == "CRITICAL":
                critical_count += 1
            elif result["urgency_level"] == "HIGH":
                high_count += 1
            elif result["urgency_level"] == "MEDIUM":
                medium_count += 1
        
        return {
            "total_cves_analyzed": len(self.mock_nvd_data),
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
            "scan_date": datetime.now().isoformat()
        }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TEST 1: Single CVE Scoring")
    print("="*60)
    scorer = ThreatScorer()
    result = scorer.calculate_quantum_urgency_score("CVE-2024-1001", "RSA", 1024)
    print(f"CVE: {result['cve_id']}")
    print(f"QUS: {result['quantum_urgency_score']}/100 ({result['urgency_level']})")
    print(f"Recommendation: {result['recommendation']}")
    
    print("\n" + "="*60)
    print("TEST 2: Batch CVE Scoring")
    print("="*60)
    cves = [
        {"cve_id": "CVE-2024-5001", "crypto_algo": "RSA", "key_bits": 1024},
        {"cve_id": "CVE-2024-5002", "crypto_algo": "MD5", "key_bits": 128},
        {"cve_id": "CVE-2024-5003", "crypto_algo": "AES-256", "key_bits": 256},
    ]
    batch_results = scorer.score_cve_batch(cves)
    for r in batch_results:
        print(f"{r['cve_id']}: QUS={r['quantum_urgency_score']} ({r['urgency_level']})")
    
    print("\n" + "="*60)
    print("TEST 3: Threat Summary")
    print("="*60)
    summary = scorer.get_threat_summary()
    print(f"Total CVEs: {summary['total_cves_analyzed']}")
    print(f"Critical: {summary['critical']}, High: {summary['high']}, Medium: {summary['medium']}")
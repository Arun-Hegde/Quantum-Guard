import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import pytest
from core.qkd_bb84 import BB84QuantumKeyDistribution
from core.pqc_engine import PQCEngine
from core.threat_scorer import ThreatScorer
from core.quantum_ids import QuantumIDS
from core.secure_channel import SecureChannel
from core.cert_auditor import CertAuditor
from core.vault import QuantumVault

class TestBB84:
    def test_bb84_secure_channel(self):
        qkd = BB84QuantumKeyDistribution(num_qubits=500, eve_eavesdrop=False)
        session = qkd.run_protocol()
        assert session.sifted_key is not None
        assert session.eve_detected == False
    
    def test_bb84_eavesdropping_detection(self):
        qkd = BB84QuantumKeyDistribution(num_qubits=1000, eve_eavesdrop=True)
        session = qkd.run_protocol()
        assert session.eve_detected == True
        assert session.qber > 0.125

class TestPQC:
    def test_encryption_decryption(self):
        pqc = PQCEngine()
        key = pqc.generate_symmetric_key()
        plaintext = "Secure test message"
        
        encrypted = pqc.encrypt_payload(plaintext, key)
        decrypted = pqc.decrypt_payload(encrypted, key)
        
        assert plaintext == decrypted
    
    def test_key_derivation(self):
        pqc = PQCEngine()
        secret = b"test_secret"
        key = pqc.derive_key_from_secret(secret)
        assert len(key) == 32

class TestThreatScorer:
    def test_rsa_scoring(self):
        scorer = ThreatScorer()
        result = scorer.calculate_quantum_urgency_score("CVE-2024-1001", "RSA", 1024)
        assert result["quantum_urgency_score"] >= 50
        assert result["urgency_level"] == "CRITICAL"
    
    def test_batch_scoring(self):
        scorer = ThreatScorer()
        cves = [
            {"cve_id": "CVE-1", "crypto_algo": "RSA", "key_bits": 1024},
            {"cve_id": "CVE-2", "crypto_algo": "AES-256", "key_bits": 256},
        ]
        results = scorer.score_cve_batch(cves)
        assert len(results) == 2

class TestQuantumIDS:
    def test_weak_protocol_detection(self):
        ids = QuantumIDS()
        report = ids.scan_traffic()
        assert report["total_alerts"] > 0

class TestSecureChannel:
    def test_channel_establishment(self):
        channel = SecureChannel("test-channel")
        status = channel.establish_channel()
        assert status["status"] == "ESTABLISHED"
        assert channel.is_established == True

class TestCertAuditor:
    def test_certificate_audit(self):
        auditor = CertAuditor()
        result = auditor.audit_certificate("insecure.example.com")
        assert result["quantum_ready"] == False
    
    def test_batch_audit(self):
        auditor = CertAuditor()
        domains = ["google.com", "localhost"]
        report = auditor.audit_domains(domains)
        assert report["total_domains"] == 2

class TestQuantumVault:
    def test_store_retrieve(self):
        vault = QuantumVault("test-vault")
        vault.store_secret("test-key", "test-value")
        retrieved = vault.retrieve_secret("test-key")
        assert retrieved["value"] == "test-value"
    
    def test_audit_ledger(self):
        vault = QuantumVault("test-vault")
        vault.store_secret("key1", "value1")
        ledger = vault.get_audit_ledger()
        assert ledger["total_entries"] > 0
    
    def test_ledger_integrity(self):
        vault = QuantumVault("test-vault")
        vault.store_secret("key1", "value1")
        integrity = vault.verify_ledger_integrity()
        assert integrity["ledger_valid"] == True

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
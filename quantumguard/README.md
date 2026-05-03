# QuantumGuard: Real-Time Quantum Cybersecurity Platform

**Harvest-now-decrypt-later defense for the post-quantum era**

Production-grade quantum security platform with 8 deployable modules.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run All Tests
```bash
cd tests
python -m pytest test_all.py -v
```

### 3. Start REST API
```bash
cd api
python app.py
# API available at http://localhost:5000
```

### 4. Run Individual Modules
```bash
python core/qkd_bb84.py      # BB84 Quantum Key Distribution
python core/pqc_engine.py    # PQC Encryption/Decryption
python core/threat_scorer.py # CVE Quantum Risk Scoring
python core/quantum_ids.py   # Network Intrusion Detection
python core/secure_channel.py # Quantum-Safe Channel
python core/cert_auditor.py  # TLS Certificate Audit
python core/vault.py         # Quantum-Safe Vault
```

## 📊 Module Overview

| Module | File | Purpose |
|--------|------|---------|
| M1 | qkd_bb84.py | BB84 quantum key distribution simulator |
| M2 | pqc_engine.py | AES-256-GCM encryption with Kyber KEM |
| M3 | threat_scorer.py | CVE quantum urgency scoring (QUS) |
| M4 | quantum_ids.py | Network traffic analysis for weak crypto |
| M5 | secure_channel.py | Hybrid PQC secure channel |
| M6 | cert_auditor.py | TLS certificate quantum audit |
| M7 | vault.py | Quantum-safe secrets vault with audit ledger |
| M8 | app.py | Flask REST API + Dashboard |

## 🔐 Features

✅ BB84 Quantum Key Distribution with eavesdropper detection  
✅ AES-256-GCM encryption with forward secrecy  
✅ NIST CVE risk scoring for quantum algorithms  
✅ Real-time network intrusion detection  
✅ TLS certificate compliance checking  
✅ Immutable audit ledger (hash-chained)  
✅ REST API for SIEM integration  
✅ Production-ready error handling  

## 📈 REST API Endpoints

```
GET  /api/health              - Health check
POST /api/qkd/bb84            - Run BB84 protocol
POST /api/pqc/encrypt         - Encrypt with AES-256-GCM
POST /api/threats/score       - Score CVE for quantum risk
POST /api/ids/scan            - Scan network traffic
POST /api/cert/audit          - Audit TLS certificate
POST /api/vault/store         - Store secret in vault
GET  /api/vault/audit         - Get audit trail
GET  /api/status              - Platform status
```

## 🧪 Test Examples

```python
# Test 1: BB84 QKD
qkd = BB84QuantumKeyDistribution(num_qubits=1000, eve_eavesdrop=False)
session = qkd.run_protocol()
print(qkd.get_session_summary())

# Test 2: PQC Encryption
pqc = PQCEngine()
key = pqc.generate_symmetric_key()
encrypted = pqc.encrypt_payload("secret message", key)
decrypted = pqc.decrypt_payload(encrypted, key)

# Test 3: Threat Scoring
scorer = ThreatScorer()
result = scorer.calculate_quantum_urgency_score("CVE-2024-1001", "RSA", 1024)
print(result["quantum_urgency_score"])  # Output: 60-100

# Test 4: Network IDS
ids = QuantumIDS()
report = ids.scan_traffic()
print(f"Alerts: {report['total_alerts']}")
```

## 🛡️ Production Deployment

QuantumGuard is ready for:
- Financial transaction security  
- Healthcare data protection  
- Enterprise SIEM integration  
- Government CNSA 2.0 compliance  
- Microservice internal comms  

## 📜 License

MIT License - Open Source Quantum Security

---

**Built at Ada Lovelace School of Programming & Logic**  
**April 2026**
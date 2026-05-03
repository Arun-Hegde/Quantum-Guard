import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from flask import Flask, jsonify, request, render_template
from core.qkd_bb84 import BB84QuantumKeyDistribution
from core.pqc_engine import PQCEngine
from core.threat_scorer import ThreatScorer
from core.quantum_ids import QuantumIDS
from core.secure_channel import SecureChannel
from core.cert_auditor import CertAuditor
from core.vault import QuantumVault
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set template folder to dashboard/templates
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dashboard', 'templates')
app = Flask(__name__, template_folder=template_dir)

# Initialize modules
pqc_engine = PQCEngine()
threat_scorer = ThreatScorer()
quantum_ids = QuantumIDS()
cert_auditor = CertAuditor()
vault = QuantumVault("api-vault")

@app.route('/')
def dashboard():
    """Serve the QuantumGuard dashboard"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "online", "platform": "QuantumGuard"}), 200

@app.route('/api/threat-summary', methods=['GET'])
def threat_summary():
    """Dashboard summary data"""
    summary = threat_scorer.get_threat_summary()
    return jsonify({
        "total_cves_scored": summary["total_cves_analyzed"],
        "critical_cves": summary["critical"],
        "network_alerts": 0,
        "certificates_audited": 0,
        "quantum_ready": 0
    }), 200

@app.route('/api/qkd/bb84', methods=['POST'])
def qkd_bb84():
    """Run BB84 QKD"""
    num_qubits = request.json.get('num_qubits', 1000)
    eve = request.json.get('eve_eavesdrop', False)
    
    qkd = BB84QuantumKeyDistribution(num_qubits=num_qubits, eve_eavesdrop=eve)
    session = qkd.run_protocol()
    
    return jsonify(qkd.get_session_summary()), 200

@app.route('/api/pqc/encrypt', methods=['POST'])
def pqc_encrypt():
    """Encrypt with AES-256-GCM"""
    plaintext = request.json.get('plaintext', '')
    key = pqc_engine.generate_symmetric_key()
    
    encrypted = pqc_engine.encrypt_payload(plaintext, key)
    
    return jsonify({
        "status": "encrypted",
        "ciphertext": encrypted["ciphertext"][:50] + "...",
        "key_size": len(key)
    }), 200

@app.route('/api/threats/score', methods=['POST'])
def threat_score():
    """Score CVE for quantum risk"""
    cve_id = request.json.get('cve_id', 'CVE-2024-0001')
    algo = request.json.get('crypto_algo', 'RSA')
    key_bits = request.json.get('key_bits', 2048)
    
    result = threat_scorer.calculate_quantum_urgency_score(cve_id, algo, key_bits)
    return jsonify(result), 200

@app.route('/api/ids/scan', methods=['POST'])
def ids_scan():
    """Scan network for weak crypto"""
    report = quantum_ids.scan_traffic()
    return jsonify(report), 200

@app.route('/api/cert/audit', methods=['POST'])
def cert_audit():
    """Audit TLS certificate"""
    domain = request.json.get('domain', 'google.com')
    result = cert_auditor.audit_certificate(domain)
    return jsonify(result), 200

@app.route('/api/vault/store', methods=['POST'])
def vault_store():
    """Store secret in vault"""
    key_name = request.json.get('key_name', 'secret1')
    secret_value = request.json.get('secret_value', 'hidden')
    
    result = vault.store_secret(key_name, secret_value)
    return jsonify(result), 200

@app.route('/api/vault/audit', methods=['GET'])
def vault_audit():
    """Get vault audit ledger"""
    ledger = vault.get_audit_ledger()
    return jsonify(ledger), 200

@app.route('/api/status', methods=['GET'])
def status():
    """Get full platform status"""
    return jsonify({
        "platform": "QuantumGuard",
        "modules": {
            "bb84_qkd": "online",
            "pqc_engine": "online",
            "threat_scorer": "online",
            "quantum_ids": "online",
            "secure_channel": "online",
            "cert_auditor": "online",
            "quantum_vault": "online"
        },
        "timestamp": "2024-04-13T10:30:00Z"
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"🚀 QuantumGuard REST API starting on port {port}...")
    app.run(debug=False, host='0.0.0.0', port=port)
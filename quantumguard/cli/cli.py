"""
M8 — CLI Tool
Click-based command-line interface for QuantumGuard.
DevSecOps pipelines and administration commands.
"""

import click
import json
import os
import sys
from datetime import datetime
from tabulate import tabulate

# Add parent path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.qkd_bb84 import BB84Protocol
from core.pqc_engine import PQCryptoEngine
from core.threat_scorer import CVEQuantumScorer, QuantumThreatDetector
from core.quantum_ids import QuantumHIDSAnalyzer
from core.cert_auditor import CertificateAuditor
from core.vault import QuantumSafeVault, AuditEventType


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """QuantumGuard: Real-Time Quantum Cybersecurity Operations Platform"""
    pass


# ===== BB84 Commands =====

@cli.group()
def qkd():
    """BB84 Quantum Key Distribution commands"""
    pass


@qkd.command()
@click.option('--qubits', default=1000, help='Number of qubits to transmit')
@click.option('--eve', is_flag=True, help='Enable eavesdropper (Eve)')
@click.option('--json', 'output_json', is_flag=True, help='JSON output')
def bb84(qubits, eve, output_json):
    """Run BB84 quantum key distribution session"""
    click.echo(f"Running BB84 with {qubits} qubits..." if not output_json else '', err=True)

    protocol = BB84Protocol(qubit_count=qubits, eve_present=eve)
    session = protocol.run_session()

    if output_json:
        click.echo(json.dumps(session.to_dict(), indent=2))
    else:
        click.echo("\n" + "=" * 70)
        click.echo("BB84 Quantum Key Distribution Session")
        click.echo("=" * 70)
        click.echo(f"Session ID: {session.session_id}")
        click.echo(f"Raw qubits: {session.raw_key_length}")
        click.echo(f"Sifted key: {session.sifted_key_length} bits")
        click.echo(f"Key efficiency: {(session.sifted_key_length / session.raw_key_length) * 100:.2f}%")
        click.echo(f"QBER: {session.qber:.4f}")
        click.echo(f"Eve detected: {'YES - CRITICAL!' if session.eve_detected else 'NO - Safe'}")
        if session.eve_detected:
            click.echo(f"Eve probability: {session.eve_probability:.4f}")
        click.echo(f"Sifted key (hex): {protocol.get_sifted_key_hex(session)[:64]}...")
        click.echo("=" * 70 + "\n")


# ===== PQC Commands =====

@cli.group()
def pqc():
    """Post-Quantum Cryptography commands"""
    pass


@pqc.command()
@click.option('--message', prompt='Message to encrypt', help='Plaintext message')
@click.option('--json', 'output_json', is_flag=True, help='JSON output')
def encrypt(message, output_json):
    """Encrypt a message using Kyber+AES-256-GCM"""
    engine = PQCryptoEngine()
    
    # Generate keypair
    keypair = engine.generate_kyber_keypair()
    
    # Encrypt
    plaintext = message.encode()
    encrypted = engine.encrypt_message(plaintext, keypair.public_key)
    
    if output_json:
        click.echo(json.dumps(encrypted.to_dict(), indent=2))
    else:
        click.echo(f"\nEncrypted successfully!")
        click.echo(f"Ciphertext size: {len(encrypted.ciphertext)} bytes")
        click.echo(f"Encapsulated key size: {len(encrypted.encapsulated_key)} bytes")


@pqc.command()
@click.option('--message', prompt='Message to sign', help='Message to sign')
@click.option('--json', 'output_json', is_flag=True, help='JSON output')
def sign(message, output_json):
    """Sign a message using Dilithium"""
    engine = PQCryptoEngine()
    
    # Generate keypair
    keypair = engine.generate_dilithium_keypair()
    
    # Sign
    plaintext = message.encode()
    sig = engine.sign(plaintext, keypair.private_key, key_id=keypair.key_id)
    
    if output_json:
        click.echo(json.dumps(sig.to_dict(), indent=2))
    else:
        click.echo(f"\nSigned successfully!")
        click.echo(f"Message hash: {sig.message_hash[:32]}...")
        click.echo(f"Signature size: {len(sig.signature)} bytes")
        click.echo(f"Key ID: {sig.key_id}")


# ===== CVE Commands =====

@cli.group()
def cve():
    """CVE Quantum Risk Scoring commands"""
    pass


@cve.command()
@click.argument('cve_id')
@click.option('--json', 'output_json', is_flag=True, help='JSON output')
def score(cve_id, output_json):
    """Score a CVE for quantum risk"""
    scorer = CVEQuantumScorer(use_mock_data=True)
    
    cve_info = scorer.score_cve(cve_id.upper())
    
    if not cve_info:
        click.echo(f"CVE {cve_id} not found", err=True)
        sys.exit(1)
    
    qus = cve_info.quantum_urgency_score
    
    if output_json:
        click.echo(json.dumps(qus.to_dict(), indent=2))
    else:
        click.echo("\n" + "=" * 70)
        click.echo(f"CVE Quantum Urgency Score: {cve_id}")
        click.echo("=" * 70)
        click.echo(f"QUS Score: {qus.qus_score}/100")
        click.echo(f"CVSS v3: {cve_info.cvss_v3_score}")
        click.echo(f"Shor Impact: {qus.shor_impact:.2%}")
        click.echo(f"Grover Impact: {qus.grover_impact:.2%}")
        click.echo(f"Harvest-Now Risk: {'YES' if qus.harvest_now_risk else 'NO'}")
        click.echo(f"Threats: {len(qus.quantum_threats)}")
        for threat in qus.quantum_threats[:3]:
            click.echo(f"  - {threat.threat_type}: {threat.description}")
        click.echo(f"\nRecommendation: {qus.recommendation}")
        click.echo("=" * 70 + "\n")


@cve.command()
@click.argument('description')
@click.option('--json', 'output_json', is_flag=True, help='JSON output')
def detect(description, output_json):
    """Detect quantum threats in text"""
    detector = QuantumThreatDetector()
    threats = detector.detect_threats(description)
    
    if output_json:
        click.echo(json.dumps(
            [t.to_dict() for t in threats],
            indent=2
        ))
    else:
        click.echo(f"\nDetected {len(threats)} quantum threats:")
        for threat in threats:
            click.echo(f"  - {threat.threat_type}")
            click.echo(f"    Algorithm: {threat.affected_algorithm}")
            click.echo(f"    Breaktime: {threat.breaktime_estimate}")


# ===== IDS Commands =====

@cli.group()
def ids():
    """Network Intrusion Detection commands"""
    pass


@ids.command()
@click.option('--packets', default=100, help='Number of packets to simulate')
@click.option('--json', 'output_json', is_flag=True, help='JSON output')
def simulate(packets, output_json):
    """Simulate network traffic and detect threats"""
    click.echo(f"Simulating {packets} packets..." if not output_json else '', err=True)
    
    analyzer = QuantumHIDSAnalyzer()
    analyzer.simulate_traffic(num_packets=packets)
    
    alerts = analyzer.get_alerts()
    
    if output_json:
        click.echo(json.dumps(
            [a.to_dict() for a in alerts],
            indent=2
        ))
    else:
        click.echo(f"\nDetected {len(alerts)} alerts:")
        
        if alerts:
            table_data = []
            for alert in alerts[:10]:
                table_data.append([
                    alert.alert_id,
                    alert.severity,
                    alert.threat_type,
                    f"{alert.network_flow.src_ip} → {alert.network_flow.dst_ip}",
                ])
            
            click.echo(tabulate(
                table_data,
                headers=['Alert ID', 'Severity', 'Threat Type', 'Flow'],
                tablefmt='grid'
            ))


# ===== Certificate Commands =====

@cli.group()
def cert():
    """TLS Certificate Auditing commands"""
    pass


@cert.command()
@click.argument('domain')
@click.option('--json', 'output_json', is_flag=True, help='JSON output')
def audit(domain, output_json):
    """Audit a TLS certificate"""
    click.echo(f"Auditing {domain}..." if not output_json else '', err=True)
    
    auditor = CertificateAuditor()
    audit_result = auditor.audit_certificate(domain)
    
    if not audit_result:
        click.echo(f"Failed to audit {domain}", err=True)
        sys.exit(1)
    
    if output_json:
        click.echo(json.dumps(audit_result.to_dict(), indent=2))
    else:
        click.echo("\n" + "=" * 70)
        click.echo(f"Certificate Audit: {domain}")
        click.echo("=" * 70)
        click.echo(f"Common Name: {audit_result.cert_analysis.common_name}")
        click.echo(f"Key Algorithm: {audit_result.cert_analysis.key_algorithm} "
                  f"({audit_result.cert_analysis.key_size} bits)")
        click.echo(f"Signature Hash: {audit_result.cert_analysis.signature_hash}")
        click.echo(f"Quantum Readiness: {audit_result.quantum_readiness}")
        click.echo(f"Compliance Score: {audit_result.compliance_score}/100")
        click.echo(f"Vulnerabilities: {len(audit_result.vulnerabilities)}")
        
        if audit_result.vulnerabilities:
            click.echo("\nVulnerabilities:")
            for vuln in audit_result.vulnerabilities:
                click.echo(f"  - [{vuln.severity}] {vuln.vulnerability_type}")
                click.echo(f"    {vuln.description}")
        
        click.echo(f"\nRecommendation: {audit_result.recommendation}")
        click.echo("=" * 70 + "\n")


# ===== Vault Commands =====

@cli.group()
def vault():
    """Quantum-Safe Vault commands"""
    pass


@vault.command()
@click.option('--name', default='default', help='Vault name')
@click.option('--password', prompt=True, hide_input=True, help='Master password')
def init(name, password):
    """Initialize a new vault"""
    click.echo(f"Initializing vault '{name}'...")
    
    try:
        v = QuantumSafeVault(vault_name=name, master_password=password)
        click.echo(f"✓ Vault '{name}' created successfully")
        v.close()
    except Exception as e:
        click.echo(f"✗ Failed to create vault: {e}", err=True)
        sys.exit(1)


@vault.command()
@click.argument('vault_name')
@click.argument('secret_name')
@click.option('--type', 'secret_type', default='generic', help='Secret type')
@click.option('--password', prompt=True, hide_input=True, help='Vault password')
def store(vault_name, secret_name, secret_type, password):
    """Store a secret in the vault"""
    secret_value = click.prompt('Secret value', hide_input=True)
    
    try:
        v = QuantumSafeVault(vault_name=vault_name, master_password=password)
        success = v.store_secret(
            name=secret_name,
            secret_value=secret_value.encode(),
            secret_type=secret_type,
            owner='cli',
        )
        
        if success:
            click.echo(f"✓ Secret '{secret_name}' stored")
        else:
            click.echo(f"✗ Failed to store secret", err=True)
        
        v.close()
    except Exception as e:
        click.echo(f"✗ Vault error: {e}", err=True)
        sys.exit(1)


@vault.command()
@click.argument('vault_name')
@click.argument('secret_name')
@click.option('--password', prompt=True, hide_input=True, help='Vault password')
def retrieve(vault_name, secret_name, password):
    """Retrieve a secret from the vault"""
    try:
        v = QuantumSafeVault(vault_name=vault_name, master_password=password)
        secret = v.retrieve_secret(secret_name)
        
        if secret:
            click.echo(secret.decode())
        else:
            click.echo(f"✗ Secret '{secret_name}' not found", err=True)
        
        v.close()
    except Exception as e:
        click.echo(f"✗ Vault error: {e}", err=True)
        sys.exit(1)


@vault.command()
@click.argument('vault_name')
@click.option('--password', prompt=True, hide_input=True, help='Vault password')
@click.option('--json', 'output_json', is_flag=True, help='JSON output')
def integrity(vault_name, password, output_json):
    """Check vault integrity"""
    try:
        v = QuantumSafeVault(vault_name=vault_name, master_password=password)
        status = v.verify_integrity()
        
        if output_json:
            click.echo(json.dumps(status.to_dict(), indent=2))
        else:
            click.echo("\n" + "=" * 70)
            click.echo("Vault Integrity Check")
            click.echo("=" * 70)
            click.echo(f"Total entries: {status.total_entries}")
            click.echo(f"Valid entries: {status.valid_entries}")
            click.echo(f"Compromised: {len(status.compromised_entries)}")
            click.echo(f"Status: {'✓ VALID' if status.is_valid else '✗ COMPROMISED'}")
            if status.compromised_entries:
                click.echo(f"Compromised entries: {status.compromised_entries}")
            click.echo("=" * 70)
        
        v.close()
    except Exception as e:
        click.echo(f"✗ Vault error: {e}", err=True)
        sys.exit(1)


# ===== System Commands =====

@cli.group()
def system():
    """System and information commands"""
    pass


@system.command()
def status():
    """Show QuantumGuard system status"""
    click.echo("\n" + "=" * 70)
    click.echo("QuantumGuard System Status")
    click.echo("=" * 70)
    click.echo(f"Version: 1.0.0")
    click.echo(f"Timestamp: {datetime.now().isoformat()}")
    click.echo("\nModules:")
    click.echo("  ✓ M1: BB84 Quantum Key Distribution")
    click.echo("  ✓ M2: Post-Quantum Cryptography Engine")
    click.echo("  ✓ M3: CVE Quantum Risk Scorer")
    click.echo("  ✓ M4: Network Anomaly IDS")
    click.echo("  ✓ M5: Quantum-Safe Secure Channel")
    click.echo("  ✓ M6: TLS Certificate Auditor")
    click.echo("  ✓ M7: Quantum-Safe Vault")
    click.echo("  ✓ M8: Dashboard & API")
    click.echo("=" * 70 + "\n")


@system.command()
def version():
    """Show version information"""
    click.echo("QuantumGuard 1.0.0")
    click.echo("Quantum Cryptography & Cybersecurity Platform")
    click.echo("https://github.com/quantumguard/quantumguard")


if __name__ == '__main__':
    cli()

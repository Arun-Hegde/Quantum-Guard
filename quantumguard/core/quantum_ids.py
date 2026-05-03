import logging
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NetworkAlert:
    """Network security alert"""
    timestamp: str
    src_ip: str
    dst_ip: str
    protocol: str
    issue: str
    severity: str
    payload_size: int

class QuantumIDS:
    """
    Real-Time Network Anomaly IDS
    Detects weak crypto + harvest-now patterns
    """
    
    def __init__(self):
        self.weak_protocols = {
            "RSA-1024": "CRITICAL",
            "MD5": "HIGH",
            "DES": "CRITICAL",
            "3DES": "HIGH",
            "SSLv3": "CRITICAL",
            "TLSv1.0": "HIGH",
            "TLSv1.1": "HIGH",
            "SHA1": "MEDIUM"
        }
        
        self.harvest_patterns = {
            "large_encrypted_blob": 10_000_000,  # >10MB
            "unknown_destination": True,
            "repeated_connections": 5
        }
        
        self.alerts = []
        self.mock_packets = [
            {
                "src_ip": "172.16.0.100",
                "dst_ip": "203.0.113.50",
                "protocol": "TLSv1.0",
                "payload_size": 5_000_000,
                "destination_reputation": "unknown"
            },
            {
                "src_ip": "192.168.1.50",
                "dst_ip": "10.0.0.1",
                "protocol": "TLSv1.3",
                "payload_size": 1024,
                "destination_reputation": "internal"
            },
            {
                "src_ip": "172.16.0.200",
                "dst_ip": "198.51.100.200",
                "protocol": "RSA-1024",
                "payload_size": 50_000_000,
                "destination_reputation": "suspicious"
            }
        ]
    
    def analyze_packet(self, packet: Dict) -> List[NetworkAlert]:
        """Analyze a single packet for quantum vulnerabilities"""
        alerts = []
        src_ip = packet["src_ip"]
        dst_ip = packet["dst_ip"]
        protocol = packet["protocol"]
        payload_size = packet["payload_size"]
        
        # Check for weak protocols
        if protocol in self.weak_protocols:
            severity = self.weak_protocols[protocol]
            alerts.append(NetworkAlert(
                timestamp=datetime.now().isoformat(),
                src_ip=src_ip,
                dst_ip=dst_ip,
                protocol=protocol,
                issue=f"Weak/quantum-vulnerable protocol: {protocol}",
                severity=severity,
                payload_size=payload_size
            ))
            logger.warning(f"⚠️  {src_ip} -> {dst_ip}: Using {protocol} ({severity})")
        
        # Check for harvest-now patterns
        if payload_size > self.harvest_patterns["large_encrypted_blob"]:
            alerts.append(NetworkAlert(
                timestamp=datetime.now().isoformat(),
                src_ip=src_ip,
                dst_ip=dst_ip,
                protocol=protocol,
                issue=f"Large encrypted payload ({payload_size:,} bytes) - potential data exfiltration",
                severity="HIGH",
                payload_size=payload_size
            ))
            logger.warning(f"🚨 {src_ip} -> {dst_ip}: Large encrypted blob ({payload_size:,} bytes)")
        
        # Check destination reputation
        if packet.get("destination_reputation") == "suspicious":
            alerts.append(NetworkAlert(
                timestamp=datetime.now().isoformat(),
                src_ip=src_ip,
                dst_ip=dst_ip,
                protocol=protocol,
                issue="Suspicious destination - high abuse potential",
                severity="MEDIUM",
                payload_size=payload_size
            ))
        
        return alerts
    
    def scan_traffic(self, packets: List[Dict] = None) -> Dict:
        """Scan multiple packets"""
        if packets is None:
            packets = self.mock_packets
        
        logger.info(f"🔍 Scanning {len(packets)} packets...")
        self.alerts = []
        
        for packet in packets:
            packet_alerts = self.analyze_packet(packet)
            self.alerts.extend(packet_alerts)
        
        logger.info(f"✅ Scan complete: {len(self.alerts)} alerts generated")
        
        return self.get_scan_report()
    
    def get_scan_report(self) -> Dict:
        """Generate scan report"""
        critical_count = sum(1 for a in self.alerts if a.severity == "CRITICAL")
        high_count = sum(1 for a in self.alerts if a.severity == "HIGH")
        medium_count = sum(1 for a in self.alerts if a.severity == "MEDIUM")
        
        return {
            "total_alerts": len(self.alerts),
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
            "alerts": [
                {
                    "timestamp": a.timestamp,
                    "src_ip": a.src_ip,
                    "dst_ip": a.dst_ip,
                    "protocol": a.protocol,
                    "issue": a.issue,
                    "severity": a.severity,
                    "payload_size": a.payload_size
                }
                for a in self.alerts
            ]
        }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TEST 1: Network Traffic Scan")
    print("="*60)
    ids = QuantumIDS()
    report = ids.scan_traffic()
    
    print(f"Total Alerts: {report['total_alerts']}")
    print(f"Critical: {report['critical']}, High: {report['high']}, Medium: {report['medium']}")
    
    print("\n" + "="*60)
    print("TEST 2: Alert Details")
    print("="*60)
    for alert in report["alerts"]:
        print(f"[{alert['severity']}] {alert['src_ip']} -> {alert['dst_ip']}")
        print(f"  Issue: {alert['issue']}")
        print()
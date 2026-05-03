import logging
import os
import json
import hashlib
from typing import Dict, List
from datetime import datetime
try:
    from core.pqc_engine import PQCEngine
except ModuleNotFoundError:
    from pqc_engine import PQCEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuantumVault:
    """
    Quantum-Safe Vault with Immutable Audit Ledger
    Real use case: storing keys, tokens, certs with tamper-evident audit trail
    """
    
    def __init__(self, vault_name: str = "default"):
        self.vault_name = vault_name
        self.pqc = PQCEngine()
        self.master_key = self.pqc.generate_symmetric_key(32)
        self.secrets = {}
        self.audit_ledger = []
        self.ledger_chain = []  # Hash chain for immutability
        
        logger.info(f"🏦 Vault '{vault_name}' initialized with Kyber master key")
    
    def _compute_hash(self, data: str) -> str:
        """Compute SHA-256 hash"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _add_to_ledger(self, action: str, key_name: str, details: str = ""):
        """Add entry to immutable audit ledger"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "key_name": key_name,
            "details": details,
            "entry_hash": ""
        }
        
        # Create hash of previous block + current entry
        if self.ledger_chain:
            prev_hash = self.ledger_chain[-1]
        else:
            prev_hash = "GENESIS"
        
        entry_content = json.dumps(entry, sort_keys=True)
        entry_hash = self._compute_hash(prev_hash + entry_content)
        entry["entry_hash"] = entry_hash
        
        self.audit_ledger.append(entry)
        self.ledger_chain.append(entry_hash)
        
        logger.info(f"📝 Audit: {action} - {key_name} (hash: {entry_hash[:16]}...)")
    
    def store_secret(self, key_name: str, secret_value: str) -> Dict:
        """Store encrypted secret"""
        logger.info(f"🔐 Storing secret: {key_name}")
        
        # Encrypt with master key
        encrypted = self.pqc.encrypt_payload(secret_value, self.master_key)
        
        self.secrets[key_name] = encrypted
        
        # Audit log
        self._add_to_ledger("STORE", key_name, f"Stored {len(secret_value)} bytes")
        
        return {
            "key_name": key_name,
            "status": "STORED",
            "encrypted": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def retrieve_secret(self, key_name: str) -> Dict:
        """Retrieve and decrypt secret"""
        if key_name not in self.secrets:
            logger.warning(f"⚠️  Secret not found: {key_name}")
            return {"error": f"Secret '{key_name}' not found"}
        
        logger.info(f"🔓 Retrieving secret: {key_name}")
        
        encrypted = self.secrets[key_name]
        plaintext = self.pqc.decrypt_payload(encrypted, self.master_key)
        
        # Audit log
        self._add_to_ledger("RETRIEVE", key_name, "Accessed")
        
        return {
            "key_name": key_name,
            "value": plaintext,
            "timestamp": datetime.now().isoformat(),
            "accessed": True
        }
    
    def delete_secret(self, key_name: str) -> Dict:
        """Delete secret (logged in audit trail)"""
        if key_name not in self.secrets:
            return {"error": f"Secret '{key_name}' not found"}
        
        logger.info(f"🗑️  Deleting secret: {key_name}")
        
        del self.secrets[key_name]
        self._add_to_ledger("DELETE", key_name, "Deleted")
        
        return {
            "key_name": key_name,
            "status": "DELETED",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_audit_ledger(self) -> Dict:
        """Get immutable audit trail"""
        return {
            "vault": self.vault_name,
            "total_entries": len(self.audit_ledger),
            "ledger": [e for e in self.audit_ledger],
            "chain_hash": self.ledger_chain[-1] if self.ledger_chain else "EMPTY"
        }
    
    def verify_ledger_integrity(self) -> Dict:
        """Verify ledger hasn't been tampered with"""
        logger.info("✔️  Verifying ledger integrity...")
        
        is_valid = True
        errors = []
        
        prev_hash = "GENESIS"
        for i, entry in enumerate(self.audit_ledger):
            # Re-compute using the same data shape as when the hash was created
            entry_copy = dict(entry)
            entry_copy["entry_hash"] = ""
            expected_hash = self._compute_hash(prev_hash + json.dumps(entry_copy, sort_keys=True))
            if expected_hash != entry["entry_hash"]:
                is_valid = False
                errors.append(f"Entry {i}: Hash mismatch")
            prev_hash = entry["entry_hash"]
        
        if is_valid:
            logger.info("✅ Ledger integrity verified - no tampering detected")
        else:
            logger.error(f"🚨 Ledger compromised! {len(errors)} errors found")
        
        return {
            "ledger_valid": is_valid,
            "entries_verified": len(self.audit_ledger),
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_vault_status(self) -> Dict:
        """Get vault statistics"""
        return {
            "vault_name": self.vault_name,
            "total_secrets": len(self.secrets),
            "audit_entries": len(self.audit_ledger),
            "master_key_present": self.master_key is not None,
            "encryption": "Kyber-1024 + AES-256-GCM",
            "audit_ledger_hash": self.ledger_chain[-1][:16] + "..." if self.ledger_chain else "EMPTY"
        }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TEST 1: Store & Retrieve Secrets")
    print("="*60)
    vault = QuantumVault("prod-vault")
    
    vault.store_secret("api-key-1", "sk_live_abc123xyz")
    vault.store_secret("db-password", "P@ssw0rd!SecureDB")
    
    retrieved = vault.retrieve_secret("api-key-1")
    print(f"Retrieved: {retrieved['key_name']} = {retrieved['value']}")
    
    print("\n" + "="*60)
    print("TEST 2: Audit Ledger")
    print("="*60)
    ledger = vault.get_audit_ledger()
    print(f"Total audit entries: {ledger['total_entries']}")
    for entry in ledger['ledger']:
        print(f"  [{entry['timestamp']}] {entry['action']}: {entry['key_name']}")
    
    print("\n" + "="*60)
    print("TEST 3: Ledger Integrity Verification")
    print("="*60)
    integrity = vault.verify_ledger_integrity()
    print(f"Ledger Valid: {integrity['ledger_valid']}")
    print(f"Entries Verified: {integrity['entries_verified']}")
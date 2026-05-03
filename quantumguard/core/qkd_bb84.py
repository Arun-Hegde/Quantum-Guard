import random
import numpy as np
from typing import Tuple, List, Dict
from enum import Enum
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Basis(Enum):
    """Quantum basis: rectilinear (+) or diagonal (x)"""
    RECTILINEAR = "+"
    DIAGONAL = "x"

class Bit(Enum):
    """Qubit measurement result"""
    ZERO = 0
    ONE = 1

@dataclass
class BB84Session:
    """BB84 protocol session data"""
    num_qubits: int
    alice_bits: List[int]
    alice_bases: List[Basis]
    bob_bases: List[Basis]
    bob_measurements: List[int]
    eve_present: bool = False
    eve_bases: List[Basis] = None
    eve_measurements: List[int] = None
    sifted_key: List[int] = None
    qber: float = 0.0
    eve_detected: bool = False

class BB84QuantumKeyDistribution:
    """
    Simulates BB84 quantum key distribution protocol.
    Real use case: secure key bootstrap between bank branches or hospital nodes.
    """
    
    def __init__(self, num_qubits: int = 500, eve_eavesdrop: bool = False):
        self.num_qubits = num_qubits
        self.eve_eavesdrop = eve_eavesdrop
        self.session = None
        
    def generate_random_bits(self, count: int) -> List[int]:
        """Alice: generate random bits"""
        return [random.randint(0, 1) for _ in range(count)]
    
    def generate_random_bases(self, count: int) -> List[Basis]:
        """Generate random measurement bases"""
        return [random.choice(list(Basis)) for _ in range(count)]
    
    def encode_qubit(self, bit: int, basis: Basis) -> int:
        """Encode classical bit into 'qubit' using specified basis"""
        return bit
    
    def measure_qubit(self, encoded_bit: int, basis: Basis, correct_basis: Basis) -> int:
        """Measure qubit with given basis"""
        if basis == correct_basis:
            return encoded_bit
        else:
            return random.randint(0, 1)
    
    def run_protocol(self) -> BB84Session:
        """Execute full BB84 protocol"""
        logger.info(f"🔐 Starting BB84 QKD ({self.num_qubits} qubits)...")
        
        alice_bits = self.generate_random_bits(self.num_qubits)
        alice_bases = self.generate_random_bases(self.num_qubits)
        bob_bases = self.generate_random_bases(self.num_qubits)
        
        encoded_qubits = [self.encode_qubit(alice_bits[i], alice_bases[i]) 
                          for i in range(self.num_qubits)]
        
        eve_measurements = None
        eve_bases = None
        if self.eve_eavesdrop:
            eve_bases = self.generate_random_bases(self.num_qubits)
            eve_measurements = [self.measure_qubit(encoded_qubits[i], eve_bases[i], alice_bases[i])
                               for i in range(self.num_qubits)]
            logger.warning("⚠️  Eve is eavesdropping!")
            # Eve re-encodes in her basis — Bob now measures Eve's disturbed qubits
            intercepted_qubits = [self.encode_qubit(eve_measurements[i], eve_bases[i])
                                  for i in range(self.num_qubits)]
            bob_measurements = [self.measure_qubit(intercepted_qubits[i], bob_bases[i], eve_bases[i])
                               for i in range(self.num_qubits)]
        else:
            bob_measurements = [self.measure_qubit(encoded_qubits[i], bob_bases[i], alice_bases[i])
                               for i in range(self.num_qubits)]
        
        sifted_indices = [i for i in range(self.num_qubits) 
                         if alice_bases[i] == bob_bases[i]]
        sifted_key = [alice_bits[i] for i in sifted_indices]
        
        logger.info(f"✅ Sifted key length: {len(sifted_key)} bits")
        
        qber = self._calculate_qber(alice_bits, bob_measurements, sifted_indices)
        eve_detected = qber > 0.125
        
        if eve_detected:
            logger.warning(f"🚨 EAVESDROPPER DETECTED! QBER: {qber:.2%}")
        else:
            logger.info(f"✔️  Channel secure. QBER: {qber:.2%}")
        
        self.session = BB84Session(
            num_qubits=self.num_qubits,
            alice_bits=alice_bits,
            alice_bases=alice_bases,
            bob_bases=bob_bases,
            bob_measurements=bob_measurements,
            eve_present=self.eve_eavesdrop,
            eve_bases=eve_bases,
            eve_measurements=eve_measurements,
            sifted_key=sifted_key,
            qber=qber,
            eve_detected=eve_detected
        )
        
        return self.session
    
    def _calculate_qber(self, alice_bits: List[int], bob_measurements: List[int], 
                        sifted_indices: List[int]) -> float:
        """Calculate Quantum Bit Error Rate"""
        if not sifted_indices:
            return 0.0
        
        errors = sum(1 for i in sifted_indices if alice_bits[i] != bob_measurements[i])
        qber = errors / len(sifted_indices)
        return qber
    
    def get_session_summary(self) -> Dict:
        """Return session statistics"""
        if not self.session:
            return {"error": "No session executed"}
        
        return {
            "total_qubits": self.session.num_qubits,
            "sifted_key_length": len(self.session.sifted_key),
            "sifted_key_sample": "".join(map(str, self.session.sifted_key[:32])),
            "qber": f"{self.session.qber:.2%}",
            "eve_present": self.session.eve_present,
            "eve_detected": self.session.eve_detected,
            "secure": not self.session.eve_detected
        }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TEST 1: Secure Channel (No Eve)")
    print("="*60)
    qkd = BB84QuantumKeyDistribution(num_qubits=1000, eve_eavesdrop=False)
    session = qkd.run_protocol()
    print(qkd.get_session_summary())
    
    print("\n" + "="*60)
    print("TEST 2: Eavesdropping Detected")
    print("="*60)
    qkd_eve = BB84QuantumKeyDistribution(num_qubits=1000, eve_eavesdrop=True)
    session_eve = qkd_eve.run_protocol()
    print(qkd_eve.get_session_summary())
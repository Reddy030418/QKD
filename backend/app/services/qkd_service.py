import random
import string
import json
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from ..models import QKDSession, QKDSessionLog
from ..core.database import SessionLocal

logger = logging.getLogger(__name__)

class QKDProtocolService:
    """BB84 Quantum Key Distribution Protocol Implementation"""

    def __init__(self):
        self.active_sessions = {}

    def generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    def generate_random_bits(self, length: int) -> List[int]:
        """Generate random bits (0 or 1)"""
        return [random.randint(0, 1) for _ in range(length)]

    def generate_random_bases(self, length: int) -> List[int]:
        """Generate random bases (0 = rectilinear, 1 = diagonal)"""
        return [random.randint(0, 1) for _ in range(length)]

    def polarize_photon(self, bit: int, basis: int) -> int:
        """Simulate photon polarization based on bit and basis"""
        # Rectilinear basis: 0° (bit 0) or 90° (bit 1)
        # Diagonal basis: 45° (bit 0) or 135° (bit 1)
        if basis == 0:  # Rectilinear
            return 0 if bit == 0 else 90  # 0° or 90°
        else:  # Diagonal
            return 45 if bit == 0 else 135  # 45° or 135°

    def measure_photon(self, polarization: int, measurement_basis: int,
                      noise_level: float, detector_efficiency: float) -> Optional[int]:
        """Simulate photon measurement with quantum noise"""

        # Random detection failure based on efficiency
        if random.random() > detector_efficiency / 100:
            return None  # Photon not detected

        measured_bit = None

        # Perfect measurement if bases match
        if ((polarization == 0 or polarization == 90) and measurement_basis == 0):
            # Rectilinear photon measured with rectilinear base
            measured_bit = 0 if polarization == 0 else 1
        elif ((polarization == 45 or polarization == 135) and measurement_basis == 1):
            # Diagonal photon measured with diagonal base
            measured_bit = 0 if polarization == 45 else 1
        else:
            # Wrong base - random result (50/50)
            measured_bit = random.randint(0, 1)

        # Apply quantum noise
        if random.random() < noise_level / 100:
            measured_bit = 1 - measured_bit  # Flip bit due to noise

        return measured_bit

    def simulate_eavesdropping(self, alice_polarizations: List[int],
                             alice_bases: List[int], noise_level: float) -> List[int]:
        """Simulate eavesdropper (Eve) intercepting and measuring photons"""
        eve_bases = self.generate_random_bases(len(alice_polarizations))
        eve_measurements = []

        for i, polarization in enumerate(alice_polarizations):
            # Eve measures with random basis
            measured_bit = self.measure_photon(polarization, eve_bases[i], noise_level, 100)
            eve_measurements.append(measured_bit)

            # Eve resends photon (this introduces additional noise)
            if measured_bit is not None:
                # Eve's measurement disturbs the quantum state
                # This will be reflected in increased noise for Bob
                pass

        return eve_measurements

    def sift_keys(self, alice_bits: List[int], alice_bases: List[int],
                 bob_bases: List[int], bob_measurements: List[Optional[int]]) -> Tuple[List[int], List[int], List[int]]:
        """Sift keys by comparing bases"""

        sifted_alice = []
        sifted_bob = []
        matching_bases = []

        for i in range(len(alice_bases)):
            if alice_bases[i] == bob_bases[i] and bob_measurements[i] is not None:
                sifted_alice.append(alice_bits[i])
                sifted_bob.append(bob_measurements[i])
                matching_bases.append(1)  # Mark as matching
            else:
                matching_bases.append(0)  # Mark as non-matching

        return sifted_alice, sifted_bob, matching_bases

    def perform_error_correction(self, sifted_alice: List[int], sifted_bob: List[int]) -> Tuple[List[int], float]:
        """Perform error detection and correction"""

        if len(sifted_alice) == 0:
            return [], 0.0

        # Sample a portion of the key for error detection (usually 10-20%)
        sample_size = max(1, len(sifted_alice) // 10)
        error_count = 0

        for i in range(sample_size):
            if sifted_alice[i] != sifted_bob[i]:
                error_count += 1

        error_rate = (error_count / sample_size * 100) if sample_size > 0 else 0.0

        # Use remaining bits for final key (after error detection)
        final_key = []
        for i in range(sample_size, len(sifted_alice)):
            if sifted_alice[i] == sifted_bob[i]:
                final_key.append(sifted_alice[i])

        return final_key, error_rate

    async def run_bb84_protocol(self, parameters: Dict) -> Dict:
        """Run the complete BB84 protocol simulation"""

        session_id = self.generate_session_id()
        key_length = parameters.get('key_length', 50)
        noise_level = parameters.get('noise_level', 5.0)
        detector_efficiency = parameters.get('detector_efficiency', 95.0)
        eavesdropper_present = parameters.get('eavesdropper_present', False)

        # Initialize session data
        session_data = {
            'session_id': session_id,
            'status': 'running',
            'alice_bits': [],
            'alice_bases': [],
            'alice_polarizations': [],
            'bob_bases': [],
            'bob_measurements': [],
            'sifted_alice': [],
            'sifted_bob': [],
            'final_key': [],
            'stats': {
                'transmitted': key_length,
                'detected': 0,
                'error_rate': 0.0,
                'final_key_length': 0
            }
        }

        self.active_sessions[session_id] = session_data

        try:
            # Step 1: Alice generates random bits and bases
            alice_bits = self.generate_random_bits(key_length)
            alice_bases = self.generate_random_bases(key_length)

            # Generate polarizations
            alice_polarizations = [
                self.polarize_photon(alice_bits[i], alice_bases[i])
                for i in range(key_length)
            ]

            session_data['alice_bits'] = alice_bits
            session_data['alice_bases'] = alice_bases
            session_data['alice_polarizations'] = alice_polarizations

            # Step 2: Simulate eavesdropping if present
            if eavesdropper_present:
                eve_measurements = self.simulate_eavesdropping(
                    alice_polarizations, alice_bases, noise_level
                )
                # Eavesdropping increases effective noise
                effective_noise = noise_level + 15
            else:
                effective_noise = noise_level

            # Step 3: Bob generates measurement bases and measures photons
            bob_bases = self.generate_random_bases(key_length)
            bob_measurements = []

            detected_count = 0
            for i in range(key_length):
                measured_bit = self.measure_photon(
                    alice_polarizations[i],
                    bob_bases[i],
                    effective_noise,
                    detector_efficiency
                )
                bob_measurements.append(measured_bit)
                if measured_bit is not None:
                    detected_count += 1

            session_data['bob_bases'] = bob_bases
            session_data['bob_measurements'] = bob_measurements
            session_data['stats']['detected'] = detected_count

            # Step 4: Basis reconciliation and key sifting
            sifted_alice, sifted_bob, matching_bases = self.sift_keys(
                alice_bits, alice_bases, bob_bases, bob_measurements
            )

            session_data['sifted_alice'] = sifted_alice
            session_data['sifted_bob'] = sifted_bob

            # Step 5: Error detection and correction
            final_key, error_rate = self.perform_error_correction(sifted_alice, sifted_bob)

            session_data['final_key'] = final_key
            session_data['stats']['error_rate'] = error_rate
            session_data['stats']['final_key_length'] = len(final_key)

            # Step 6: Security assessment
            security_status = "secure" if error_rate <= 11 else "compromised"

            session_data['status'] = 'completed'
            session_data['security_status'] = security_status

            # Save to database
            await self.save_session_to_db(session_data, parameters)

            return {
                'session_id': session_id,
                'status': 'completed',
                'alice_bits': alice_bits,
                'alice_bases': alice_bases,
                'bob_bases': bob_bases,
                'bob_measurements': bob_measurements,
                'sifted_alice': sifted_alice,
                'sifted_bob': sifted_bob,
                'final_key': final_key,
                'stats': session_data['stats'],
                'security_status': security_status,
                'error_rate': error_rate
            }

        except Exception as e:
            logger.error(f"Error in BB84 protocol simulation: {e}")
            session_data['status'] = 'error'
            return {
                'session_id': session_id,
                'status': 'error',
                'error': str(e)
            }

    async def save_session_to_db(self, session_data: Dict, parameters: Dict):
        """Save session data to database"""
        try:
            db = SessionLocal()
            session = QKDSession(
                session_id=session_data['session_id'],
                key_length=parameters.get('key_length', 50),
                noise_level=parameters.get('noise_level', 5.0),
                detector_efficiency=parameters.get('detector_efficiency', 95.0),
                eavesdropper_present=parameters.get('eavesdropper_present', False),
                alice_bits=json.dumps(session_data['alice_bits']),
                alice_bases=json.dumps(session_data['alice_bases']),
                bob_bases=json.dumps(session_data['bob_bases']),
                bob_measurements=json.dumps(session_data['bob_measurements']),
                sifted_key_alice=json.dumps(session_data['sifted_alice']),
                sifted_key_bob=json.dumps(session_data['sifted_bob']),
                final_shared_key=json.dumps(session_data['final_key']),
                transmitted_photons=session_data['stats']['transmitted'],
                detected_photons=session_data['stats']['detected'],
                quantum_error_rate=session_data['stats']['error_rate'],
                final_key_length=session_data['stats']['final_key_length'],
                status=session_data['status'],
                security_status=session_data['security_status']
            )

            db.add(session)
            db.commit()
            db.refresh(session)

            # Add log entry
            log_entry = QKDSessionLog(
                session_id=session_data['session_id'],
                level="INFO",
                message=f"QKD session {session_data['session_id']} completed successfully",
                data=session_data['stats']
            )
            db.add(log_entry)
            db.commit()

        except Exception as e:
            logger.error(f"Error saving session to database: {e}")
        finally:
            db.close()

# Global QKD service instance
qkd_service = QKDProtocolService()

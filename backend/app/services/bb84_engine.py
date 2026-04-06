import random
from typing import Dict, List, Optional, Tuple


class BB84Engine:
    """Pure BB84 simulation engine (processing + transformation layers)."""

    def generate_random_bits(self, length: int) -> List[int]:
        return [random.randint(0, 1) for _ in range(length)]

    def generate_random_bases(self, length: int) -> List[int]:
        return [random.randint(0, 1) for _ in range(length)]

    def polarize_photon(self, bit: int, basis: int) -> int:
        if basis == 0:
            return 0 if bit == 0 else 90
        return 45 if bit == 0 else 135

    def measure_photon(
        self,
        polarization: int,
        measurement_basis: int,
        noise_level: float,
        detector_efficiency: float,
    ) -> Optional[int]:
        if random.random() > detector_efficiency / 100:
            return None

        if ((polarization in (0, 90)) and measurement_basis == 0):
            measured_bit = 0 if polarization == 0 else 1
        elif ((polarization in (45, 135)) and measurement_basis == 1):
            measured_bit = 0 if polarization == 45 else 1
        else:
            measured_bit = random.randint(0, 1)

        if random.random() < noise_level / 100:
            measured_bit = 1 - measured_bit

        return measured_bit

    def simulate_eavesdropping(self, alice_polarizations: List[int], noise_level: float) -> None:
        eve_bases = self.generate_random_bases(len(alice_polarizations))
        for i, polarization in enumerate(alice_polarizations):
            self.measure_photon(polarization, eve_bases[i], noise_level, 100)

    def sift_keys(
        self,
        alice_bits: List[int],
        alice_bases: List[int],
        bob_bases: List[int],
        bob_measurements: List[Optional[int]],
    ) -> Tuple[List[int], List[int]]:
        sifted_alice: List[int] = []
        sifted_bob: List[int] = []

        for i in range(len(alice_bases)):
            if alice_bases[i] == bob_bases[i] and bob_measurements[i] is not None:
                sifted_alice.append(alice_bits[i])
                sifted_bob.append(bob_measurements[i])

        return sifted_alice, sifted_bob

    def perform_error_correction(self, sifted_alice: List[int], sifted_bob: List[int]) -> Tuple[List[int], float]:
        if not sifted_alice:
            return [], 0.0

        sample_size = max(1, len(sifted_alice) // 10)
        error_count = sum(1 for i in range(sample_size) if sifted_alice[i] != sifted_bob[i])
        qber = (error_count / sample_size) * 100

        final_key = [
            sifted_alice[i]
            for i in range(sample_size, len(sifted_alice))
            if sifted_alice[i] == sifted_bob[i]
        ]

        return final_key, qber

    def run(self, parameters: Dict) -> Dict:
        key_length = parameters.get("key_length", 50)
        noise_level = parameters.get("noise_level", 5.0)
        detector_efficiency = parameters.get("detector_efficiency", 95.0)
        eavesdropper_present = parameters.get("eavesdropper_present", False)

        alice_bits = self.generate_random_bits(key_length)
        alice_bases = self.generate_random_bases(key_length)
        alice_polarizations = [
            self.polarize_photon(alice_bits[i], alice_bases[i])
            for i in range(key_length)
        ]

        effective_noise = noise_level
        if eavesdropper_present:
            self.simulate_eavesdropping(alice_polarizations, noise_level)
            effective_noise = min(30.0, noise_level + 15)

        bob_bases = self.generate_random_bases(key_length)
        bob_measurements: List[Optional[int]] = []
        detected_count = 0

        for i in range(key_length):
            measured_bit = self.measure_photon(
                alice_polarizations[i],
                bob_bases[i],
                effective_noise,
                detector_efficiency,
            )
            bob_measurements.append(measured_bit)
            if measured_bit is not None:
                detected_count += 1

        sifted_alice, sifted_bob = self.sift_keys(alice_bits, alice_bases, bob_bases, bob_measurements)
        final_key, qber = self.perform_error_correction(sifted_alice, sifted_bob)

        final_key_length = len(final_key)
        key_rate = (final_key_length / key_length) if key_length > 0 else 0.0
        security_status = "secure" if qber <= 11 else "compromised"

        return {
            "alice_bits": alice_bits,
            "alice_bases": alice_bases,
            "alice_polarizations": alice_polarizations,
            "bob_bases": bob_bases,
            "bob_measurements": bob_measurements,
            "sifted_alice": sifted_alice,
            "sifted_bob": sifted_bob,
            "final_key": final_key,
            "metrics": {
                "transmitted": key_length,
                "detected": detected_count,
                "qber": round(qber, 4),
                "error_rate": round(qber, 4),
                "key_rate": round(key_rate, 6),
                "final_key_length": final_key_length,
                "security_status": security_status,
            },
        }

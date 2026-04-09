#!/usr/bin/env python3
"""
Script to populate the database with sample QKD sessions for dashboard testing
"""
import sys
import os
import json
from datetime import datetime, timedelta
import random

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app.core.database import db, init_db
    from app.models.qkd_session import QKDSession, QKDSessionLog
    from app.main import app
    from flask import Flask

    print("🔄 Initializing database connection...")

    # Initialize the app context
    with app.app_context():
        # Clear existing data
        print("🧹 Clearing existing session data...")
        QKDSessionLog.query.delete()
        QKDSession.query.delete()
        db.session.commit()

        # Sample data parameters
        num_sessions = 25
        base_time = datetime.utcnow() - timedelta(days=30)

        print(f"📊 Creating {num_sessions} sample QKD sessions...")

        for i in range(num_sessions):
            # Generate realistic QKD parameters
            key_length = random.randint(50, 200)
            noise_level = round(random.uniform(1.0, 15.0), 2)
            detector_efficiency = round(random.uniform(85.0, 98.0), 2)
            eavesdropper_present = random.choice([True, False])

            # Calculate realistic results
            transmitted_photons = key_length * 2
            detected_photons = int(transmitted_photons * (detector_efficiency / 100))
            quantum_error_rate = round(noise_level * 0.8, 2) if not eavesdropper_present else round(random.uniform(15.0, 35.0), 2)
            final_key_length = int(key_length * (1 - quantum_error_rate / 100))

            # Determine status and security
            if quantum_error_rate > 25:
                status = 'error'
                security_status = 'compromised'
            elif quantum_error_rate > 15:
                status = 'completed'
                security_status = 'compromised'
            else:
                status = 'completed'
                security_status = 'secure'

            # Create session
            session = QKDSession(
                session_id=f"sample_session_{(i+1):03d}",
                user_id=1,  # Default user
                key_length=key_length,
                noise_level=noise_level,
                detector_efficiency=detector_efficiency,
                eavesdropper_present=eavesdropper_present,
                transmitted_photons=transmitted_photons,
                detected_photons=detected_photons,
                quantum_error_rate=quantum_error_rate,
                final_key_length=final_key_length,
                status=status,
                security_status=security_status,
                created_at=base_time + timedelta(hours=i*24),
                completed_at=base_time + timedelta(hours=i*24 + random.randint(1, 4)) if status == 'completed' else None
            )

            # Add sample key data
            alice_bits = [random.randint(0, 1) for _ in range(key_length)]
            alice_bases = [random.randint(0, 1) for _ in range(key_length)]
            bob_bases = [random.randint(0, 1) for _ in range(key_length)]
            bob_measurements = [random.randint(0, 1) for _ in range(key_length)]

            session.alice_bits_list = alice_bits
            session.alice_bases_list = alice_bases
            session.bob_bases_list = bob_bases
            session.bob_measurements_list = bob_measurements

            # Create sifted keys (where bases match)
            sifted_indices = [j for j in range(key_length) if alice_bases[j] == bob_bases[j]]
            sifted_key_alice = [alice_bits[j] for j in sifted_indices]
            sifted_key_bob = [bob_measurements[j] for j in sifted_indices]

            session.sifted_key_alice_list = sifted_key_alice
            session.sifted_key_bob_list = sifted_key_bob

            # Final key (remove errors)
            final_key = []
            for j, bit in enumerate(sifted_key_alice):
                if j < len(sifted_key_bob) and bit == sifted_key_bob[j]:
                    final_key.append(bit)

            session.final_shared_key_list = final_key

            db.session.add(session)

            # Add some log entries for each session
            log_messages = [
                "QKD session initialized",
                "Alice generated random bits and bases",
                "Bob received photons and measured",
                "Sifting process completed",
                "Error correction applied",
                "Privacy amplification completed"
            ]

            for log_msg in log_messages:
                log = QKDSessionLog(
                    session_id=session.session_id,
                    level='INFO',
                    message=log_msg,
                    timestamp=session.created_at + timedelta(minutes=random.randint(1, 10))
                )
                db.session.add(log)

        # Commit all changes
        db.session.commit()

        print("✅ Sample data created successfully!")

        # Verify the data
        total_sessions = QKDSession.query.count()
        successful_sessions = QKDSession.query.filter_by(status='completed').count()
        compromised_sessions = QKDSession.query.filter_by(security_status='compromised').count()

        print("\n📈 Statistics Summary:")
        print(f"   Total sessions: {total_sessions}")
        print(f"   Successful sessions: {successful_sessions}")
        print(f"   Compromised sessions: {compromised_sessions}")
        success_rate = (successful_sessions / total_sessions * 100) if total_sessions > 0 else 0
        print(f"   Success rate: {success_rate:.1f}%")

        # Test the stats endpoint
        from app.sessions import get_session_stats
        stats = get_session_stats()

        print("\n📊 API Response Preview:")
        print(f"   Total sessions: {stats[0].json['total_sessions']}")
        print(f"   Successful sessions: {stats[0].json['successful_sessions']}")
        print(f"   Compromised sessions: {stats[0].json['compromised_sessions']}")
        print(f"   Success rate: {stats[0].json['success_rate']:.1f}%")
        print(f"   Average error rate: {stats[0].json['average_error_rate']:.2f}%")
        print(f"   Average key length: {stats[0].json['average_key_length']:.1f}")

        print("\n🎉 Database populated successfully!")
        print("The dashboard should now display meaningful statistics.")

except Exception as e:
    print(f"❌ Error populating database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

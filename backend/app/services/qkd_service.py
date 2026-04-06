import random
import string
from datetime import datetime
from typing import Dict, Optional
import logging

from ..models import QKDSession, QKDSessionLog
from ..core.database import SessionLocal
from ..websockets.manager import manager
from .bb84_engine import BB84Engine

logger = logging.getLogger(__name__)


class QKDProtocolService:
    """ETL orchestrator for BB84 simulations."""

    def __init__(self):
        self.active_sessions = {}
        self.engine = BB84Engine()

    def generate_session_id(self) -> str:
        return "".join(random.choices(string.ascii_letters + string.digits, k=16))

    async def run_bb84_protocol(self, parameters: Dict, user_id: Optional[int] = None) -> Dict:
        session_id = parameters.get("session_id") or self.generate_session_id()

        session_data = {
            "session_id": session_id,
            "status": "running",
            "alice_bits": [],
            "alice_bases": [],
            "bob_bases": [],
            "bob_measurements": [],
            "sifted_alice": [],
            "sifted_bob": [],
            "final_key": [],
            "stats": {
                "transmitted": parameters.get("key_length", 50),
                "detected": 0,
                "qber": 0.0,
                "error_rate": 0.0,
                "key_rate": 0.0,
                "final_key_length": 0,
            },
            "security_status": "unknown",
        }

        self.active_sessions[session_id] = session_data

        try:
            await manager.send_qkd_progress(
                session_id, "bit_generation", 20, {"message": "Generating bits and bases"}
            )

            await manager.send_qkd_progress(
                session_id, "transmission", 50, {"message": "Transmitting and measuring photons"}
            )

            engine_result = self.engine.run(parameters)

            await manager.send_qkd_progress(
                session_id, "sifting", 75, {"message": "Sifting key and estimating QBER"}
            )

            metrics = engine_result["metrics"]
            security_status = metrics["security_status"]

            session_data.update(
                {
                    "alice_bits": engine_result["alice_bits"],
                    "alice_bases": engine_result["alice_bases"],
                    "bob_bases": engine_result["bob_bases"],
                    "bob_measurements": engine_result["bob_measurements"],
                    "sifted_alice": engine_result["sifted_alice"],
                    "sifted_bob": engine_result["sifted_bob"],
                    "final_key": engine_result["final_key"],
                    "stats": {
                        "transmitted": metrics["transmitted"],
                        "detected": metrics["detected"],
                        "qber": metrics["qber"],
                        "error_rate": metrics["error_rate"],
                        "key_rate": metrics["key_rate"],
                        "final_key_length": metrics["final_key_length"],
                    },
                    "status": "completed",
                    "security_status": security_status,
                }
            )

            await manager.send_qkd_progress(
                session_id, "final_key", 95, {"message": "Final shared key generated"}
            )

            await self.save_session_to_db(session_data, parameters, user_id=user_id)

            await manager.send_qkd_progress(
                session_id, "completed", 100, {"message": "Simulation completed"}
            )

            return {
                "session_id": session_id,
                "status": "completed",
                "alice_bits": session_data["alice_bits"],
                "alice_bases": session_data["alice_bases"],
                "bob_bases": session_data["bob_bases"],
                "bob_measurements": session_data["bob_measurements"],
                "sifted_alice": session_data["sifted_alice"],
                "sifted_bob": session_data["sifted_bob"],
                "final_key": session_data["final_key"],
                "stats": session_data["stats"],
                "security_status": session_data["security_status"],
                "error_rate": session_data["stats"]["error_rate"],
                "qber": session_data["stats"]["qber"],
                "key_rate": session_data["stats"]["key_rate"],
            }

        except Exception as e:
            logger.error("Error in BB84 protocol simulation: %s", e)
            session_data["status"] = "error"
            return {
                "session_id": session_id,
                "status": "error",
                "error": str(e),
            }

    async def save_session_to_db(self, session_data: Dict, parameters: Dict, user_id: Optional[int] = None):
        db = SessionLocal()
        try:
            session = QKDSession(
                session_id=session_data["session_id"],
                user_id=user_id,
                key_length=parameters.get("key_length", 50),
                noise_level=parameters.get("noise_level", 5.0),
                detector_efficiency=parameters.get("detector_efficiency", 95.0),
                eavesdropper_present=parameters.get("eavesdropper_present", False),
                alice_bits=session_data["alice_bits"],
                alice_bases=session_data["alice_bases"],
                bob_bases=session_data["bob_bases"],
                bob_measurements=session_data["bob_measurements"],
                sifted_key_alice=session_data["sifted_alice"],
                sifted_key_bob=session_data["sifted_bob"],
                final_shared_key=session_data["final_key"],
                transmitted_photons=session_data["stats"]["transmitted"],
                detected_photons=session_data["stats"]["detected"],
                quantum_error_rate=session_data["stats"]["qber"],
                final_key_length=session_data["stats"]["final_key_length"],
                status=session_data["status"],
                security_status=session_data["security_status"],
                completed_at=datetime.utcnow(),
            )

            db.add(session)
            db.commit()

            log_entry = QKDSessionLog(
                session_id=session_data["session_id"],
                level="INFO",
                message=f"QKD session {session_data['session_id']} completed successfully",
                data={
                    **session_data["stats"],
                    "user_id": user_id,
                    "parameters": {
                        "key_length": parameters.get("key_length", 50),
                        "noise_level": parameters.get("noise_level", 5.0),
                        "detector_efficiency": parameters.get("detector_efficiency", 95.0),
                        "eavesdropper_present": parameters.get("eavesdropper_present", False),
                    },
                },
            )
            db.add(log_entry)
            db.commit()

        except Exception as e:
            logger.error("Error saving session to database: %s", e)
            db.rollback()
            raise
        finally:
            db.close()


qkd_service = QKDProtocolService()

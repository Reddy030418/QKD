from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class SessionListItem(BaseModel):
    id: int
    session_id: str
    user_id: Optional[int] = None
    key_length: int
    noise_level: float
    detector_efficiency: float
    eavesdropper_present: bool
    transmitted_photons: int
    detected_photons: int
    quantum_error_rate: float
    final_key_length: int
    status: str
    security_status: str
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


class SessionLogItem(BaseModel):
    id: int
    timestamp: Optional[str] = None
    level: str
    message: str
    data: Optional[Dict[str, Any]] = None


class SessionDetailResponse(BaseModel):
    id: int
    session_id: str
    user_id: Optional[int] = None
    key_length: int
    noise_level: float
    detector_efficiency: float
    eavesdropper_present: bool
    alice_bits: Optional[Any] = None
    alice_bases: Optional[Any] = None
    bob_bases: Optional[Any] = None
    bob_measurements: Optional[Any] = None
    sifted_key_alice: Optional[Any] = None
    sifted_key_bob: Optional[Any] = None
    final_shared_key: Optional[Any] = None
    transmitted_photons: int
    detected_photons: int
    quantum_error_rate: float
    final_key_length: int
    status: str
    security_status: str
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    logs: List[SessionLogItem]


class SessionSummaryStatsResponse(BaseModel):
    total_sessions: int
    successful_sessions: int
    compromised_sessions: int
    success_rate: float
    compromise_rate: float
    average_error_rate: float
    average_key_length: float
    confusion_matrix: Dict[str, int]
    f1_score: float


class DeleteSessionResponse(BaseModel):
    message: str

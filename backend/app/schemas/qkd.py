from typing import List, Optional, Literal
from pydantic import BaseModel, Field, validator


class QKDRunRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, min_length=8, max_length=64)
    key_length: int = Field(default=50, ge=10, le=500)
    noise_level: float = Field(default=5.0, ge=0, le=30)
    detector_efficiency: float = Field(default=95.0, ge=70, le=100)
    eavesdropper_present: bool = False

    @validator("noise_level", "detector_efficiency", pre=True)
    def normalize_float_fields(cls, value):
        return round(float(value), 2)


class QKDStatsResponse(BaseModel):
    transmitted: int
    detected: int
    qber: float
    error_rate: float
    key_rate: float
    final_key_length: int


class QKDRunResponse(BaseModel):
    session_id: str
    status: Literal["completed", "error"]
    alice_bits: List[int] = []
    alice_bases: List[int] = []
    bob_bases: List[int] = []
    bob_measurements: List[Optional[int]] = []
    sifted_alice: List[int] = []
    sifted_bob: List[int] = []
    final_key: List[int] = []
    stats: Optional[QKDStatsResponse] = None
    security_status: Optional[Literal["secure", "compromised"]] = None
    error_rate: Optional[float] = None
    qber: Optional[float] = None
    key_rate: Optional[float] = None
    error: Optional[str] = None


class QKDSessionInfoResponse(BaseModel):
    session_id: str
    status: str
    message: str
    requested_by: str


class QKDSystemStatsResponse(BaseModel):
    total_sessions: int
    successful_sessions: int
    average_key_length: int
    average_error_rate: float
    security_incidents: int
    requested_by: str

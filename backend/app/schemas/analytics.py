from typing import List
from pydantic import BaseModel


class AnalyticsSummaryResponse(BaseModel):
    total_sessions: int
    secure_sessions: int
    compromised_sessions: int
    secure_ratio: float
    compromise_ratio: float
    average_qber: float
    average_key_rate: float
    noise_error_correlation: float


class TrendPoint(BaseModel):
    date: str
    value: float


class SecurityTrendPoint(BaseModel):
    date: str
    secure: int
    compromised: int


class TrendsPagination(BaseModel):
    page: int
    page_size: int
    total_points: int


class AnalyticsTrendsResponse(BaseModel):
    qber_trend: List[TrendPoint]
    key_rate_trend: List[TrendPoint]
    security_trend: List[SecurityTrendPoint]
    pagination: TrendsPagination


class AnalyticsUserInfo(BaseModel):
    id: int
    username: str
    role: str


class AnalyticsUserMetrics(BaseModel):
    total_sessions: int
    secure_sessions: int
    compromised_sessions: int
    secure_ratio: float
    compromise_ratio: float
    average_qber: float
    average_key_rate: float


class AnalyticsUserResponse(BaseModel):
    user: AnalyticsUserInfo
    metrics: AnalyticsUserMetrics

from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import case, func
import math

from ..core.database import get_db
from ..core.audit import log_audit_event
from ..models import QKDSession, User
from ..services.auth_service import require_admin, require_roles
from ..schemas import AnalyticsSummaryResponse, AnalyticsTrendsResponse, AnalyticsUserResponse

router = APIRouter()


def _apply_date_filters(query, date_from: date | None, date_to: date | None):
    if date_from is not None:
        query = query.filter(func.date(QKDSession.created_at) >= date_from)
    if date_to is not None:
        query = query.filter(func.date(QKDSession.created_at) <= date_to)
    return query


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def analytics_summary(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    log_audit_event("analytics.summary", actor=current_user, outcome="success")
    base = db.query(QKDSession)
    base = _apply_date_filters(base, date_from, date_to)

    total_sessions = base.count()

    secure_sessions = base.filter(QKDSession.security_status == "secure").count()
    compromised_sessions = base.filter(QKDSession.security_status == "compromised").count()

    averages = base.with_entities(
        func.avg(QKDSession.quantum_error_rate),
        func.avg(
            case(
                [(QKDSession.transmitted_photons > 0, QKDSession.final_key_length * 1.0 / QKDSession.transmitted_photons)],
                else_=0.0,
            )
        ),
    ).first()

    avg_qber = float(averages[0] or 0.0)
    avg_key_rate = float(averages[1] or 0.0)

    paired = base.with_entities(QKDSession.noise_level, QKDSession.quantum_error_rate).filter(
        QKDSession.noise_level.isnot(None),
        QKDSession.quantum_error_rate.isnot(None),
    ).all()

    correlation = 0.0
    if len(paired) > 1:
        xs = [float(p[0]) for p in paired]
        ys = [float(p[1]) for p in paired]
        mean_x = sum(xs) / len(xs)
        mean_y = sum(ys) / len(ys)
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
        den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
        den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
        correlation = numerator / (den_x * den_y) if den_x > 0 and den_y > 0 else 0.0

    secure_ratio = (secure_sessions / total_sessions * 100) if total_sessions > 0 else 0.0
    compromise_ratio = (compromised_sessions / total_sessions * 100) if total_sessions > 0 else 0.0

    return {
        "total_sessions": total_sessions,
        "secure_sessions": secure_sessions,
        "compromised_sessions": compromised_sessions,
        "secure_ratio": round(secure_ratio, 2),
        "compromise_ratio": round(compromise_ratio, 2),
        "average_qber": round(avg_qber, 4),
        "average_key_rate": round(avg_key_rate, 6),
        "noise_error_correlation": round(correlation, 4),
    }


@router.get("/trends", response_model=AnalyticsTrendsResponse)
async def analytics_trends(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=30, ge=1, le=180),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    log_audit_event("analytics.trends", actor=current_user, outcome="success")
    day_col = func.date(QKDSession.created_at)

    grouped_base = db.query(
        day_col.label("day"),
        func.avg(QKDSession.quantum_error_rate).label("avg_qber"),
        func.avg(
            case(
                [(QKDSession.transmitted_photons > 0, QKDSession.final_key_length * 1.0 / QKDSession.transmitted_photons)],
                else_=0.0,
            )
        ).label("avg_key_rate"),
        func.sum(case([(QKDSession.security_status == "secure", 1)], else_=0)).label("secure_count"),
        func.sum(case([(QKDSession.security_status == "compromised", 1)], else_=0)).label("compromised_count"),
    )

    grouped_base = _apply_date_filters(grouped_base, date_from, date_to)
    grouped_base = grouped_base.group_by(day_col)

    total_points = grouped_base.count()
    offset = (page - 1) * page_size

    rows = (
        grouped_base
        .order_by(day_col.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    rows = list(reversed(rows))

    qber_trend = [{"date": str(r.day), "value": round(float(r.avg_qber or 0.0), 4)} for r in rows]
    key_rate_trend = [{"date": str(r.day), "value": round(float(r.avg_key_rate or 0.0), 6)} for r in rows]
    security_trend = [
        {
            "date": str(r.day),
            "secure": int(r.secure_count or 0),
            "compromised": int(r.compromised_count or 0),
        }
        for r in rows
    ]

    return {
        "qber_trend": qber_trend,
        "key_rate_trend": key_rate_trend,
        "security_trend": security_trend,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_points": total_points,
        },
    }


@router.get("/user/{user_id}", response_model=AnalyticsUserResponse)
async def analytics_user(
    user_id: int,
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "user")),
):
    if current_user.role != "admin" and current_user.id != user_id:
        log_audit_event(
            "analytics.user",
            actor=current_user,
            target=f"user_id:{user_id}",
            outcome="failure",
            reason="forbidden",
        )
        raise HTTPException(status_code=403, detail="Not authorized to view this user's analytics")

    log_audit_event(
        "analytics.user",
        actor=current_user,
        target=f"user_id:{user_id}",
        outcome="success",
    )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = db.query(QKDSession).filter(QKDSession.user_id == user_id)
    query = _apply_date_filters(query, date_from, date_to)

    total_sessions = query.count()
    secure_sessions = query.filter(QKDSession.security_status == "secure").count()
    compromised_sessions = query.filter(QKDSession.security_status == "compromised").count()

    averages = query.with_entities(
        func.avg(QKDSession.quantum_error_rate),
        func.avg(
            case(
                [(QKDSession.transmitted_photons > 0, QKDSession.final_key_length * 1.0 / QKDSession.transmitted_photons)],
                else_=0.0,
            )
        ),
    ).first()

    avg_qber = float(averages[0] or 0.0)
    avg_key_rate = float(averages[1] or 0.0)
    secure_ratio = (secure_sessions / total_sessions * 100) if total_sessions > 0 else 0.0
    compromise_ratio = (compromised_sessions / total_sessions * 100) if total_sessions > 0 else 0.0

    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
        },
        "metrics": {
            "total_sessions": total_sessions,
            "secure_sessions": secure_sessions,
            "compromised_sessions": compromised_sessions,
            "secure_ratio": round(secure_ratio, 2),
            "compromise_ratio": round(compromise_ratio, 2),
            "average_qber": round(avg_qber, 4),
            "average_key_rate": round(avg_key_rate, 6),
        },
    }

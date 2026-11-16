
from fastapi import APIRouter, Query

from app.services.anomaly_detection import anomaly_detector


router = APIRouter(
    prefix="/anomalies",
    tags=["Anomaly Detection"],
)


@router.post("/analyze")
async def analyze_traffic():
    """
    Analyze the latest traffic history sample
    and detect unusual bandwidth peaks.
    """

    result = anomaly_detector.analyze_latest_sample()

    return {
        "message": "Traffic anomaly analysis completed.",
        "data": result,
    }


@router.get("/alerts")
async def get_anomaly_alerts(
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of alerts to return.",
    ),
):
    alerts = anomaly_detector.get_alerts(limit=limit)

    return {
        "message": "Anomaly alerts retrieved successfully.",
        "total_alerts": len(alerts),
        "alerts": alerts,
    }


@router.get("/status")
async def get_anomaly_status():
    return {
        "message": "Anomaly detection status retrieved successfully.",
        "data": anomaly_detector.get_status(),
    }

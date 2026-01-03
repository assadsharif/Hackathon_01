"""
Health Check Endpoint

Provides service health status and dependent service availability checks.
"""

from fastapi import APIRouter, Depends
from datetime import datetime

from ...config.settings import Settings, get_settings
from ...services.storage import StorageService, get_storage_service
from ...models.query import HealthCheckResponse


router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health Check",
    description="Check service health and dependent service status",
)
async def health_check(
    settings: Settings = Depends(get_settings),
    storage: StorageService = Depends(lambda: get_storage_service(get_settings())),
) -> HealthCheckResponse:
    """
    Perform health check on the API and all dependent services.

    Returns:
        HealthCheckResponse with status for each service

    Status Codes:
        - healthy: All services operational
        - degraded: Some services failing but API functional
        - unhealthy: Critical services failing
    """
    # Check all dependent services
    services_health = await storage.check_all_services_health()

    # Determine overall status
    overall_status = determine_overall_status(services_health)

    # Get collection stats for additional info
    try:
        collection_stats = await storage.get_collection_stats()
        services_health["qdrant"]["points_count"] = collection_stats.get("points_count", 0)
    except Exception:
        pass

    return HealthCheckResponse(
        status=overall_status,
        version="1.0.0",
        services=services_health,
        timestamp=datetime.utcnow(),
    )


@router.get(
    "/health/ready",
    summary="Readiness Check",
    description="Check if service is ready to accept requests",
)
async def readiness_check(
    storage: StorageService = Depends(lambda: get_storage_service(get_settings())),
) -> dict:
    """
    Readiness check for Kubernetes/container orchestration.

    Returns 200 if service is ready, 503 otherwise.
    """
    # Check critical services
    services_health = await storage.check_all_services_health()

    # Service is ready if Qdrant and Postgres are healthy
    qdrant_healthy = services_health.get("qdrant", {}).get("status") == "healthy"
    postgres_healthy = services_health.get("postgres", {}).get("status") == "healthy"

    if qdrant_healthy and postgres_healthy:
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
        }
    else:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503,
            detail="Service not ready - dependent services unavailable",
        )


@router.get(
    "/health/live",
    summary="Liveness Check",
    description="Check if service is alive (basic ping)",
)
async def liveness_check() -> dict:
    """
    Liveness check for Kubernetes/container orchestration.

    Always returns 200 if the service is running.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }


def determine_overall_status(services_health: dict) -> str:
    """
    Determine overall health status based on dependent services.

    Args:
        services_health: Dictionary of service health statuses

    Returns:
        Overall status: "healthy", "degraded", or "unhealthy"
    """
    qdrant_status = services_health.get("qdrant", {}).get("status")
    postgres_status = services_health.get("postgres", {}).get("status")

    # Both critical services must be healthy
    if qdrant_status == "healthy" and postgres_status == "healthy":
        return "healthy"

    # If either critical service is unhealthy
    if qdrant_status == "unhealthy" or postgres_status == "unhealthy":
        return "unhealthy"

    # Partial degradation
    return "degraded"

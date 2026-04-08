"""
System monitoring and alerting service.

Provides:
1. Health checks for all connected services
2. Performance metrics (latency, throughput, error rates)
3. Alert rules with configurable thresholds
4. Alert history and notification dispatch
5. System dashboard data aggregation
"""

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class HealthCheck:
    """Health status of a single service."""

    name: str
    status: str  # "healthy", "degraded", "down"
    latency_ms: float
    last_check: str
    message: str = ""


@dataclass
class AlertRule:
    """A configurable alert rule."""

    id: str
    name: str
    metric: str
    condition: str  # "gt", "lt", "eq"
    threshold: float
    severity: str  # "info", "warning", "critical"
    enabled: bool = True
    cooldown_seconds: int = 300
    last_triggered: float = 0


@dataclass
class Alert:
    """A triggered alert."""

    rule_id: str
    rule_name: str
    severity: str
    metric: str
    value: float
    threshold: float
    message: str
    timestamp: str


@dataclass
class PerformanceMetric:
    """A performance metric sample."""

    name: str
    value: float
    unit: str
    timestamp: str


class MonitoringService:
    """
    System monitoring, health checking, and alerting.

    Tracks:
    - Service health (PM-US, PM-Intl, Kalshi, Falcon, DB, WS)
    - API latency p50/p95/p99
    - Error rates per endpoint
    - WebSocket connection status
    - Alert rule evaluation and history
    """

    def __init__(self) -> None:
        self._health_cache: dict[str, HealthCheck] = {}
        self._alert_rules: list[AlertRule] = self._default_rules()
        self._alert_history: deque[Alert] = deque(maxlen=500)
        self._latency_samples: deque[float] = deque(maxlen=1000)
        self._error_count = 0
        self._request_count = 0
        self._start_time = time.time()

    def _default_rules(self) -> list[AlertRule]:
        """Default alert rules."""
        return [
            AlertRule(
                id="api-latency-high",
                name="API Latency High",
                metric="api_latency_p95_ms",
                condition="gt",
                threshold=500,
                severity="warning",
            ),
            AlertRule(
                id="api-latency-critical",
                name="API Latency Critical",
                metric="api_latency_p99_ms",
                condition="gt",
                threshold=2000,
                severity="critical",
            ),
            AlertRule(
                id="error-rate-high",
                name="Error Rate High",
                metric="error_rate_pct",
                condition="gt",
                threshold=5.0,
                severity="warning",
            ),
            AlertRule(
                id="ws-disconnected",
                name="WebSocket Disconnected",
                metric="ws_connected",
                condition="eq",
                threshold=0,
                severity="critical",
            ),
            AlertRule(
                id="circuit-breaker",
                name="Circuit Breaker Triggered",
                metric="circuit_breaker_active",
                condition="eq",
                threshold=1,
                severity="critical",
            ),
            AlertRule(
                id="position-limit",
                name="Position Near Limit",
                metric="max_position_usage_pct",
                condition="gt",
                threshold=80,
                severity="warning",
            ),
        ]

    # ──────────────────────────────────────────
    # Health Checks
    # ──────────────────────────────────────────

    async def check_all_services(
        self,
        polymarket_client: Any = None,
        polymarket_intl: Any = None,
        kalshi_client: Any = None,
        falcon_client: Any = None,
        ws_manager: Any = None,
    ) -> list[HealthCheck]:
        """Run health checks on all services."""
        checks: list[HealthCheck] = []
        now = datetime.now(timezone.utc).isoformat()

        # Polymarket US
        try:
            start = time.monotonic()
            if polymarket_client:
                await polymarket_client.get_sports()
            latency = (time.monotonic() - start) * 1000
            checks.append(HealthCheck("Polymarket US", "healthy", round(latency, 1), now))
        except Exception as e:
            checks.append(HealthCheck("Polymarket US", "down", 0, now, str(e)))

        # Polymarket International
        try:
            start = time.monotonic()
            if polymarket_intl:
                await polymarket_intl.get_markets(limit=1)
            latency = (time.monotonic() - start) * 1000
            checks.append(HealthCheck("Polymarket Intl", "healthy", round(latency, 1), now))
        except Exception as e:
            checks.append(HealthCheck("Polymarket Intl", "down", 0, now, str(e)))

        # Kalshi
        try:
            start = time.monotonic()
            if kalshi_client:
                await kalshi_client.get_exchange_status()
            latency = (time.monotonic() - start) * 1000
            checks.append(HealthCheck("Kalshi", "healthy", round(latency, 1), now))
        except Exception as e:
            checks.append(HealthCheck("Kalshi", "down", 0, now, str(e)))

        # Falcon
        try:
            start = time.monotonic()
            if falcon_client and falcon_client._api_token:
                # Falcon requires subscription
                checks.append(HealthCheck("Falcon", "healthy", 0, now, "API token configured"))
            else:
                checks.append(HealthCheck("Falcon", "degraded", 0, now, "No API token — subscription inactive"))
        except Exception as e:
            checks.append(HealthCheck("Falcon", "down", 0, now, str(e)))

        # WebSocket
        if ws_manager:
            is_running = getattr(ws_manager, "_running", False)
            status = "healthy" if is_running else "down"
            checks.append(HealthCheck("WebSocket", status, 0, now))
        else:
            checks.append(HealthCheck("WebSocket", "down", 0, now, "Not initialised"))

        self._health_cache = {c.name: c for c in checks}
        return checks

    # ──────────────────────────────────────────
    # Metrics
    # ──────────────────────────────────────────

    def record_request(self, latency_ms: float, is_error: bool = False) -> None:
        """Record a request for metrics tracking."""
        self._request_count += 1
        self._latency_samples.append(latency_ms)
        if is_error:
            self._error_count += 1

    def get_metrics(self) -> dict[str, Any]:
        """Get current performance metrics."""
        uptime = time.time() - self._start_time
        samples = sorted(self._latency_samples) if self._latency_samples else [0]

        p50 = samples[len(samples) // 2]
        p95 = samples[int(len(samples) * 0.95)] if len(samples) > 1 else samples[0]
        p99 = samples[int(len(samples) * 0.99)] if len(samples) > 1 else samples[0]

        error_rate = (self._error_count / max(self._request_count, 1)) * 100

        return {
            "uptime_seconds": round(uptime, 0),
            "total_requests": self._request_count,
            "total_errors": self._error_count,
            "error_rate_pct": round(error_rate, 2),
            "latency": {
                "p50_ms": round(p50, 1),
                "p95_ms": round(p95, 1),
                "p99_ms": round(p99, 1),
                "avg_ms": round(sum(samples) / len(samples), 1),
            },
            "services": {
                name: {
                    "status": check.status,
                    "latency_ms": check.latency_ms,
                }
                for name, check in self._health_cache.items()
            },
        }

    # ──────────────────────────────────────────
    # Alerting
    # ──────────────────────────────────────────

    def evaluate_alerts(self, metrics: dict[str, float]) -> list[Alert]:
        """Evaluate all alert rules against current metrics."""
        triggered: list[Alert] = []
        now = time.time()

        for rule in self._alert_rules:
            if not rule.enabled:
                continue
            if now - rule.last_triggered < rule.cooldown_seconds:
                continue

            value = metrics.get(rule.metric)
            if value is None:
                continue

            fired = False
            if rule.condition == "gt" and value > rule.threshold:
                fired = True
            elif rule.condition == "lt" and value < rule.threshold:
                fired = True
            elif rule.condition == "eq" and value == rule.threshold:
                fired = True

            if fired:
                alert = Alert(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    metric=rule.metric,
                    value=value,
                    threshold=rule.threshold,
                    message=f"{rule.name}: {rule.metric} = {value} ({rule.condition} {rule.threshold})",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
                self._alert_history.append(alert)
                triggered.append(alert)
                rule.last_triggered = now
                logger.warning("Alert fired: %s — %s", alert.rule_name, alert.message)

        return triggered

    def get_alert_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get recent alert history."""
        alerts = list(self._alert_history)[-limit:]
        return [
            {
                "rule_id": a.rule_id,
                "rule_name": a.rule_name,
                "severity": a.severity,
                "metric": a.metric,
                "value": a.value,
                "threshold": a.threshold,
                "message": a.message,
                "timestamp": a.timestamp,
            }
            for a in reversed(alerts)
        ]

    def get_alert_rules(self) -> list[dict[str, Any]]:
        """Get all configured alert rules."""
        return [
            {
                "id": r.id,
                "name": r.name,
                "metric": r.metric,
                "condition": r.condition,
                "threshold": r.threshold,
                "severity": r.severity,
                "enabled": r.enabled,
                "cooldown_seconds": r.cooldown_seconds,
            }
            for r in self._alert_rules
        ]

    def toggle_alert_rule(self, rule_id: str, enabled: bool) -> bool:
        """Enable or disable an alert rule."""
        for rule in self._alert_rules:
            if rule.id == rule_id:
                rule.enabled = enabled
                logger.info("Alert rule %s %s", rule_id, "enabled" if enabled else "disabled")
                return True
        return False

    def get_system_summary(self) -> dict[str, Any]:
        """Full system summary for the monitoring dashboard."""
        metrics = self.get_metrics()
        healthy = sum(1 for c in self._health_cache.values() if c.status == "healthy")
        total = len(self._health_cache)
        recent_alerts = len([a for a in self._alert_history if True])  # all in deque are recent

        return {
            "overall_status": "healthy" if healthy == total else "degraded" if healthy > 0 else "down",
            "services_healthy": healthy,
            "services_total": total,
            "recent_alerts": min(recent_alerts, 50),
            "metrics": metrics,
            "health_checks": [
                {
                    "name": c.name,
                    "status": c.status,
                    "latency_ms": c.latency_ms,
                    "message": c.message,
                }
                for c in self._health_cache.values()
            ],
        }

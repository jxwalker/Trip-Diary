"""
Production Monitoring & Health Checks
Advanced monitoring system for production environments
"""
import asyncio
import time
import psutil
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

from ..config import get_settings
from ..services.service_factory import service_factory

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class MetricType(str, Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class HealthCheck:
    """Health check definition"""
    name: str
    check_function: Callable[[], Awaitable[Dict[str, Any]]]
    interval_seconds: int = 60
    timeout_seconds: int = 30
    critical: bool = False
    enabled: bool = True
    last_check: Optional[datetime] = None
    last_result: Optional[Dict[str, Any]] = None
    consecutive_failures: int = 0


@dataclass
class Metric:
    """Metric data point"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "type": self.metric_type.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags
        }


@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_free_gb: float
    load_average: List[float]
    uptime_seconds: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_used_mb": self.memory_used_mb,
            "memory_available_mb": self.memory_available_mb,
            "disk_percent": self.disk_percent,
            "disk_used_gb": self.disk_used_gb,
            "disk_free_gb": self.disk_free_gb,
            "load_average": self.load_average,
            "uptime_seconds": self.uptime_seconds,
            "timestamp": self.timestamp.isoformat()
        }


class MonitoringService:
    """Production monitoring service"""
    
    def __init__(self):
        self.settings = get_settings()
        self.health_checks: Dict[str, HealthCheck] = {}
        self.metrics: List[Metric] = []
        self.system_metrics_history: List[SystemMetrics] = []
        self.alerts: List[Dict[str, Any]] = []
        self._monitoring_task: Optional[asyncio.Task] = None
        self._start_time = time.time()
        
        # Initialize default health checks
        self._register_default_health_checks()
    
    async def start_monitoring(self) -> None:
        """Start the monitoring service"""
        if self._monitoring_task and not self._monitoring_task.done():
            logger.warning("Monitoring already running")
            return
        
        logger.info("Starting monitoring service")
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self) -> None:
        """Stop the monitoring service"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Monitoring service stopped")
    
    def register_health_check(self, health_check: HealthCheck) -> None:
        """Register a health check"""
        self.health_checks[health_check.name] = health_check
        logger.info(f"Registered health check: {health_check.name}")
    
    def record_metric(self, metric: Metric) -> None:
        """Record a metric"""
        self.metrics.append(metric)
        
        # Keep only recent metrics (last hour)
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        try:
            # Run all health checks
            health_results = {}
            overall_status = HealthStatus.HEALTHY
            critical_failures = 0
            total_checks = 0
            
            for name, check in self.health_checks.items():
                if not check.enabled:
                    continue
                
                total_checks += 1
                
                try:
                    # Run health check with timeout
                    result = await asyncio.wait_for(
                        check.check_function(),
                        timeout=check.timeout_seconds
                    )
                    
                    check.last_check = datetime.now()
                    check.last_result = result
                    check.consecutive_failures = 0
                    
                    health_results[name] = {
                        **result,
                        "last_check": check.last_check.isoformat(),
                        "critical": check.critical
                    }
                    
                    # Update overall status
                    check_status = result.get("status", "unknown")
                    if check_status == "unhealthy":
                        if check.critical:
                            overall_status = HealthStatus.CRITICAL
                            critical_failures += 1
                        elif overall_status == HealthStatus.HEALTHY:
                            overall_status = HealthStatus.WARNING
                    
                except asyncio.TimeoutError:
                    check.consecutive_failures += 1
                    error_result = {
                        "status": "unhealthy",
                        "error": "Health check timeout",
                        "consecutive_failures": check.consecutive_failures
                    }
                    
                    health_results[name] = error_result
                    
                    if check.critical:
                        overall_status = HealthStatus.CRITICAL
                        critical_failures += 1
                    elif overall_status == HealthStatus.HEALTHY:
                        overall_status = HealthStatus.WARNING
                
                except Exception as e:
                    check.consecutive_failures += 1
                    error_result = {
                        "status": "unhealthy",
                        "error": str(e),
                        "consecutive_failures": check.consecutive_failures
                    }
                    
                    health_results[name] = error_result
                    
                    if check.critical:
                        overall_status = HealthStatus.CRITICAL
                        critical_failures += 1
                    elif overall_status == HealthStatus.HEALTHY:
                        overall_status = HealthStatus.WARNING
            
            return {
                "status": overall_status.value,
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": time.time() - self._start_time,
                "checks": health_results,
                "summary": {
                    "total_checks": total_checks,
                    "critical_failures": critical_failures,
                    "healthy_checks": sum(1 for r in health_results.values() if r.get("status") == "healthy")
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get health status: {e}")
            return {
                "status": HealthStatus.CRITICAL.value,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_used_mb = (memory.total - memory.available) / (1024 * 1024)
            memory_available_mb = memory.available / (1024 * 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_used_gb = disk.used / (1024 * 1024 * 1024)
            disk_free_gb = disk.free / (1024 * 1024 * 1024)
            disk_percent = (disk.used / disk.total) * 100
            
            # Load average
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0.0, 0.0, 0.0]
            
            # Uptime
            uptime_seconds = time.time() - self._start_time
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory_used_mb,
                memory_available_mb=memory_available_mb,
                disk_percent=disk_percent,
                disk_used_gb=disk_used_gb,
                disk_free_gb=disk_free_gb,
                load_average=list(load_avg),
                uptime_seconds=uptime_seconds
            )
            
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                memory_available_mb=0.0,
                disk_percent=0.0,
                disk_used_gb=0.0,
                disk_free_gb=0.0,
                load_average=[0.0, 0.0, 0.0],
                uptime_seconds=0.0
            )
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        try:
            if not self.metrics:
                return {"message": "No metrics available"}
            
            # Group metrics by name
            metrics_by_name = {}
            for metric in self.metrics:
                if metric.name not in metrics_by_name:
                    metrics_by_name[metric.name] = []
                metrics_by_name[metric.name].append(metric)
            
            # Calculate summaries
            summaries = {}
            for name, metric_list in metrics_by_name.items():
                values = [m.value for m in metric_list]
                summaries[name] = {
                    "count": len(values),
                    "latest": values[-1] if values else 0,
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0,
                    "avg": sum(values) / len(values) if values else 0,
                    "type": metric_list[0].metric_type.value if metric_list else "unknown"
                }
            
            return {
                "total_metrics": len(self.metrics),
                "metric_summaries": summaries,
                "time_range": {
                    "start": min(m.timestamp for m in self.metrics).isoformat() if self.metrics else None,
                    "end": max(m.timestamp for m in self.metrics).isoformat() if self.metrics else None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {"error": str(e)}
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        logger.info("Monitoring loop started")
        
        try:
            while True:
                # Collect system metrics
                system_metrics = await self.get_system_metrics()
                self.system_metrics_history.append(system_metrics)
                
                # Keep only recent system metrics (last 24 hours)
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.system_metrics_history = [
                    m for m in self.system_metrics_history 
                    if m.timestamp > cutoff_time
                ]
                
                # Record system metrics as metrics
                self.record_metric(Metric("system.cpu_percent", system_metrics.cpu_percent, MetricType.GAUGE))
                self.record_metric(Metric("system.memory_percent", system_metrics.memory_percent, MetricType.GAUGE))
                self.record_metric(Metric("system.disk_percent", system_metrics.disk_percent, MetricType.GAUGE))
                
                # Check for alerts
                await self._check_alerts(system_metrics)
                
                # Wait before next iteration
                await asyncio.sleep(60)  # Check every minute
                
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Monitoring loop error: {e}")
            # Continue monitoring even if there's an error
            await asyncio.sleep(60)
    
    async def _check_alerts(self, system_metrics: SystemMetrics) -> None:
        """Check for alert conditions"""
        try:
            alerts = []
            
            # CPU alert
            if system_metrics.cpu_percent > 90:
                alerts.append({
                    "type": "high_cpu",
                    "severity": "critical",
                    "message": f"High CPU usage: {system_metrics.cpu_percent:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
            elif system_metrics.cpu_percent > 80:
                alerts.append({
                    "type": "high_cpu",
                    "severity": "warning",
                    "message": f"Elevated CPU usage: {system_metrics.cpu_percent:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Memory alert
            if system_metrics.memory_percent > 90:
                alerts.append({
                    "type": "high_memory",
                    "severity": "critical",
                    "message": f"High memory usage: {system_metrics.memory_percent:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
            elif system_metrics.memory_percent > 80:
                alerts.append({
                    "type": "high_memory",
                    "severity": "warning",
                    "message": f"Elevated memory usage: {system_metrics.memory_percent:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Disk alert
            if system_metrics.disk_percent > 95:
                alerts.append({
                    "type": "high_disk",
                    "severity": "critical",
                    "message": f"High disk usage: {system_metrics.disk_percent:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
            elif system_metrics.disk_percent > 85:
                alerts.append({
                    "type": "high_disk",
                    "severity": "warning",
                    "message": f"Elevated disk usage: {system_metrics.disk_percent:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Add new alerts
            for alert in alerts:
                self.alerts.append(alert)
                logger.warning(f"Alert: {alert['message']}")
            
            # Keep only recent alerts (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.alerts = [
                a for a in self.alerts 
                if datetime.fromisoformat(a["timestamp"]) > cutoff_time
            ]
            
        except Exception as e:
            logger.error(f"Failed to check alerts: {e}")
    
    def _register_default_health_checks(self) -> None:
        """Register default health checks"""
        # Service factory health check
        self.register_health_check(HealthCheck(
            name="service_factory",
            check_function=self._check_service_factory_health,
            interval_seconds=60,
            critical=True
        ))
        
        # Database health check
        self.register_health_check(HealthCheck(
            name="database",
            check_function=self._check_database_health,
            interval_seconds=30,
            critical=True
        ))
        
        # System resources health check
        self.register_health_check(HealthCheck(
            name="system_resources",
            check_function=self._check_system_resources_health,
            interval_seconds=60,
            critical=False
        ))
    
    async def _check_service_factory_health(self) -> Dict[str, Any]:
        """Check service factory health"""
        try:
            if not service_factory._initialized:
                return {"status": "unhealthy", "error": "Service factory not initialized"}
            
            health_status = await service_factory.health_check_all()
            
            unhealthy_services = [
                name for name, status in health_status.items()
                if status.get("status") != "healthy"
            ]
            
            if unhealthy_services:
                return {
                    "status": "warning",
                    "message": f"Some services unhealthy: {', '.join(unhealthy_services)}",
                    "unhealthy_services": unhealthy_services,
                    "total_services": len(health_status)
                }
            
            return {
                "status": "healthy",
                "message": "All services healthy",
                "total_services": len(health_status)
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            storage_service = service_factory.get_storage_service()
            if not storage_service:
                return {"status": "unhealthy", "error": "Storage service not available"}
            
            health = await storage_service.health_check()
            return health
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def _check_system_resources_health(self) -> Dict[str, Any]:
        """Check system resources health"""
        try:
            metrics = await self.get_system_metrics()
            
            issues = []
            if metrics.cpu_percent > 90:
                issues.append(f"High CPU: {metrics.cpu_percent:.1f}%")
            if metrics.memory_percent > 90:
                issues.append(f"High memory: {metrics.memory_percent:.1f}%")
            if metrics.disk_percent > 95:
                issues.append(f"High disk: {metrics.disk_percent:.1f}%")
            
            if issues:
                return {
                    "status": "warning",
                    "message": f"Resource issues: {', '.join(issues)}",
                    "metrics": metrics.to_dict()
                }
            
            return {
                "status": "healthy",
                "message": "System resources normal",
                "metrics": metrics.to_dict()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Global monitoring service instance
monitoring_service = MonitoringService()

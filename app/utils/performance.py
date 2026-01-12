# -*- coding: utf-8 -*-
"""
Performance Monitoring Module
Tracks and reports performance metrics
Supports MASTER_PLAN extensibility and monitoring requirements
"""

import time
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Monitor and track application performance metrics
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize performance monitor
        
        Args:
            max_history: Maximum number of metric entries to keep
        """
        self.max_history = max_history
        self.metrics = defaultdict(deque)
        self.timers = {}
        self.counters = defaultdict(int)
        self.gauges = {}
        
    def start_timer(self, name: str) -> float:
        """
        Start a timer for measuring operation duration
        
        Args:
            name: Timer name
            
        Returns:
            Start timestamp
        """
        start_time = time.time()
        self.timers[name] = start_time
        return start_time
    
    def stop_timer(self, name: str) -> Optional[float]:
        """
        Stop a timer and record duration
        
        Args:
            name: Timer name
            
        Returns:
            Duration in seconds or None if timer wasn't started
        """
        if name not in self.timers:
            logger.warning(f"Timer '{name}' was not started")
            return None
        
        start_time = self.timers.pop(name)
        duration = time.time() - start_time
        
        # Record metric
        self._add_metric(name, duration)
        
        return duration
    
    def record_metric(self, name: str, value: float, metadata: Optional[Dict] = None):
        """
        Record a custom metric value
        
        Args:
            name: Metric name
            value: Metric value
            metadata: Optional metadata dictionary
        """
        metric_entry = {
            'timestamp': datetime.now().isoformat(),
            'value': value,
            'metadata': metadata or {}
        }
        
        self.metrics[name].append(metric_entry)
        
        # Trim history if needed
        if len(self.metrics[name]) > self.max_history:
            self.metrics[name].popleft()
    
    def _add_metric(self, name: str, value: float, metadata: Optional[Dict] = None):
        """Internal method to add metric"""
        self.record_metric(name, value, metadata)
    
    def increment_counter(self, name: str, amount: int = 1):
        """
        Increment a counter
        
        Args:
            name: Counter name
            amount: Amount to increment by
        """
        self.counters[name] += amount
    
    def decrement_counter(self, name: str, amount: int = 1):
        """
        Decrement a counter
        
        Args:
            name: Counter name
            amount: Amount to decrement by
        """
        self.counters[name] -= amount
    
    def set_gauge(self, name: str, value: float):
        """
        Set a gauge value (current state measurement)
        
        Args:
            name: Gauge name
            value: Current value
        """
        self.gauges[name] = {
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_metric_stats(self, name: str, window_seconds: Optional[int] = None) -> Dict[str, Any]:
        """
        Get statistics for a metric
        
        Args:
            name: Metric name
            window_seconds: Optional time window (only include recent metrics)
            
        Returns:
            Dictionary with statistics (min, max, avg, count, etc.)
        """
        if name not in self.metrics or not self.metrics[name]:
            return {
                'count': 0,
                'min': None,
                'max': None,
                'avg': None,
                'sum': None
            }
        
        # Filter by time window if specified
        metrics = list(self.metrics[name])
        if window_seconds:
            cutoff_time = datetime.now() - timedelta(seconds=window_seconds)
            metrics = [
                m for m in metrics
                if datetime.fromisoformat(m['timestamp']) >= cutoff_time
            ]
        
        if not metrics:
            return {
                'count': 0,
                'min': None,
                'max': None,
                'avg': None,
                'sum': None
            }
        
        values = [m['value'] for m in metrics]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'sum': sum(values),
            'latest': values[-1] if values else None
        }
    
    def get_counter_value(self, name: str) -> int:
        """
        Get current counter value
        
        Args:
            name: Counter name
            
        Returns:
            Current value
        """
        return self.counters.get(name, 0)
    
    def get_gauge_value(self, name: str) -> Optional[float]:
        """
        Get current gauge value
        
        Args:
            name: Gauge name
            
        Returns:
            Current value or None
        """
        gauge = self.gauges.get(name)
        return gauge['value'] if gauge else None
    
    def get_all_stats(self) -> Dict[str, Any]:
        """
        Get all performance statistics
        
        Returns:
            Dictionary with all metrics, counters, and gauges
        """
        stats = {
            'metrics': {},
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'timestamp': datetime.now().isoformat()
        }
        
        # Get stats for all metrics
        for name in self.metrics.keys():
            stats['metrics'][name] = self.get_metric_stats(name)
        
        return stats
    
    def reset(self):
        """Reset all metrics, counters, and gauges"""
        self.metrics.clear()
        self.timers.clear()
        self.counters.clear()
        self.gauges.clear()
        logger.info("Performance monitor reset")
    
    def reset_metric(self, name: str):
        """Reset specific metric"""
        if name in self.metrics:
            self.metrics[name].clear()
    
    def reset_counter(self, name: str):
        """Reset specific counter"""
        if name in self.counters:
            self.counters[name] = 0
    
    def export_metrics(self, format: str = 'json') -> str:
        """
        Export metrics in specified format
        
        Args:
            format: Export format ('json' or 'csv')
            
        Returns:
            Formatted string
        """
        stats = self.get_all_stats()
        
        if format == 'json':
            import json
            return json.dumps(stats, indent=2, ensure_ascii=False)
        
        elif format == 'csv':
            # Simple CSV format for metrics
            lines = ['metric_name,count,min,max,avg,sum']
            for name, metric_stats in stats['metrics'].items():
                lines.append(
                    f"{name},{metric_stats['count']},{metric_stats['min']},"
                    f"{metric_stats['max']},{metric_stats['avg']},{metric_stats['sum']}"
                )
            return '\n'.join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def log_stats(self, metric_names: Optional[List[str]] = None):
        """
        Log statistics to logger
        
        Args:
            metric_names: Optional list of specific metrics to log (all if None)
        """
        if metric_names is None:
            metric_names = list(self.metrics.keys())
        
        logger.info("=== Performance Statistics ===")
        
        for name in metric_names:
            stats = self.get_metric_stats(name)
            if stats['count'] > 0:
                logger.info(
                    f"{name}: count={stats['count']}, "
                    f"avg={stats['avg']:.3f}s, "
                    f"min={stats['min']:.3f}s, "
                    f"max={stats['max']:.3f}s"
                )
        
        if self.counters:
            logger.info("--- Counters ---")
            for name, value in self.counters.items():
                logger.info(f"{name}: {value}")
        
        if self.gauges:
            logger.info("--- Gauges ---")
            for name, gauge in self.gauges.items():
                logger.info(f"{name}: {gauge['value']}")


class TransferPerformanceTracker:
    """
    Specialized tracker for transfer operations
    Integrates with PerformanceMonitor for transfer-specific metrics
    """
    
    def __init__(self, monitor: Optional[PerformanceMonitor] = None):
        """
        Initialize transfer tracker
        
        Args:
            monitor: PerformanceMonitor instance (creates new if None)
        """
        self.monitor = monitor or PerformanceMonitor()
        self.transfer_start_time = None
        self.message_times = deque(maxlen=100)  # Keep last 100 message times
    
    def start_transfer(self):
        """Mark start of transfer"""
        self.transfer_start_time = time.time()
        self.monitor.start_timer('total_transfer_time')
        self.monitor.set_gauge('transfer_active', 1)
    
    def end_transfer(self):
        """Mark end of transfer"""
        if self.transfer_start_time:
            self.monitor.stop_timer('total_transfer_time')
            self.transfer_start_time = None
        self.monitor.set_gauge('transfer_active', 0)
    
    def record_message_transferred(self, message_id: int, size_bytes: Optional[int] = None):
        """
        Record a successful message transfer
        
        Args:
            message_id: Message ID
            size_bytes: Optional message size in bytes
        """
        current_time = time.time()
        self.message_times.append(current_time)
        
        self.monitor.increment_counter('messages_transferred')
        
        if size_bytes:
            self.monitor.increment_counter('bytes_transferred', size_bytes)
            self.monitor.record_metric('message_size', size_bytes)
    
    def record_message_skipped(self, reason: str):
        """
        Record a skipped message
        
        Args:
            reason: Reason for skipping
        """
        self.monitor.increment_counter('messages_skipped')
        self.monitor.increment_counter(f'skip_reason_{reason}')
    
    def record_error(self, error_type: str):
        """
        Record an error
        
        Args:
            error_type: Type of error
        """
        self.monitor.increment_counter('errors_total')
        self.monitor.increment_counter(f'error_{error_type}')
    
    def get_current_speed(self) -> float:
        """
        Calculate current transfer speed (messages per second)
        
        Returns:
            Messages per second
        """
        if len(self.message_times) < 2:
            return 0.0
        
        time_span = self.message_times[-1] - self.message_times[0]
        if time_span <= 0:
            return 0.0
        
        return len(self.message_times) / time_span
    
    def get_eta(self, total_messages: int) -> Optional[float]:
        """
        Estimate time to completion
        
        Args:
            total_messages: Total number of messages to transfer
            
        Returns:
            Estimated seconds remaining or None
        """
        transferred = self.monitor.get_counter_value('messages_transferred')
        remaining = total_messages - transferred
        
        if remaining <= 0:
            return 0.0
        
        speed = self.get_current_speed()
        if speed <= 0:
            return None
        
        return remaining / speed
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get transfer statistics
        
        Returns:
            Dictionary with transfer stats
        """
        return {
            'messages_transferred': self.monitor.get_counter_value('messages_transferred'),
            'messages_skipped': self.monitor.get_counter_value('messages_skipped'),
            'errors_total': self.monitor.get_counter_value('errors_total'),
            'bytes_transferred': self.monitor.get_counter_value('bytes_transferred'),
            'current_speed_msg_per_sec': self.get_current_speed(),
            'transfer_active': bool(self.monitor.get_gauge_value('transfer_active')),
            'elapsed_time': time.time() - self.transfer_start_time if self.transfer_start_time else 0
        }


# Global instances
_default_monitor = None
_default_transfer_tracker = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _default_monitor
    if _default_monitor is None:
        _default_monitor = PerformanceMonitor()
    return _default_monitor


def get_transfer_tracker() -> TransferPerformanceTracker:
    """Get global transfer tracker instance"""
    global _default_transfer_tracker
    if _default_transfer_tracker is None:
        _default_transfer_tracker = TransferPerformanceTracker(get_performance_monitor())
    return _default_transfer_tracker

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for performance monitoring functionality
Tests performance tracking features
"""

import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly from module to avoid kivy dependencies
from app.utils.performance import PerformanceMonitor, TransferPerformanceTracker


def test_performance_monitor_timers():
    """Test timer functionality"""
    print("Testing PerformanceMonitor timers...")
    
    monitor = PerformanceMonitor()
    
    # Test timer
    monitor.start_timer('test_operation')
    time.sleep(0.1)  # Simulate operation
    duration = monitor.stop_timer('test_operation')
    
    assert duration is not None, "Timer should return duration"
    assert duration >= 0.1, "Duration should be at least 0.1 seconds"
    assert duration < 0.2, "Duration should be less than 0.2 seconds (sanity check)"
    
    # Test stats
    stats = monitor.get_metric_stats('test_operation')
    assert stats['count'] == 1, "Should have 1 measurement"
    assert stats['avg'] >= 0.1, "Average should be at least 0.1"
    
    print("✓ Timer tests passed")


def test_performance_monitor_counters():
    """Test counter functionality"""
    print("Testing PerformanceMonitor counters...")
    
    monitor = PerformanceMonitor()
    
    # Test increment
    monitor.increment_counter('messages', 5)
    assert monitor.get_counter_value('messages') == 5, "Counter should be 5"
    
    monitor.increment_counter('messages', 3)
    assert monitor.get_counter_value('messages') == 8, "Counter should be 8"
    
    # Test decrement
    monitor.decrement_counter('messages', 2)
    assert monitor.get_counter_value('messages') == 6, "Counter should be 6"
    
    # Test reset
    monitor.reset_counter('messages')
    assert monitor.get_counter_value('messages') == 0, "Counter should be reset to 0"
    
    print("✓ Counter tests passed")


def test_performance_monitor_gauges():
    """Test gauge functionality"""
    print("Testing PerformanceMonitor gauges...")
    
    monitor = PerformanceMonitor()
    
    # Set gauge
    monitor.set_gauge('cpu_usage', 45.5)
    assert monitor.get_gauge_value('cpu_usage') == 45.5, "Gauge should be 45.5"
    
    # Update gauge
    monitor.set_gauge('cpu_usage', 60.0)
    assert monitor.get_gauge_value('cpu_usage') == 60.0, "Gauge should be updated to 60.0"
    
    # Non-existent gauge
    assert monitor.get_gauge_value('nonexistent') is None, "Non-existent gauge should return None"
    
    print("✓ Gauge tests passed")


def test_performance_monitor_metrics():
    """Test metric recording and statistics"""
    print("Testing PerformanceMonitor metrics...")
    
    monitor = PerformanceMonitor()
    
    # Record multiple metrics
    for i in range(10):
        monitor.record_metric('response_time', i * 0.1)
    
    stats = monitor.get_metric_stats('response_time')
    
    assert stats['count'] == 10, "Should have 10 measurements"
    assert stats['min'] == 0.0, "Min should be 0.0"
    assert stats['max'] == 0.9, "Max should be 0.9"
    assert abs(stats['avg'] - 0.45) < 0.01, "Average should be approximately 0.45"
    assert abs(stats['sum'] - 4.5) < 0.01, "Sum should be approximately 4.5"
    
    print("✓ Metric tests passed")


def test_performance_monitor_export():
    """Test metric export functionality"""
    print("Testing PerformanceMonitor export...")
    
    monitor = PerformanceMonitor()
    
    # Add some data
    monitor.increment_counter('test_counter', 42)
    monitor.set_gauge('test_gauge', 3.14)
    monitor.record_metric('test_metric', 1.5)
    
    # Export as JSON
    json_export = monitor.export_metrics('json')
    assert 'test_counter' in json_export, "JSON should contain counter"
    assert 'test_gauge' in json_export, "JSON should contain gauge"
    assert 'test_metric' in json_export, "JSON should contain metric"
    
    # Export as CSV
    csv_export = monitor.export_metrics('csv')
    assert 'test_metric' in csv_export, "CSV should contain metric"
    assert 'count,min,max,avg,sum' in csv_export, "CSV should have header"
    
    print("✓ Export tests passed")


def test_transfer_performance_tracker():
    """Test TransferPerformanceTracker functionality"""
    print("Testing TransferPerformanceTracker...")
    
    tracker = TransferPerformanceTracker()
    
    # Start transfer
    tracker.start_transfer()
    assert tracker.monitor.get_gauge_value('transfer_active') == 1, "Transfer should be active"
    
    # Record some messages
    for i in range(5):
        tracker.record_message_transferred(i, 1024)
        time.sleep(0.01)  # Small delay
    
    # Check counters
    assert tracker.monitor.get_counter_value('messages_transferred') == 5, "Should have 5 messages"
    assert tracker.monitor.get_counter_value('bytes_transferred') == 5120, "Should have 5120 bytes"
    
    # Check speed calculation
    speed = tracker.get_current_speed()
    assert speed > 0, "Speed should be positive"
    
    # Record skipped message
    tracker.record_message_skipped('deleted')
    assert tracker.monitor.get_counter_value('messages_skipped') == 1, "Should have 1 skipped"
    
    # Record error
    tracker.record_error('network')
    assert tracker.monitor.get_counter_value('errors_total') == 1, "Should have 1 error"
    
    # Get stats
    stats = tracker.get_stats()
    assert stats['messages_transferred'] == 5, "Stats should show 5 messages"
    assert stats['messages_skipped'] == 1, "Stats should show 1 skipped"
    assert stats['errors_total'] == 1, "Stats should show 1 error"
    assert stats['transfer_active'] is True, "Transfer should be active"
    
    # End transfer
    tracker.end_transfer()
    assert tracker.monitor.get_gauge_value('transfer_active') == 0, "Transfer should be inactive"
    
    print("✓ TransferPerformanceTracker tests passed")


def test_transfer_eta_calculation():
    """Test ETA calculation"""
    print("Testing ETA calculation...")
    
    tracker = TransferPerformanceTracker()
    tracker.start_transfer()
    
    # Record some messages with timing
    for i in range(10):
        tracker.record_message_transferred(i)
        time.sleep(0.01)
    
    # Calculate ETA for 100 total messages
    eta = tracker.get_eta(100)
    assert eta is not None, "ETA should be calculable"
    assert eta > 0, "ETA should be positive"
    assert eta < 10, "ETA should be reasonable (sanity check)"
    
    # ETA should be 0 when all messages are transferred
    for i in range(10, 100):
        tracker.record_message_transferred(i)
    
    eta = tracker.get_eta(100)
    assert eta == 0.0, "ETA should be 0 when complete"
    
    print("✓ ETA calculation tests passed")


def test_performance_monitor_reset():
    """Test reset functionality"""
    print("Testing reset functionality...")
    
    monitor = PerformanceMonitor()
    
    # Add data
    monitor.increment_counter('test', 10)
    monitor.set_gauge('test_gauge', 5.0)
    monitor.record_metric('test_metric', 1.0)
    
    # Reset all
    monitor.reset()
    
    assert monitor.get_counter_value('test') == 0, "Counter should be reset"
    assert monitor.get_gauge_value('test_gauge') is None, "Gauge should be reset"
    assert len(monitor.metrics) == 0, "Metrics should be reset"
    
    print("✓ Reset tests passed")


def test_metric_history_limit():
    """Test that metric history is limited"""
    print("Testing metric history limit...")
    
    monitor = PerformanceMonitor(max_history=10)
    
    # Record more than max_history metrics
    for i in range(20):
        monitor.record_metric('test', i)
    
    # Should only keep last 10
    assert len(monitor.metrics['test']) == 10, "Should keep only 10 metrics"
    
    # Should have metrics 10-19 (last 10)
    stats = monitor.get_metric_stats('test')
    assert stats['count'] == 10, "Should have 10 metrics"
    assert stats['min'] == 10, "Min should be 10 (first of last 10)"
    assert stats['max'] == 19, "Max should be 19 (last metric)"
    
    print("✓ History limit tests passed")


if __name__ == '__main__':
    print("Running performance monitoring tests...\n")
    
    try:
        test_performance_monitor_timers()
        test_performance_monitor_counters()
        test_performance_monitor_gauges()
        test_performance_monitor_metrics()
        test_performance_monitor_export()
        test_transfer_performance_tracker()
        test_transfer_eta_calculation()
        test_performance_monitor_reset()
        test_metric_history_limit()
        
        print("\n✅ All performance monitoring tests passed!")
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

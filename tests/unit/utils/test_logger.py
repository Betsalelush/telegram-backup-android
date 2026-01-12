# -*- coding: utf-8 -*-
"""
Unit tests for logger utilities
"""
import pytest
from unittest.mock import patch, MagicMock
import sentry_sdk
from app.utils.logger import (
    add_breadcrumb,
    set_user_context,
    set_transfer_context,
    capture_exception
)


class TestLogger:
    """Test logger utility functions"""
    
    @patch('sentry_sdk.add_breadcrumb')
    def test_add_breadcrumb(self, mock_add_breadcrumb):
        """Test adding breadcrumb to Sentry"""
        add_breadcrumb('test_category', 'test message', 'info', {'key': 'value'})
        
        mock_add_breadcrumb.assert_called_once_with(
            category='test_category',
            message='test message',
            level='info',
            data={'key': 'value'}
        )
    
    @patch('sentry_sdk.add_breadcrumb')
    def test_add_breadcrumb_no_data(self, mock_add_breadcrumb):
        """Test adding breadcrumb without data"""
        add_breadcrumb('test_category', 'test message')
        
        mock_add_breadcrumb.assert_called_once_with(
            category='test_category',
            message='test message',
            level='info',
            data={}
        )
    
    @patch('sentry_sdk.set_user')
    def test_set_user_context(self, mock_set_user):
        """Test setting user context in Sentry"""
        set_user_context(account_id='123', phone='+972123456789')
        
        mock_set_user.assert_called_once_with({
            'id': '123',
            'phone': '+972123456789'
        })
    
    @patch('sentry_sdk.set_tag')
    def test_set_transfer_context(self, mock_set_tag):
        """Test setting transfer context in Sentry"""
        set_transfer_context(
            transfer_id='transfer_123',
            source_channel='source_id',
            target_channel='target_id'
        )
        
        assert mock_set_tag.call_count == 3
        mock_set_tag.assert_any_call('transfer_id', 'transfer_123')
        mock_set_tag.assert_any_call('source_channel', 'source_id')
        mock_set_tag.assert_any_call('target_channel', 'target_id')
    
    @patch('sentry_sdk.set_tag')
    def test_set_transfer_context_minimal(self, mock_set_tag):
        """Test setting transfer context with minimal data"""
        set_transfer_context(transfer_id='transfer_123')
        
        assert mock_set_tag.call_count == 1
        mock_set_tag.assert_called_once_with('transfer_id', 'transfer_123')
    
    @patch('sentry_sdk.capture_exception')
    @patch('sentry_sdk.set_context')
    def test_capture_exception(self, mock_set_context, mock_capture_exception):
        """Test capturing exception in Sentry"""
        exception = ValueError('Test error')
        extra_data = {'key': 'value'}
        
        capture_exception(exception, extra_data)
        
        mock_set_context.assert_called_once_with('extra', extra_data)
        mock_capture_exception.assert_called_once_with(exception)
    
    @patch('sentry_sdk.capture_exception')
    @patch('sentry_sdk.set_context')
    def test_capture_exception_no_extra(self, mock_set_context, mock_capture_exception):
        """Test capturing exception without extra data"""
        exception = ValueError('Test error')
        
        capture_exception(exception)
        
        mock_set_context.assert_not_called()
        mock_capture_exception.assert_called_once_with(exception)

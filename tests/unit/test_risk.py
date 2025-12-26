"""
Unit tests for risk management.

Tests risk checks, position limits, and validation logic.
"""
import pytest
from src.risk.manager import RiskManager, RiskCheck


class TestRiskManager:
    """Test cases for risk manager."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.risk = RiskManager(
            max_position_usdt=500.0,
            max_order_usdt=50.0,
            max_daily_orders=10
        )
    
    def test_can_place_order_within_limits(self):
        """Test order approval when within limits."""
        check = self.risk.can_place_order(
            current_position=100.0,
            order_size=50.0
        )
        
        assert isinstance(check, RiskCheck)
        assert check.passed is True
        assert "passed" in check.reason.lower()
    
    def test_rejects_order_exceeding_position_limit(self):
        """Test order rejection when position limit exceeded."""
        check = self.risk.can_place_order(
            current_position=480.0,
            order_size=50.0
        )
        
        assert check.passed is False
        assert "limit exceeded" in check.reason.lower()
        assert "current_position" in check.metadata
    
    def test_rejects_oversized_order(self):
        """Test order rejection when order size too large."""
        check = self.risk.can_place_order(
            current_position=100.0,
            order_size=100.0  # Exceeds max_order_usdt
        )
        
        assert check.passed is False
        assert "too large" in check.reason.lower()
    
    def test_rejects_excessive_daily_orders(self):
        """Test order rejection when daily limit reached."""
        check = self.risk.can_place_order(
            current_position=100.0,
            order_size=50.0,
            daily_orders=10
        )
        
        assert check.passed is False
        assert "daily" in check.reason.lower()
    
    def test_position_utilization_calculation(self):
        """Test position utilization percentage."""
        utilization = self.risk.get_position_utilization(250.0)
        assert utilization == 50.0
        
        utilization = self.risk.get_position_utilization(500.0)
        assert utilization == 100.0
        
        utilization = self.risk.get_position_utilization(0.0)
        assert utilization == 0.0
    
    def test_available_capacity_calculation(self):
        """Test available capacity calculation."""
        available = self.risk.get_available_capacity(100.0)
        assert available == 400.0
        
        available = self.risk.get_available_capacity(500.0)
        assert available == 0.0
        
        available = self.risk.get_available_capacity(0.0)
        assert available == 500.0

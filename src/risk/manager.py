"""
Risk management system implementing multi-layer controls.

Provides position limits, exposure checks, and risk validation
before order execution.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class RiskCheck:
    """Result of a risk validation check."""

    passed: bool
    reason: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize metadata if None."""
        if self.metadata is None:
            self.metadata = {}


class RiskManager:
    """
    Multi-layer risk management system.

    Implements position limits, order size validation, and
    exposure controls.
    """

    def __init__(
        self,
        max_position_usdt: float,
        max_order_usdt: float,
        max_daily_orders: int = 10,
    ):
        """
        Initialize risk manager.

        Args:
            max_position_usdt: Maximum total position value
            max_order_usdt: Maximum single order size
            max_daily_orders: Maximum orders per day (optional)
        """
        self.max_position_usdt = max_position_usdt
        self.max_order_usdt = max_order_usdt
        self.max_daily_orders = max_daily_orders
        self.daily_order_count = 0

    def can_place_order(
        self,
        current_position: float,
        order_size: float,
        daily_orders: Optional[int] = None,
    ) -> RiskCheck:
        """
        Check if order can be placed based on risk limits.

        Args:
            current_position: Current position value in USDT
            order_size: Proposed order size in USDT
            daily_orders: Number of orders placed today (optional)

        Returns:
            RiskCheck result with pass/fail and reason
        """
        # Check position limit
        new_position = current_position + order_size
        if new_position > self.max_position_usdt:
            return RiskCheck(
                passed=False,
                reason=f"Position limit exceeded: {new_position:.2f} > "
                f"{self.max_position_usdt:.2f} USDT",
                metadata={
                    "current_position": current_position,
                    "order_size": order_size,
                    "max_position": self.max_position_usdt,
                },
            )

        # Check single order size
        if order_size > self.max_order_usdt:
            return RiskCheck(
                passed=False,
                reason=f"Order size too large: {order_size:.2f} > "
                f"{self.max_order_usdt:.2f} USDT",
                metadata={
                    "order_size": order_size,
                    "max_order": self.max_order_usdt,
                },
            )

        # Check daily order count
        if daily_orders is not None and daily_orders >= self.max_daily_orders:
            return RiskCheck(
                passed=False,
                reason=f"Daily order limit reached: {daily_orders} >= "
                f"{self.max_daily_orders}",
                metadata={
                    "daily_orders": daily_orders,
                    "max_daily_orders": self.max_daily_orders,
                },
            )

        return RiskCheck(
            passed=True,
            reason="Risk checks passed",
            metadata={
                "current_position": current_position,
                "new_position": new_position,
                "order_size": order_size,
                "position_utilization": (
                    new_position / self.max_position_usdt * 100
                ),
            },
        )

    def get_position_utilization(self, current_position: float) -> float:
        """
        Calculate position utilization percentage.

        Args:
            current_position: Current position value

        Returns:
            Utilization percentage (0-100)
        """
        return (current_position / self.max_position_usdt) * 100

    def get_available_capacity(self, current_position: float) -> float:
        """
        Calculate remaining position capacity.

        Args:
            current_position: Current position value

        Returns:
            Available capacity in USDT
        """
        return max(0, self.max_position_usdt - current_position)

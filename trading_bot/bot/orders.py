"""
orders.py
---------
Order placement logic for Binance Futures Testnet.

Provides a high-level 'OrderManager' that:
  - Accepts validated parameters
  - Builds the correct request payload for each order type
  - Returns a rich 'OrderResult' dataclass
  - Formats a human-readable summary for CLI output
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, Optional

from .client import BinanceFuturesClient
from .logging_config import get_logger

logger = get_logger("orders")


# ── Result dataclass ──────────────────────────────────────────────────────────


@dataclass
class OrderResult:
    """
    Structured representation of a Binance order response.

    Attributes
    ----------
    order_id : int
        Binance-assigned order ID.
    client_order_id : str
        Client-generated order ID.
    symbol : str
        Trading pair.
    side : str
        BUY or SELL.
    order_type : str
        MARKET, LIMIT, STOP, STOP_MARKET, etc.
    status : str
        Order status (NEW, FILLED, PARTIALLY_FILLED, …).
    orig_qty : str
        Original order quantity.
    executed_qty : str
        Quantity executed so far.
    avg_price : str
        Average fill price (if any).
    price : str
        Limit price (if any).
    raw : dict
        Full raw response from Binance.
    """

    order_id: int
    client_order_id: str
    symbol: str
    side: str
    order_type: str
    status: str
    orig_qty: str
    executed_qty: str
    avg_price: str
    price: str
    raw: Dict[str, Any] = field(repr=False)

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "OrderResult":
        """Build an OrderResult from a raw Binance API response dict."""
        return cls(
            order_id=data.get("orderId", 0),
            client_order_id=data.get("clientOrderId", ""),
            symbol=data.get("symbol", ""),
            side=data.get("side", ""),
            order_type=data.get("type", ""),
            status=data.get("status", ""),
            orig_qty=data.get("origQty", "0"),
            executed_qty=data.get("executedQty", "0"),
            avg_price=data.get("avgPrice", "0"),
            price=data.get("price", "0"),
            raw=data,
        )

    def summary(self) -> str:
        """Return a concise human-readable summary string."""
        lines = [
            "─" * 52,
            "  ORDER RESULT",
            "─" * 52,
            f"  Order ID       : {self.order_id}",
            f"  Client OID     : {self.client_order_id}",
            f"  Symbol         : {self.symbol}",
            f"  Side           : {self.side}",
            f"  Type           : {self.order_type}",
            f"  Status         : {self.status}",
            f"  Orig Qty       : {self.orig_qty}",
            f"  Executed Qty   : {self.executed_qty}",
            f"  Avg Fill Price : {self.avg_price}",
            f"  Limit Price    : {self.price}",
            "─" * 52,
        ]
        return "\n".join(lines)


# ── Order Manager ─────────────────────────────────────────────────────────────


class OrderManager:
    """
    High-level order placement controller.

    Parameters
    ----------
    client : BinanceFuturesClient
        Configured and authenticated Binance client.
    """

    def __init__(self, client: BinanceFuturesClient) -> None:
        self._client = client

    # ── Internal payload builders ─────────────────────────────────────────────

    def _build_market_params(
        self, symbol: str, side: str, quantity: Decimal
    ) -> Dict[str, Any]:
        return {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": str(quantity),
        }

    def _build_limit_params(
        self,
        symbol: str,
        side: str,
        quantity: Decimal,
        price: Decimal,
        time_in_force: str = "GTC",
    ) -> Dict[str, Any]:
        return {
            "symbol": symbol,
            "side": side,
            "type": "LIMIT",
            "quantity": str(quantity),
            "price": str(price),
            "timeInForce": time_in_force,
        }

    def _build_stop_params(
        self,
        symbol: str,
        side: str,
        quantity: Decimal,
        stop_price: Decimal,
        price: Optional[Decimal] = None,
    ) -> Dict[str, Any]:
        """
        Build params for either STOP_MARKET or STOP (stop-limit) order.

        If 'price' is provided → STOP (stop-limit); otherwise → STOP_MARKET.
        """
        if price is not None:
            return {
                "symbol": symbol,
                "side": side,
                "type": "STOP",
                "quantity": str(quantity),
                "price": str(price),
                "stopPrice": str(stop_price),
                "timeInForce": "GTC",
            }
        return {
            "symbol": symbol,
            "side": side,
            "type": "STOP_MARKET",
            "quantity": str(quantity),
            "stopPrice": str(stop_price),
        }

    # ── Public interface ──────────────────────────────────────────────────────

    def place_market_order(
        self, symbol: str, side: str, quantity: Decimal
    ) -> OrderResult:
        """
        Place a MARKET order.

        Parameters
        ----------
        symbol : str
            Validated trading pair.
        side : str
            'BUY' or 'SELL'.
        quantity : Decimal
            Order quantity.

        Returns
        -------
        OrderResult
            Parsed order result.
        """
        params = self._build_market_params(symbol, side, quantity)
        logger.info(
            "Submitting MARKET order | %s %s qty=%s", side, symbol, quantity
        )
        logger.debug("Request payload: %s", json.dumps(params, default=str))
        response = self._client.place_order(params)
        result = OrderResult.from_response(response)
        logger.info("MARKET order result: %s", result.summary())
        return result

    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: Decimal,
        price: Decimal,
        time_in_force: str = "GTC",
    ) -> OrderResult:
        """
        Place a LIMIT order.

        Parameters
        ----------
        symbol : str
            Validated trading pair.
        side : str
            'BUY' or 'SELL'.
        quantity : Decimal
            Order quantity.
        price : Decimal
            Limit price.
        time_in_force : str
            GTC (default), IOC, or FOK.

        Returns
        -------
        OrderResult
            Parsed order result.
        """
        params = self._build_limit_params(symbol, side, quantity, price, time_in_force)
        logger.info(
            "Submitting LIMIT order | %s %s qty=%s @ %s (%s)",
            side,
            symbol,
            quantity,
            price,
            time_in_force,
        )
        logger.debug("Request payload: %s", json.dumps(params, default=str))
        response = self._client.place_order(params)
        result = OrderResult.from_response(response)
        logger.info("LIMIT order result: %s", result.summary())
        return result

    def place_stop_order(
        self,
        symbol: str,
        side: str,
        quantity: Decimal,
        stop_price: Decimal,
        price: Optional[Decimal] = None,
    ) -> OrderResult:
        """
        Place a Stop-Market or Stop-Limit order.

        If 'price' is provided, places a STOP (stop-limit) order.
        Otherwise places a STOP_MARKET order.

        Parameters
        ----------
        symbol : str
            Validated trading pair.
        side : str
            'BUY' or 'SELL'.
        quantity : Decimal
            Order quantity.
        stop_price : Decimal
            Trigger price.
        price : Decimal, optional
            Limit price for stop-limit orders.

        Returns
        -------
        OrderResult
            Parsed order result.
        """
        order_type = "STOP" if price is not None else "STOP_MARKET"
        params = self._build_stop_params(symbol, side, quantity, stop_price, price)
        logger.info(
            "Submitting %s order | %s %s qty=%s stopPrice=%s%s",
            order_type,
            side,
            symbol,
            quantity,
            stop_price,
            f" limitPrice={price}" if price else "",
        )
        logger.debug("Request payload: %s", json.dumps(params, default=str))
        response = self._client.place_order(params)
        result = OrderResult.from_response(response)
        logger.info("%s order result: %s", order_type, result.summary())
        return result

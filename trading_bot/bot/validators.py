"""
validators.py
-------------
Input validation helpers for order parameters.
All functions raise ValueError with human-readable messages on failure.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Optional

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET", "STOP"}


def validate_symbol(symbol: str) -> str:
    """
    Ensure 'symbol' is a non-empty uppercase alphanumeric string.

    Parameters
    ----------
    symbol : str
        Trading pair, e.g. 'BTCUSDT'.

    Returns
    -------
    str
        Normalised (upper-cased) symbol.

    Raises
    ------
    ValueError
        If the symbol is empty or contains invalid characters.
    """
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    if not symbol.isalnum():
        raise ValueError(
            f"Symbol '{symbol}' contains invalid characters. "
            "Use alphanumeric only (e.g. BTCUSDT)."
        )
    return symbol


def validate_side(side: str) -> str:
    """
    Ensure 'side' is either 'BUY' or 'SELL'.

    Parameters
    ----------
    side : str
        Order side.

    Returns
    -------
    str
        Normalised (upper-cased) side.

    Raises
    ------
    ValueError
        If side is not recognised.
    """
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        )
    return side


def validate_order_type(order_type: str) -> str:
    """
    Ensure 'order_type' is a supported type.

    Parameters
    ----------
    order_type : str
        Order type string.

    Returns
    -------
    str
        Normalised (upper-cased) order type.

    Raises
    ------
    ValueError
        If order_type is not recognised.
    """
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return order_type


def validate_quantity(quantity: str | float) -> Decimal:
    """
    Ensure 'quantity' is a positive finite decimal number.

    Parameters
    ----------
    quantity : str | float
        Order quantity.

    Returns
    -------
    Decimal
        Validated quantity as Decimal.

    Raises
    ------
    ValueError
        If quantity is not positive or not a valid number.
    """
    try:
        qty = Decimal(str(quantity))
    except InvalidOperation:
        raise ValueError(f"Quantity '{quantity}' is not a valid number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than 0 (got {qty}).")
    return qty


def validate_price(price: str | float | None, order_type: str) -> Optional[Decimal]:
    """
    Validate price field based on order type.

    Parameters
    ----------
    price : str | float | None
        Order price.
    order_type : str
        Normalised order type.

    Returns
    -------
    Decimal | None
        Validated price, or None for MARKET orders.

    Raises
    ------
    ValueError
        If price is required but missing, or if it is not positive.
    """
    if order_type == "MARKET":
        return None

    if price is None:
        raise ValueError(f"Price is required for {order_type} orders.")

    try:
        p = Decimal(str(price))
    except InvalidOperation:
        raise ValueError(f"Price '{price}' is not a valid number.")
    if p <= 0:
        raise ValueError(f"Price must be greater than 0 (got {p}).")
    return p


def validate_stop_price(
    stop_price: str | float | None, order_type: str
) -> Optional[Decimal]:
    """
    Validate stop price for STOP / STOP_MARKET orders.

    Parameters
    ----------
    stop_price : str | float | None
        Stop-trigger price.
    order_type : str
        Normalised order type.

    Returns
    -------
    Decimal | None
        Validated stop price, or None when not applicable.

    Raises
    ------
    ValueError
        If stop price is required but missing, or not positive.
    """
    if order_type not in ("STOP", "STOP_MARKET"):
        return None

    if stop_price is None:
        raise ValueError(f"stopPrice is required for {order_type} orders.")

    try:
        sp = Decimal(str(stop_price))
    except InvalidOperation:
        raise ValueError(f"stopPrice '{stop_price}' is not a valid number.")
    if sp <= 0:
        raise ValueError(f"stopPrice must be greater than 0 (got {sp}).")
    return sp


def validate_all(
    *,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: str | float | None = None,
    stop_price: str | float | None = None,
) -> dict:
    """
    Run all validations and return a cleaned parameter dict.

    Returns
    -------
    dict
        Validated parameters with keys:
        symbol, side, order_type, quantity, price, stop_price.
    """
    v_symbol = validate_symbol(symbol)
    v_side = validate_side(side)
    v_type = validate_order_type(order_type)
    v_qty = validate_quantity(quantity)
    v_price = validate_price(price, v_type)
    v_stop = validate_stop_price(stop_price, v_type)

    return {
        "symbol": v_symbol,
        "side": v_side,
        "order_type": v_type,
        "quantity": v_qty,
        "price": v_price,
        "stop_price": v_stop,
    }

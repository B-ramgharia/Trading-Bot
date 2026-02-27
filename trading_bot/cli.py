"""
cli.py
------
CLI entry point for the Binance Futures Testnet trading bot.

Usage examples
--------------
# Market BUY
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Limit SELL
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 90000

# Stop-Market BUY
python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 85000

# Stop-Limit SELL
python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.001 --stop-price 85000 --price 84900
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# ── Bootstrap path so we can run 'python cli.py' from the project root ────────
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv

from trading_bot.bot.client import BinanceFuturesClient, BinanceAPIError
from trading_bot.bot.logging_config import setup_logging, get_logger
from trading_bot.bot.orders import OrderManager
from trading_bot.bot.validators import validate_all

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
#  Argument parser
# ─────────────────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Market BUY 0.001 BTC
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  # Limit SELL 0.001 BTC @ 90000 USDT
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 90000

  # Stop-Market BUY trigger @ 85000
  python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 85000

  # Stop-Limit SELL trigger @ 85000, limit @ 84900
  python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.001 --stop-price 85000 --price 84900
        """,
    )

    parser.add_argument(
        "--symbol",
        required=True,
        help="Trading pair, e.g. BTCUSDT",
        metavar="SYMBOL",
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL"],
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type",
        required=True,
        dest="order_type",
        choices=["MARKET", "LIMIT", "STOP_MARKET", "STOP"],
        help="Order type",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        type=float,
        help="Order quantity (base asset)",
        metavar="QTY",
    )
    parser.add_argument(
        "--price",
        required=False,
        type=float,
        default=None,
        help="Limit price (required for LIMIT and STOP orders)",
    )
    parser.add_argument(
        "--stop-price",
        required=False,
        type=float,
        default=None,
        dest="stop_price",
        help="Stop trigger price (required for STOP_MARKET / STOP orders)",
    )
    parser.add_argument(
        "--tif",
        required=False,
        default="GTC",
        choices=["GTC", "IOC", "FOK"],
        help="Time-in-force for LIMIT orders (default: GTC)",
    )
    parser.add_argument(
        "--log-level",
        default="DEBUG",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Minimum log level written to the log file (default: DEBUG)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print request summary WITHOUT placing the order",
    )
    return parser


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _print_banner() -> None:
    print(
        "\n"
        "╔══════════════════════════════════════════════════════╗\n"
        "║   Binance Futures Testnet – Trading Bot CLI          ║\n"
        "╚══════════════════════════════════════════════════════╝"
    )


def _print_request_summary(params: dict) -> None:
    print(
        "\n"
        "┌── Order Request Summary ──────────────────────────────┐\n"
        f"│  Symbol         : {params['symbol']}\n"
        f"│  Side           : {params['side']}\n"
        f"│  Type           : {params['order_type']}\n"
        f"│  Quantity       : {params['quantity']}\n"
        f"│  Price          : {params['price'] or 'N/A (MARKET)'}\n"
        f"│  Stop Price     : {params['stop_price'] or 'N/A'}\n"
        "└───────────────────────────────────────────────────────┘"
    )


def _load_credentials() -> tuple[str, str]:
    """Load API key and secret from environment, raising if absent."""
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()
    if not api_key or not api_secret:
        raise EnvironmentError(
            "BINANCE_API_KEY and BINANCE_API_SECRET must be set.\n"
            "Copy .env.example → .env and fill in your testnet credentials."
        )
    return api_key, api_secret


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    setup_logging(log_level=args.log_level)
    logger = get_logger("cli")
    _print_banner()

    # ── Step 1: Validate all inputs ───────────────────────────────────────────
    try:
        validated = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValueError as exc:
        logger.error("Input validation failed: %s", exc)
        print(f"\n❌  Validation error: {exc}\n")
        sys.exit(1)

    _print_request_summary(validated)

    if args.dry_run:
        print("\n⚠️  Dry-run mode – order NOT placed.\n")
        logger.info("Dry-run complete. Parameters: %s", validated)
        sys.exit(0)

    # ── Step 2: Load credentials ──────────────────────────────────────────────
    try:
        api_key, api_secret = _load_credentials()
    except EnvironmentError as exc:
        logger.error("Credential error: %s", exc)
        print(f"\n❌  {exc}\n")
        sys.exit(1)

    # ── Step 3: Initialise client & manager ───────────────────────────────────
    client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)
    manager = OrderManager(client)

    symbol = validated["symbol"]
    side = validated["side"]
    qty = validated["quantity"]
    price = validated["price"]
    stop_price = validated["stop_price"]
    order_type = validated["order_type"]

    # ── Step 4: Place order ───────────────────────────────────────────────────
    try:
        if order_type == "MARKET":
            result = manager.place_market_order(symbol, side, qty)

        elif order_type == "LIMIT":
            result = manager.place_limit_order(
                symbol, side, qty, price, time_in_force=args.tif
            )

        elif order_type in ("STOP_MARKET", "STOP"):
            result = manager.place_stop_order(symbol, side, qty, stop_price, price)

        else:
            print(f"\n❌  Unsupported order type: {order_type}\n")
            sys.exit(1)

    except BinanceAPIError as exc:
        logger.error("API error while placing order: %s", exc)
        print(f"\n❌  Binance API error [{exc.code}]: {exc.message}\n")
        sys.exit(1)
    except Exception as exc:
        logger.exception("Unexpected error while placing order: %s", exc)
        print(f"\n❌  Unexpected error: {exc}\n")
        sys.exit(1)

    # ── Step 5: Print result ──────────────────────────────────────────────────
    print("\n✅  Order placed successfully!\n")
    print(result.summary())
    print()


if __name__ == "__main__":
    main()

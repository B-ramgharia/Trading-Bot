"""
client.py
---------
Binance Futures Testnet REST API client.

Wraps raw HTTP calls with:
  - HMAC-SHA256 request signing
  - Structured request / response logging
  - Retry on transient network errors
  - Descriptive exception mapping
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .logging_config import get_logger

logger = get_logger("client")

# ── Default configuration ─────────────────────────────────────────────────────
TESTNET_BASE_URL: str = os.getenv(
    "BINANCE_BASE_URL", "https://testnet.binancefuture.com"
)
DEFAULT_TIMEOUT: int = 10  # seconds
REQUEST_WINDOW: int = 5_000  # ms – recvWindow sent with each signed request


class BinanceAPIError(Exception):
    """Raised when Binance returns a non-2xx response or a -XXXX error code."""

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class BinanceFuturesClient:
    """
    Lightweight Binance USDT-M Futures Testnet client.

    Parameters
    ----------
    api_key : str
        Binance API key.
    api_secret : str
        Binance API secret (used for HMAC signing).
    base_url : str
        Base URL for the Futures Testnet (overridable for prod).
    timeout : int
        HTTP request timeout in seconds.
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = TESTNET_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self._api_key = api_key
        self._api_secret = api_secret
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = self._build_session()

    # ── Session construction ──────────────────────────────────────────────────

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update(
            {
                "X-MBX-APIKEY": self._api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        return session

    # ── Signing helpers ───────────────────────────────────────────────────────

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Append timestamp + recvWindow, then compute HMAC-SHA256 signature."""
        params["timestamp"] = int(time.time() * 1000)
        params["recvWindow"] = REQUEST_WINDOW
        query_string = urlencode(params)
        signature = hmac.new(
            self._api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    # ── Core HTTP helpers ─────────────────────────────────────────────────────

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute a signed or unsigned HTTP request and return parsed JSON.

        Raises
        ------
        BinanceAPIError
            On API-level errors (non-zero 'code' in response body).
        requests.exceptions.RequestException
            On network / transport failures.
        """
        url = f"{self._base_url}{endpoint}"
        params = params or {}
        if signed:
            params = self._sign(params)

        logger.debug(
            "→ %s %s | params=%s",
            method.upper(),
            endpoint,
            {k: v for k, v in params.items() if k != "signature"},
        )

        try:
            if method.upper() == "GET":
                response = self._session.get(url, params=params, timeout=self._timeout)
            elif method.upper() == "POST":
                response = self._session.post(url, data=params, timeout=self._timeout)
            elif method.upper() == "DELETE":
                response = self._session.delete(
                    url, params=params, timeout=self._timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            logger.debug(
                "← %s %s | status=%s",
                method.upper(),
                endpoint,
                response.status_code,
            )

            data = response.json()

        except requests.exceptions.RequestException as exc:
            logger.error("Network error on %s %s: %s", method.upper(), endpoint, exc)
            raise

        # Binance error responses have a 'code' key (negative int) and 'msg'
        if isinstance(data, dict) and data.get("code", 0) != 0:
            code = data["code"]
            msg = data.get("msg", "Unknown error")
            logger.error("Binance API error %s: %s", code, msg)
            raise BinanceAPIError(code, msg)

        logger.debug("Response body: %s", data)
        return data

    # ── Public endpoints ──────────────────────────────────────────────────────

    def ping(self) -> bool:
        """Return True if the server is reachable."""
        try:
            self._request("GET", "/fapi/v1/ping", signed=False)
            logger.info("Server ping successful.")
            return True
        except Exception as exc:
            logger.warning("Server ping failed: %s", exc)
            return False

    def get_exchange_info(self) -> Dict[str, Any]:
        """Fetch exchange trading rules and symbol information."""
        return self._request("GET", "/fapi/v1/exchangeInfo", signed=False)

    def get_account_info(self) -> Dict[str, Any]:
        """Fetch account balance and position information."""
        return self._request("GET", "/fapi/v2/account")

    # ── Order endpoints ───────────────────────────────────────────────────────

    def place_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place a new order on Binance Futures.

        Parameters
        ----------
        params : dict
            Raw order parameters (symbol, side, type, quantity, etc.)

        Returns
        -------
        dict
            Full order response from Binance.
        """
        logger.info(
            "Placing order: symbol=%s side=%s type=%s qty=%s",
            params.get("symbol"),
            params.get("side"),
            params.get("type"),
            params.get("quantity"),
        )
        response = self._request("POST", "/fapi/v1/order", params=params)
        logger.info(
            "Order placed: orderId=%s status=%s",
            response.get("orderId"),
            response.get("status"),
        )
        return response

    def get_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Retrieve details of an existing order."""
        return self._request(
            "GET", "/fapi/v1/order", params={"symbol": symbol, "orderId": order_id}
        )

    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Cancel an open order."""
        return self._request(
            "DELETE",
            "/fapi/v1/order",
            params={"symbol": symbol, "orderId": order_id},
        )

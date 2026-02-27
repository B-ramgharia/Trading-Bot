# 🤖 Binance Futures Testnet – Trading Bot

A Python CLI trading bot for placing orders on the **Binance USDT-M Futures Testnet**. Supports **Market**, **Limit**, **Stop-Market**, and **Stop-Limit** order types with structured logging, input validation, and a clean modular architecture.

---

## ✨ Features

| Feature | Description |
|---|---|
| **4 Order Types** | MARKET · LIMIT · STOP_MARKET · STOP (stop-limit) |
| **HMAC-SHA256 Signing** | All signed requests follow Binance's authentication spec |
| **Input Validation** | Symbol, side, quantity, price, and stop-price validated before submission |
| **Structured Logging** | Rotating file logs (DEBUG) + coloured console output (INFO) |
| **Dry-Run Mode** | `--dry-run` flag validates inputs without placing an order |
| **Retry on Failure** | Automatic retry on 429 / 5xx HTTP errors |
| **Modular Design** | Clean separation: client → orders → validators → CLI |

---

## 📁 Project Structure

```
Trading Bot/
├── .env.example              # Template for API credentials
├── requirements.txt          # Python dependencies
├── README.md                 # ← You are here
├── trading_bot.db            # SQLite database (generated)
├── logs/
│   └── trading_bot.log       # Application logs
└── trading_bot/
    ├── __init__.py
    ├── cli.py                # CLI entry point
    ├── bot/                  # Core trading logic
    └── dashboard/            # Full-stack app
        ├── app.py            # FastAPI Backend
        ├── auth.py           # JWT & Hashing
        ├── database.py       # SQLite connection
        ├── models.py         # SQLModel definitions
        └── dashboard_ui.py   # Streamlit Frontend
```

---

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.10+**
- A **Binance Futures Testnet** account → [testnet.binancefuture.com](https://testnet.binancefuture.com)

### 2. Install dependencies

```bash
cd "Trading Bot"
pip install -r requirements.txt
```

### 3. Configure credentials

```bash
cp .env.example .env
# Edit .env and paste your testnet API key + secret
```

### 4. Place an order

```bash
# Market BUY 0.001 BTC
python trading_bot/cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Limit SELL 0.001 BTC @ 90,000 USDT
python trading_bot/cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 90000

# Stop-Market BUY trigger @ 85,000
python trading_bot/cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 85000

# Stop-Limit SELL trigger @ 85,000 / limit @ 84,900
python trading_bot/cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.001 --stop-price 85000 --price 84900
```

### 5. Dry-run (validate only)

```bash
python trading_bot/cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run
```

---

## 📋 CLI Reference

| Argument | Required | Description |
|---|---|---|
| `--symbol` | ✅ | Trading pair (e.g. `BTCUSDT`) |
| `--side` | ✅ | `BUY` or `SELL` |
| `--type` | ✅ | `MARKET`, `LIMIT`, `STOP_MARKET`, `STOP` |
| `--quantity` | ✅ | Order quantity in base asset |
| `--price` | ❌ | Limit price (required for LIMIT and STOP) |
| `--stop-price` | ❌ | Trigger price (required for STOP_MARKET / STOP) |
| `--tif` | ❌ | Time-in-force: `GTC` (default), `IOC`, `FOK` |
| `--log-level` | ❌ | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `--dry-run` | ❌ | Validate inputs without placing order |

---

## 📄 Sample Log Output

**MARKET BUY** – filled instantly at market price:
```
2026-02-27 09:05:12 | INFO     | trading_bot.cli    | Logging initialised
2026-02-27 09:05:13 | INFO     | trading_bot.orders | MARKET order result:
────────────────────────────────────────────────────
  ORDER RESULT
────────────────────────────────────────────────────
  Order ID       : 4020905628
  Symbol         : BTCUSDT
  Side           : BUY
  Type           : MARKET
  Status         : FILLED
  Orig Qty       : 0.001
  Executed Qty   : 0.001
  Avg Fill Price : 84321.40
────────────────────────────────────────────────────
```

**LIMIT SELL** – order placed, awaiting fill:
```
2026-02-27 09:12:45 | INFO     | trading_bot.orders | LIMIT order result:
────────────────────────────────────────────────────
  ORDER RESULT
────────────────────────────────────────────────────
  Order ID       : 4020912741
  Symbol         : BTCUSDT
  Side           : SELL
  Type           : LIMIT
  Status         : NEW
  Limit Price    : 90000
────────────────────────────────────────────────────
```

---

## 🏗️ Architecture & Design Decisions

1. **`client.py`** – Low-level HTTP client. Handles HMAC signing, timestamping, retry logic, and error mapping. All other modules depend on this.
2. **`orders.py`** – `OrderManager` builds typed payloads and returns `OrderResult` dataclasses. Keeps order logic separate from HTTP concerns.
3. **`validators.py`** – Pure validation functions (no side effects). Each returns a cleaned value or raises `ValueError`.
4. **`cli.py`** – Thin orchestration: parse args → validate → load credentials → place order → print result.
5. **`logging_config.py`** – Single `setup_logging()` call configures rotating file + console handlers. Child loggers created via `get_logger(name)`.

---

## 🔒 Security Considerations

- API keys are loaded from `.env` (never hardcoded)
- `.env` should be added to `.gitignore` (included in `.env.example`)
- HMAC-SHA256 signing per Binance spec
- `recvWindow` set to 5 000 ms to limit replay attacks
- Testnet only by default – production URL requires manual override

---

## 📈 Scaling Notes

| Area | Current | Production Path |
|---|---|---|
| **Order types** | 4 types | Add OCO, Trailing-Stop via new builder methods |
| **Concurrency** | Synchronous requests | Switch to `aiohttp` + async `OrderManager` |
| **Persistence** | Log files only | Add SQLite/PostgreSQL trade journal |
| **Monitoring** | CLI output | WebSocket price feeds + alerting |
| **CI/CD** | Manual | Add `pytest` suite + GitHub Actions |
| **Config** | `.env` | Use `pydantic-settings` for typed configuration |

---

## 🎁 Bonus Features (Completed)

This submission includes several optional enhancements to demonstrate technical breadth:

1.  **Extra Order Types**: Beyond MARKET/LIMIT, I've implemented **STOP_MARKET** and **STOP (Stop-Limit)** support.
2.  **Premium Dashboard**: A full-stack **React + FastAPI + TailwindCSS** dashboard with live charts (`lightweight-charts`) and a glassmorphism UI.
3.  **Enhanced CLI UX**: Using a clean layout with colored verification messages and exhaustive validation.

---

## 📜 Project Assumptions & Implementation Notes

- **Symbol Format**: Assumes standard Binance pair format (uppercase, e.g., `BTCUSDT`).
- **Precision**: Uses standard string-to-float conversion; for ultra-high precision financial apps, `decimal.Decimal` is recommended (current logic uses standard float for simplified testnet demo).
- **Environment**: Tested on Python 3.10+ and modern Node.js environments.

---

## 📜 License

MIT – Free for personal and educational use.

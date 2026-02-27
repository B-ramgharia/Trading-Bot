# 🤖 Binance Futures Testnet – Trading Bot (Application Task)

This project is a submission for the **Binance Futures Testnet Trading Bot** application task. It features a robust Python CLI for order execution and a **Premium React Dashboard** as an enhanced UI bonus.

---

## 📋 Core Requirements (Hiring Manager Checklist)

| Requirement | Implementation Details |
|---|---|
| **Language** | Python 3.10+ |
| **Orders** | MARKET, LIMIT, STOP_MARKET, and STOP (Stop-Limit) supported. |
| **Sides** | Fully supports both `BUY` and `SELL` sides. |
| **CLI Validation** | Comprehensive input validation for symbol, side, type, quantity, and price. |
| **Direct REST** | Direct HMAC-SHA256 signed REST calls (no external client library used). |
| **Logging** | Structured rotating file logs + detailed record of all API interactions. |
| **Architecture** | Clean separation: `client` (API) → `orders` (Logic) → `cli` (Entry). |
| **Error Handling** | Robust exception handling for network, API (429/5xx), and logic errors. |

---

## 📁 Project Structure

Following the suggested recruitment architecture with enhanced layers:

```
Trading Bot/
├── trading_bot/
│   ├── bot/                  # Core Trading Engine
│   │   ├── client.py         # HMAC-Signed REST Wrapper (Deliverable)
│   │   ├── orders.py         # Order Placement Logic (Deliverable)
│   │   ├── validators.py     # Input Validation (Deliverable)
│   │   └── logging_config.py # Structured Logging (Deliverable)
│   ├── cli.py                # Main CLI Entry Point (Deliverable)
│   └── dashboard/            # ✨ Bonus: Full-Stack App
│       ├── app.py            # FastAPI Backend
│       └── frontend/         # Premium React (Vite) Frontend
├── logs/                     # Order Evidence Logs (Deliverable)
├── README.md                 # Setup & Reference
├── requirements.txt          # Python Dependencies
├── .env.example              # API Credential Template
└── .gitignore                # Security Configuration
```

---

## 🚀 Setup & Execution

### 1. Prerequisites
- **Python 3.10+**
- **Node.js** (Only required for the React Dashboard bonus)

### 2. Installation
```bash
# Clone the repository and install Python dependencies
pip install -r requirements.txt
```

### 3. API Configuration
1. Copy `.env.example` to `.env`.
2. Enter your **Binance Futures Testnet** API Key and Secret.
   - Base URL used: `https://testnet.binancefuture.com`

---

## ⌨️ CLI Usage Examples

Ensure you are in the project root.

### Place a MARKET BUY Order
```bash
python trading_bot/cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Place a LIMIT SELL Order
```bash
python trading_bot/cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 95000
```

### Dry-Run (Validation only)
```bash
python trading_bot/cli.py --symbol ETHUSDT --side BUY --type MARKET --quantity 0.1 --dry-run
```

---

## ✨ Bonus: Premium React Dashboard

As an optional bonus, I have implemented a full-stack dashboard featuring **Glassmorphism**, **Live TradingView Charts**, and **JWT Authentication**.

**To launch both the Backend and Frontend with one command:**
```bash
cd trading_bot/dashboard/frontend
npm run dev
```

---

## 📄 Assumptions & Design Decisions
1. **Safety First**: The bot defaults to the Testnet URL. Placing real orders requires a manual configuration change in `client.py` to prevent accidental loss.
2. **REST over Library**: Implemented direct REST calls to demonstrate understanding of HMAC-SHA256 signing and Binance's API authentication protocol.
3. **Structured Logs**: Logs include full request headers/bodies for debugging, but hide sensitive API keys.

---

## ✅ Deliverables Included
- [x] Full Source Code (Clean & Modular)
- [x] Comprehensive README
- [x] Verified Log Files (`logs/market_order.log` & `logs/limit_order.log`)
- [x] Professional Git History & `.gitignore`

---

## 📜 License
MIT – Prepared for the Recruitment Application Task.

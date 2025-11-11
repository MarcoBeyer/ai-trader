# Configuration Files

This directory contains configuration files for the AI-Trader Bench. These JSON configuration files define the parameters and settings used by the trading agents during execution.

## Files

This directory contains multiple configuration files for different trading scenarios:

### Available Configurations

| Configuration File | Market | Trading Frequency | Description |
|-------------------|--------|-------------------|-------------|
| `default_config.json` | US (NASDAQ 100) | Daily | Default US stock trading configuration |
| `astock_config.json` | CN (SSE 50) | Daily | A-share market trading configuration |
| `alpaca_paper_config.json` | US (Alpaca) | Real-time | Alpaca paper trading configuration |

### `default_config.json`

The main configuration file that defines all system parameters. This file is loaded by `main.py` and contains the following sections:

#### Agent Configuration
- **`agent_type`**: Specifies which agent class to use 
- **`agent_config`**: Agent-specific parameters
  - `max_steps`: Maximum number of reasoning steps per trading decision (default: 30)
  - `max_retries`: Maximum retry attempts for failed operations (default: 3)
  - `base_delay`: Base delay between operations in seconds (default: 1.0)
  - `initial_cash`: Starting cash amount for trading (default: $10,000)

#### Date Range
- **`date_range`**: Trading period configuration
  - `init_date`: Start date for trading simulation (format: YYYY-MM-DD)
  - `end_date`: End date for trading simulation (format: YYYY-MM-DD)

#### Model Configuration
- **`models`**: List of AI models to use for trading decisions
  - Each model entry contains:
    - `name`: Display name for the model
    - `basemodel`: Full model identifier/path
    - `signature`: Model signature for API calls
    - `enabled`: Boolean flag to enable/disable the model

#### Logging Configuration
- **`log_config`**: Logging parameters
  - `log_path`: Directory path where agent data and logs are stored

## Usage

### Quick Start with Scripts

The easiest way to run the system with a specific configuration:

```bash
# US Market (NASDAQ 100) - uses default_config.json
bash scripts/main.sh

# US Market with hourly data
bash scripts/main_step1.sh  # Prepare hourly price data
bash scripts/main_step2.sh  # Start MCP services
bash scripts/main_step3.sh  # Run with test_real_hour_config.json

# A-Share Market (SSE 50) - uses astock_config.json
bash scripts/main_a_stock_step1.sh  # Prepare A-share data
bash scripts/main_a_stock_step2.sh  # Start MCP services
bash scripts/main_a_stock_step3.sh  # Run with astock_config.json
```

### Manual Configuration

#### Default Configuration
The system automatically loads `default_config.json` when no specific configuration file is provided:

```bash
python main.py
```

#### Custom Configuration
You can specify a custom configuration file:

```bash
python main.py configs/my_custom_config.json
python main.py configs/astock_config.json
python main.py configs/test_real_hour_config.json
```

### Environment Variable Overrides
Certain configuration values can be overridden using environment variables:
- `INIT_DATE`: Overrides the initial trading date
- `END_DATE`: Overrides the end trading date

## Configuration Examples

### US Stock Configuration (BaseAgent)
```json
{
  "agent_type": "BaseAgent",
  "market": "us",
  "date_range": {
    "init_date": "2025-01-01",
    "end_date": "2025-01-31"
  },
  "models": [
    {
      "name": "gpt-4o",
      "basemodel": "openai/gpt-4o-2024-11-20",
      "signature": "gpt-4o-2024-11-20",
      "enabled": true
    }
  ],
  "agent_config": {
    "max_steps": 30,
    "initial_cash": 10000.0
  },
  "log_config": {
    "log_path": "./data/agent_data"
  }
}
```

### A-Share Configuration (BaseAgentAStock)
```json
{
  "agent_type": "BaseAgentAStock",
  "market": "cn",
  "date_range": {
    "init_date": "2025-10-09",
    "end_date": "2025-10-31"
  },
  "models": [
    {
      "name": "claude-3.7-sonnet",
      "basemodel": "anthropic/claude-3.7-sonnet",
      "signature": "claude-3.7-sonnet",
      "enabled": true
    }
  ],
  "agent_config": {
    "max_steps": 30,
    "initial_cash": 100000.0
  },
  "log_config": {
    "log_path": "./data/agent_data_astock"
  }
}
```

### Multi-Model Configuration
```json
{
  "agent_type": "BaseAgent",
  "date_range": {
    "init_date": "2025-01-01",
    "end_date": "2025-01-31"
  },
  "models": [
    {
      "name": "claude-3.7-sonnet",
      "basemodel": "anthropic/claude-3.7-sonnet",
      "signature": "claude-3.7-sonnet",
      "enabled": true
    },
    {
      "name": "gpt-4o",
      "basemodel": "openai/gpt-4o-2024-11-20",
      "signature": "gpt-4o-2024-11-20",
      "enabled": true
    },
    {
      "name": "qwen3-max",
      "basemodel": "qwen/qwen3-max",
      "signature": "qwen3-max",
      "enabled": false
    }
  ],
  "agent_config": {
    "max_steps": 50,
    "max_retries": 5,
    "base_delay": 2.0,
    "initial_cash": 20000.0
  },
  "log_config": {
    "log_path": "./data/agent_data"
  }
}
```

### Alpaca Paper Trading Configuration
```json
{
  "agent_type": "BaseAgent",
  "market": "us",
  "trading_mode": "alpaca_paper",
  "date_range": {
    "init_date": "2025-10-01",
    "end_date": "2025-10-21"
  },
  "models": [
    {
      "name": "gpt-4o",
      "basemodel": "openai/gpt-4o",
      "signature": "gpt-4o-alpaca",
      "enabled": true
    }
  ],
  "agent_config": {
    "max_steps": 30,
    "max_retries": 3,
    "base_delay": 1.0,
    "initial_cash": 10000.0
  },
  "log_config": {
    "log_path": "./data/agent_data_alpaca"
  },
  "alpaca_config": {
    "paper_trading": true,
    "enable_alpaca": true
  }
}
```

## Alpaca Integration

The system now supports real trading through the Alpaca API for both paper trading (simulated) and live trading.

### Setup

1. **Get Alpaca API Credentials**:
   - Sign up for a free account at [Alpaca](https://alpaca.markets/)
   - Generate API keys from your dashboard
   - For paper trading, use paper trading API keys
   - For live trading, use live trading API keys

2. **Configure Environment Variables**:
   Add your Alpaca credentials to `.env`:
   ```bash
   ALPACA_API_KEY=your_alpaca_api_key
   ALPACA_SECRET_KEY=your_alpaca_secret_key
   ALPACA_HTTP_PORT=8004
   ```

3. **Start MCP Services with Alpaca**:
   When Alpaca credentials are configured in `.env`, the Alpaca trading service will automatically start:
   ```bash
   cd agent_tools
   python start_mcp_services.py
   ```

### Alpaca Tools Available

The Alpaca integration provides the following MCP tools:

- **`alpaca_buy(symbol, amount, paper=True)`**: Buy stocks via Alpaca
- **`alpaca_sell(symbol, amount, paper=True)`**: Sell stocks via Alpaca
- **`alpaca_get_account(paper=True)`**: Get account balance and portfolio value
- **`alpaca_get_positions(paper=True)`**: Get current stock positions
- **`alpaca_get_latest_price(symbol)`**: Get latest market quote for a symbol

### Paper Trading vs Live Trading

- **Paper Trading** (`paper=True`): Uses Alpaca's paper trading environment with simulated money
- **Live Trading** (`paper=False`): Uses real money in the live market ⚠️

**Important**: Always test your strategies with paper trading first before using live trading!

### Example Usage

```bash
# Run with Alpaca paper trading configuration
python main.py configs/alpaca_paper_config.json
```

### Notes on Alpaca Trading

- Alpaca supports fractional shares for most US stocks
- Market orders are executed at the current market price
- Trading is only available during market hours (9:30 AM - 4:00 PM ET, weekdays)
- Paper trading accounts start with $100,000 virtual cash
- All trades are logged in `data/agent_data_alpaca/{signature}/alpaca_trades/trades.jsonl`

## Agent Types

### BaseAgent
- **Market Support**: US stocks or A-shares (configurable via `market` parameter)
- **Use Case**: General-purpose trading agent with flexible market selection
- **Stock Pool**: Configurable (NASDAQ 100 by default for US, SSE 50 for CN)

### BaseAgentAStock
- **Market Support**: A-share market only
- **Use Case**: Specialized A-share trading with built-in Chinese market rules
- **Stock Pool**: SSE 50 by default
- **Trading Rules**: T+1 settlement, 100-share lot size, CNY pricing

## Notes

- Configuration files must be valid JSON format
- The system validates date ranges and ensures `init_date` is not greater than `end_date`
- Only models with `enabled: true` will be used for trading simulations
- Configuration errors will cause the system to exit with appropriate error messages
- The configuration system supports dynamic agent class loading through the `AGENT_REGISTRY` mapping
- When using `BaseAgentAStock`, the `market` parameter is automatically set to `"cn"`
- Initial cash should be $10,000 for US stocks and ¥100,000 for A-shares

"""
Alpaca Trading Tool - MCP tool for real trading via Alpaca API

This module provides trading functionality using Alpaca's API for both paper trading
and live trading. It integrates with the AI-Trader system following the same interface
as the simulated trading tool.
"""

import os
import sys
import json
from typing import Any, Dict, Optional
from pathlib import Path

from fastmcp import FastMCP
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus, QueryOrderStatus
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

# Add project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.general_tools import get_config_value, write_config_value

mcp = FastMCP("AlpacaTradeTools")


def _get_alpaca_client(paper: bool = True) -> TradingClient:
    """
    Create and return an Alpaca TradingClient instance.
    
    Args:
        paper: If True, use paper trading. If False, use live trading.
        
    Returns:
        TradingClient instance
        
    Raises:
        ValueError: If required API credentials are not found in environment
    """
    api_key = os.getenv("ALPACA_API_KEY")
    api_secret = os.getenv("ALPACA_SECRET_KEY")
    
    if not api_key or not api_secret:
        raise ValueError(
            "Alpaca API credentials not found. Please set ALPACA_API_KEY and "
            "ALPACA_SECRET_KEY environment variables."
        )
    
    return TradingClient(api_key=api_key, secret_key=api_secret, paper=paper)


def _get_alpaca_data_client() -> StockHistoricalDataClient:
    """
    Create and return an Alpaca StockHistoricalDataClient instance for market data.
    
    Returns:
        StockHistoricalDataClient instance
        
    Raises:
        ValueError: If required API credentials are not found in environment
    """
    api_key = os.getenv("ALPACA_API_KEY")
    api_secret = os.getenv("ALPACA_SECRET_KEY")
    
    if not api_key or not api_secret:
        raise ValueError(
            "Alpaca API credentials not found. Please set ALPACA_API_KEY and "
            "ALPACA_SECRET_KEY environment variables."
        )
    
    return StockHistoricalDataClient(api_key=api_key, secret_key=api_secret)


def _log_trade(action: str, symbol: str, amount: float, details: Dict[str, Any]) -> None:
    """
    Log trading action to file for record keeping.
    
    Args:
        action: Trading action ('buy' or 'sell')
        symbol: Stock symbol
        amount: Number of shares
        details: Additional details about the trade
    """
    signature = get_config_value("SIGNATURE")
    if not signature:
        return
        
    log_path = get_config_value("LOG_PATH", "./data/agent_data")
    if log_path.startswith("./data/"):
        log_path = log_path[7:]  # Remove "./data/" prefix
        
    today_date = get_config_value("TODAY_DATE")
    log_dir = Path(project_root) / "data" / log_path / signature / "alpaca_trades"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "trades.jsonl"
    log_entry = {
        "date": today_date,
        "action": action,
        "symbol": symbol,
        "amount": amount,
        "details": details
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


@mcp.tool()
def alpaca_buy(symbol: str, amount: float, paper: bool = True) -> Dict[str, Any]:
    """
    Buy stock using Alpaca API.
    
    This function executes a market order to buy stocks through Alpaca's trading API.
    It supports both paper trading (simulated) and live trading.
    
    Args:
        symbol: Stock symbol (e.g., "AAPL", "TSLA")
        amount: Number of shares to buy (can be fractional for supported stocks)
        paper: If True, use paper trading. If False, use live trading. Default is True.
        
    Returns:
        Dict[str, Any]:
          - Success: Returns order details including order_id, status, filled price, etc.
          - Failure: Returns {"error": error message, ...} dictionary
          
    Example:
        >>> result = alpaca_buy("AAPL", 10, paper=True)
        >>> print(result)  # {"order_id": "...", "status": "filled", "symbol": "AAPL", ...}
    """
    try:
        # Validate inputs
        if amount <= 0:
            return {
                "error": "Amount must be positive",
                "symbol": symbol,
                "amount": amount
            }
        
        # Get trading client
        client = _get_alpaca_client(paper=paper)
        
        # Create market order request
        order_data = MarketOrderRequest(
            symbol=symbol,
            qty=amount,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        
        # Submit order
        order = client.submit_order(order_data)
        
        # Prepare response
        result = {
            "success": True,
            "order_id": str(order.id),
            "symbol": order.symbol,
            "qty": float(order.qty) if order.qty else 0,
            "side": order.side.value,
            "type": order.type.value,
            "status": order.status.value,
            "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
            "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None,
            "submitted_at": str(order.submitted_at),
            "paper_trading": paper
        }
        
        # Log the trade
        _log_trade("buy", symbol, amount, result)
        
        # Mark that a trade was executed
        write_config_value("IF_TRADE", True)
        
        return result
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "symbol": symbol,
            "amount": amount,
            "paper_trading": paper
        }
        _log_trade("buy_failed", symbol, amount, error_result)
        return error_result


@mcp.tool()
def alpaca_sell(symbol: str, amount: float, paper: bool = True) -> Dict[str, Any]:
    """
    Sell stock using Alpaca API.
    
    This function executes a market order to sell stocks through Alpaca's trading API.
    It supports both paper trading (simulated) and live trading.
    
    Args:
        symbol: Stock symbol (e.g., "AAPL", "TSLA")
        amount: Number of shares to sell (can be fractional for supported stocks)
        paper: If True, use paper trading. If False, use live trading. Default is True.
        
    Returns:
        Dict[str, Any]:
          - Success: Returns order details including order_id, status, filled price, etc.
          - Failure: Returns {"error": error message, ...} dictionary
          
    Example:
        >>> result = alpaca_sell("AAPL", 10, paper=True)
        >>> print(result)  # {"order_id": "...", "status": "filled", "symbol": "AAPL", ...}
    """
    try:
        # Validate inputs
        if amount <= 0:
            return {
                "error": "Amount must be positive",
                "symbol": symbol,
                "amount": amount
            }
        
        # Get trading client
        client = _get_alpaca_client(paper=paper)
        
        # Check if we have sufficient position
        try:
            position = client.get_open_position(symbol)
            available_qty = float(position.qty)
            
            if available_qty < amount:
                return {
                    "error": f"Insufficient shares. You have {available_qty} shares but tried to sell {amount}",
                    "symbol": symbol,
                    "amount": amount,
                    "available": available_qty
                }
        except Exception as pos_error:
            # Position might not exist
            return {
                "error": f"No position found for {symbol} or unable to check position: {str(pos_error)}",
                "symbol": symbol,
                "amount": amount
            }
        
        # Create market order request
        order_data = MarketOrderRequest(
            symbol=symbol,
            qty=amount,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        
        # Submit order
        order = client.submit_order(order_data)
        
        # Prepare response
        result = {
            "success": True,
            "order_id": str(order.id),
            "symbol": order.symbol,
            "qty": float(order.qty) if order.qty else 0,
            "side": order.side.value,
            "type": order.type.value,
            "status": order.status.value,
            "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
            "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None,
            "submitted_at": str(order.submitted_at),
            "paper_trading": paper
        }
        
        # Log the trade
        _log_trade("sell", symbol, amount, result)
        
        # Mark that a trade was executed
        write_config_value("IF_TRADE", True)
        
        return result
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "symbol": symbol,
            "amount": amount,
            "paper_trading": paper
        }
        _log_trade("sell_failed", symbol, amount, error_result)
        return error_result


@mcp.tool()
def alpaca_get_account(paper: bool = True) -> Dict[str, Any]:
    """
    Get Alpaca account information including cash balance, buying power, and portfolio value.
    
    Args:
        paper: If True, use paper trading account. If False, use live trading account.
        
    Returns:
        Dict with account information including:
        - cash: Available cash balance
        - portfolio_value: Total portfolio value
        - buying_power: Current buying power
        - equity: Total equity value
        
    Example:
        >>> result = alpaca_get_account(paper=True)
        >>> print(result)  # {"cash": 100000.0, "portfolio_value": 100000.0, ...}
    """
    try:
        client = _get_alpaca_client(paper=paper)
        account = client.get_account()
        
        return {
            "success": True,
            "cash": float(account.cash),
            "portfolio_value": float(account.portfolio_value),
            "buying_power": float(account.buying_power),
            "equity": float(account.equity),
            "currency": account.currency,
            "status": account.status.value,
            "paper_trading": paper
        }
    except Exception as e:
        return {
            "error": str(e),
            "paper_trading": paper
        }


@mcp.tool()
def alpaca_get_positions(paper: bool = True) -> Dict[str, Any]:
    """
    Get all current positions in the Alpaca account.
    
    Args:
        paper: If True, use paper trading account. If False, use live trading account.
        
    Returns:
        Dict with list of positions, each containing:
        - symbol: Stock symbol
        - qty: Number of shares
        - avg_entry_price: Average entry price
        - current_price: Current market price
        - market_value: Current market value
        - unrealized_pl: Unrealized profit/loss
        
    Example:
        >>> result = alpaca_get_positions(paper=True)
        >>> print(result)  # {"positions": [{"symbol": "AAPL", "qty": 10, ...}], ...}
    """
    try:
        client = _get_alpaca_client(paper=paper)
        positions = client.get_all_positions()
        
        position_list = []
        for pos in positions:
            position_list.append({
                "symbol": pos.symbol,
                "qty": float(pos.qty),
                "avg_entry_price": float(pos.avg_entry_price),
                "current_price": float(pos.current_price),
                "market_value": float(pos.market_value),
                "unrealized_pl": float(pos.unrealized_pl),
                "unrealized_plpc": float(pos.unrealized_plpc)
            })
        
        return {
            "success": True,
            "positions": position_list,
            "count": len(position_list),
            "paper_trading": paper
        }
    except Exception as e:
        return {
            "error": str(e),
            "paper_trading": paper
        }


@mcp.tool()
def alpaca_get_latest_price(symbol: str) -> Dict[str, Any]:
    """
    Get the latest price quote for a stock symbol using Alpaca's market data API.
    
    Args:
        symbol: Stock symbol (e.g., "AAPL", "TSLA")
        
    Returns:
        Dict with latest quote information:
        - symbol: Stock symbol
        - bid_price: Latest bid price
        - ask_price: Latest ask price
        - bid_size: Latest bid size
        - ask_size: Latest ask size
        
    Example:
        >>> result = alpaca_get_latest_price("AAPL")
        >>> print(result)  # {"symbol": "AAPL", "bid_price": 150.25, "ask_price": 150.30, ...}
    """
    try:
        data_client = _get_alpaca_data_client()
        request_params = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        latest_quote = data_client.get_stock_latest_quote(request_params)
        
        quote = latest_quote[symbol]
        
        return {
            "success": True,
            "symbol": symbol,
            "bid_price": float(quote.bid_price),
            "ask_price": float(quote.ask_price),
            "bid_size": float(quote.bid_size),
            "ask_size": float(quote.ask_size),
            "timestamp": str(quote.timestamp)
        }
    except Exception as e:
        return {
            "error": str(e),
            "symbol": symbol
        }


if __name__ == "__main__":
    port = int(os.getenv("ALPACA_HTTP_PORT", "8004"))
    mcp.run(transport="streamable-http", port=port)

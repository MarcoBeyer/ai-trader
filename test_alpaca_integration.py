#!/usr/bin/env python3
"""
Alpaca Integration Test Script

This script demonstrates and tests the Alpaca trading integration.
It can be used to verify that your Alpaca API credentials are working correctly.

Usage:
    python test_alpaca_integration.py
    
Requirements:
    - Set ALPACA_API_KEY and ALPACA_SECRET_KEY in your .env file
    - Run this script to test paper trading connectivity
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_alpaca_credentials():
    """Test if Alpaca credentials are configured"""
    print("🔍 Checking Alpaca credentials...")
    api_key = os.getenv("ALPACA_API_KEY")
    api_secret = os.getenv("ALPACA_SECRET_KEY")
    
    if not api_key or not api_secret:
        print("❌ Alpaca credentials not found!")
        print("   Please set ALPACA_API_KEY and ALPACA_SECRET_KEY in your .env file")
        return False
    
    print(f"✅ Alpaca API Key: {api_key[:8]}...")
    print(f"✅ Alpaca Secret Key: {api_secret[:8]}...")
    return True

def test_alpaca_connection():
    """Test connection to Alpaca API"""
    print("\n🔌 Testing Alpaca API connection...")
    
    try:
        from alpaca.trading.client import TradingClient
        
        api_key = os.getenv("ALPACA_API_KEY")
        api_secret = os.getenv("ALPACA_SECRET_KEY")
        
        # Create client with paper trading
        client = TradingClient(api_key=api_key, secret_key=api_secret, paper=True)
        
        # Try to get account info
        account = client.get_account()
        
        print("✅ Successfully connected to Alpaca API!")
        print(f"   Account Status: {account.status}")
        print(f"   Cash Balance: ${float(account.cash):,.2f}")
        print(f"   Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"   Buying Power: ${float(account.buying_power):,.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Alpaca API: {e}")
        return False

def test_alpaca_tool():
    """Test the Alpaca MCP tool"""
    print("\n🛠️  Testing Alpaca MCP tool...")
    
    try:
        from agent_tools.tool_alpaca_trade import alpaca_get_account
        
        # Test getting account info through the tool
        result = alpaca_get_account(paper=True)
        
        if "error" in result:
            print(f"❌ Tool returned error: {result['error']}")
            return False
        
        print("✅ Alpaca MCP tool working correctly!")
        print(f"   Cash: ${result['cash']:,.2f}")
        print(f"   Portfolio Value: ${result['portfolio_value']:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test Alpaca tool: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Alpaca Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Check credentials
    if not test_alpaca_credentials():
        print("\n❌ Test suite failed: Credentials not configured")
        return 1
    
    # Test 2: Test API connection
    if not test_alpaca_connection():
        print("\n❌ Test suite failed: Could not connect to Alpaca API")
        return 1
    
    # Test 3: Test MCP tool
    if not test_alpaca_tool():
        print("\n❌ Test suite failed: MCP tool not working")
        return 1
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Alpaca integration is working correctly.")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("   1. Review configs/alpaca_paper_config.json")
    print("   2. Start MCP services: cd agent_tools && python start_mcp_services.py")
    print("   3. Run with Alpaca: python main.py configs/alpaca_paper_config.json")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

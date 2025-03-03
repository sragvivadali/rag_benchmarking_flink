import requests
import json
from datetime import datetime

def fetch_eodhd_data(symbols=["AAPL.US"], api_token="demo"):
    """
    Fetch real-time stock data from EODHD API for multiple symbols
    
    Args:
        symbols (list): List of stock symbols with exchange suffix (e.g., ["AAPL.US", "TSLA.US"])
        api_token (str): API token for EODHD (using 'demo' for testing)
    
    Returns:
        dict: JSON response with stock data for all symbols
    """
    # Per the API docs, we need one primary symbol and the rest as parameters
    base_url = "https://eodhd.com/api/real-time"
    primary_symbol = symbols[0]
    endpoint = f"{base_url}/{primary_symbol}"
    
    # If we have multiple symbols, add them as a comma-separated parameter
    params = {
        "api_token": api_token,
        "fmt": "json"
    }
    
    if len(symbols) > 1:
        additional_symbols = ",".join(symbols[1:])
        params["s"] = additional_symbols
    
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        data = response.json()
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def display_stock_data(data):
    """
    Format and display stock data for multiple symbols
    
    Args:
        data (dict or list): Stock data from EODHD API
    """
    if not data:
        print("No data available")
        return
    
    print("\n==== EODHD Real-Time Stock Data ====")
    
    # If data is a dictionary, it's for a single symbol
    if isinstance(data, dict):
        display_single_stock_data(data)
    # If data is a list, it contains multiple symbols
    elif isinstance(data, list):
        for stock in data:
            display_single_stock_data(stock)
            print("---------------------------------")
    
    print("=================================\n")

def display_single_stock_data(data):
    """
    Format and display data for a single stock
    
    Args:
        data (dict): Stock data for a single symbol
    """
    print(f"Symbol: {data.get('code', 'N/A')}")
    print(f"Exchange: {data.get('exchange_short_name', 'N/A')}")
    print(f"Price: ${data.get('close', 'N/A')}")
    print(f"Change: {data.get('change_p', 'N/A')}%")
    print(f"Volume: {data.get('volume', 'N/A')}")
    
    # Format timestamp if available
    if 'timestamp' in data:
        timestamp = datetime.fromtimestamp(data['timestamp'])
        print(f"Last Updated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    # Test with multiple symbols (note: demo API token only works with specific symbols)
    symbols = ["AAPL.US", "TSLA.US", "AMZN.US", "VTI.US"]
    api_token = "demo"  # Replace with your actual API token for production use
    
    print(f"Fetching real-time data for {', '.join(symbols)}...")
    stock_data = fetch_eodhd_data(symbols, api_token)
    
    if stock_data:
        # Pretty print raw JSON
        print("Raw JSON Response:")
        print(json.dumps(stock_data, indent=2))
        
        # Display formatted data
        display_stock_data(stock_data)
    else:
        print("Failed to retrieve data")

if __name__ == "__main__":
    main()
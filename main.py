import json
import requests
from datetime import datetime
from confluent_kafka import Producer, Consumer

def read_config():
    """Reads the client configuration from client.properties and returns it as a key-value map."""
    config = {}
    with open("client.properties") as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                config[parameter] = value.strip()
    return config

def fetch_eodhd_data(symbols=["AAPL.US"], api_token="demo"):
    """Fetches real-time stock data from EODHD API for multiple symbols."""
    base_url = "https://eodhd.com/api/real-time"
    primary_symbol = symbols[0]
    endpoint = f"{base_url}/{primary_symbol}"
    
    params = {
        "api_token": api_token,
        "fmt": "json"
    }
    
    if len(symbols) > 1:
        additional_symbols = ",".join(symbols[1:])
        params["s"] = additional_symbols
    
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def produce_stock_data(topic, config, stock_data):
    """Produces stock data messages to a Kafka topic."""
    producer = Producer(config)
    
    if not stock_data:
        print("No stock data available to produce.")
        return
    
    stock_data_json = json.dumps(stock_data)
    producer.produce(topic, key="stock_data", value=stock_data_json)
    print(f"Produced stock data to topic {topic}")
    producer.flush()

def consume_stock_data(topic, config):
    """Consumes and displays stock data messages from a Kafka topic."""
    print("Starting consumer...")
    config["group.id"] = "python-group-1"
    config["auto.offset.reset"] = "earliest"
    consumer = Consumer(config)
    consumer.subscribe([topic])
    
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is not None and msg.error() is None:
                key = msg.key().decode("utf-8")
                value = json.loads(msg.value().decode("utf-8"))
                print(f"Consumed message from topic {topic}: key = {key} value = {json.dumps(value, indent=2)}")
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

def main():
    config = read_config()
    topic = "new_documents"
    symbols = ["AAPL.US", "TSLA.US", "AMZN.US", "VTI.US"]
    api_token = "demo"
    
    print(f"Fetching real-time data for {', '.join(symbols)}...")
    stock_data = fetch_eodhd_data(symbols, api_token)
    
    if stock_data:
        produce_stock_data(topic, config, stock_data)
        consume_stock_data(topic, config)
    else:
        print("Failed to retrieve stock data")

if __name__ == "__main__":
    main()

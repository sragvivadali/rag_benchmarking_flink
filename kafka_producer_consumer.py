import json
import requests
from datetime import datetime
from confluent_kafka import Producer, Consumer

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

def produce_stock_data(topic, stock_data):
    """Produces stock data messages to a Kafka topic on localhost."""
    producer_config = {
        'bootstrap.servers': 'localhost:9092'
    }
    producer = Producer(producer_config)
    
    if not stock_data:
        print("No stock data available to produce.")
        return
    
    stock_data_json = json.dumps(stock_data)
    producer.produce(topic, key="stock_data", value=stock_data_json)
    print(f"Produced stock data to topic {topic}")
    producer.flush()

def consume_stock_data(topic):
    """Consumes and displays stock data messages from a Kafka topic on localhost."""
    print("Starting consumer...")
    consumer_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'python-group-1',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(consumer_config)
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
    topic = "my-topic"
    symbols = ["AAPL.US", "TSLA.US", "AMZN.US", "VTI.US"]
    api_token = "demo"
    
    print(f"Fetching real-time data for {', '.join(symbols)}...")
    stock_data = fetch_eodhd_data(symbols, api_token)
    
    if stock_data:
        produce_stock_data(topic, stock_data)
        consume_stock_data(topic)
    else:
        print("Failed to retrieve stock data")

if __name__ == "__main__":
    main()

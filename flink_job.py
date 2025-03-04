import json
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from sentence_transformers import SentenceTransformer

# Load the Sentence Transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

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

def process_stock_data(stock_json):
    """Convert stock data into an embedding vector."""
    try:
        stock_data = json.loads(stock_json)  # Parse JSON message
        text_representation = f"Stock Data: {json.dumps(stock_data, indent=2)}"  # Convert stock data to text
        embedding = model.encode(text_representation)  # Generate embedding
        return json.dumps({"stock_embedding": embedding.tolist()})  # Return JSON
    except Exception as e:
        return json.dumps({"error": str(e)})  # Handle errors gracefully

def main():
    kafka_props = read_config()
    kafka_props["group.id"] = "python-group-1"
    kafka_props["auto.offset.reset"] = "earliest"

    env = StreamExecutionEnvironment.get_execution_environment()

    print("Set up Flink")

    print("Props created")
    # Create Kafka Source
    consumer = FlinkKafkaConsumer(
        topics="new_documents",  # Match the producer's topic
        deserialization_schema=SimpleStringSchema(),
        properties=kafka_props
    )

    print("Consumer created")

    # Read data from Kafka topic
    stock_stream = env.add_source(consumer)

    # Process stream: Convert stock data to embeddings
    embedding_stream = stock_stream \
        .map(process_stock_data, output_type=Types.STRING())

    # Print the embeddings (Can also write to another Kafka topic)
    embedding_stream.print()

    # Execute Flink job
    env.execute("Stock Data Embedding with Flink")


if __name__ == "__main__":
    main()

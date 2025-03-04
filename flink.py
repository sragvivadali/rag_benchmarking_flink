import json
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from sentence_transformers import SentenceTransformer

# Load the Sentence Transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

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
    env = StreamExecutionEnvironment.get_execution_environment()

    # Kafka Consumer Configuration
    kafka_props = {
        "bootstrap.servers": "YOUR_CONFLUENT_CLOUD_BROKER",
        "group.id": "flink-embedding-group",
        "auto.offset.reset": "earliest"
    }

    # Create Kafka Source
    consumer = FlinkKafkaConsumer(
        topics="new_documents",  # Match the producer's topic
        deserialization_schema=SimpleStringSchema(),
        properties=kafka_props
    )

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

from confluent_kafka import Consumer, Producer
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
from sentence_transformers import SentenceTransformer
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

# Confluent Kafka Configuration
KAFKA_CONFIG = {
    'bootstrap.servers': 'your-confluent-broker',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': '4CEPHY36MPWKLVH3',
    'sasl.password': 'your-confluent-api-secret',
    'group.id': 'flink-group',
    'auto.offset.reset': 'earliest'
}

# Milvus Configuration
MILVUS_HOST = 'localhost'
MILVUS_PORT = '19530'
COLLECTION_NAME = 'document_embeddings'

# Initialize Flink Environment
env = StreamExecutionEnvironment.get_execution_environment()

# Sentence-BERT Model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Connect to Milvus
connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
collection = Collection(COLLECTION_NAME)

# Kafka Consumers
new_docs_consumer = FlinkKafkaConsumer(
    topics='new_documents',
    properties=KAFKA_CONFIG,
    deserialization_schema=SimpleStringSchema()
)

# Kafka Producers
processed_chunks_producer = FlinkKafkaProducer(
    topic='processed_chunks',
    producer_config=KAFKA_CONFIG,
    serialization_schema=SimpleStringSchema()
)

embedding_producer = FlinkKafkaProducer(
    topic='embedding',
    producer_config=KAFKA_CONFIG,
    serialization_schema=SimpleStringSchema()
)

# Define Flink Data Pipeline
def process_stream():
    stream = env.add_source(new_docs_consumer)

    def process_document(document):
        chunks = document.split('. ')  # Simple text chunking
        for chunk in chunks:
            processed_chunks_producer.produce(chunk)  # Send to Kafka
            vector = model.encode(chunk).tolist()
            
            # Insert into Milvus
            collection.insert([[chunk], [vector]])
            
            # Publish embedding to Kafka
            embedding_producer.produce(str(vector))
    
    stream.map(process_document)
    env.execute("Kafka-Flink-Embedding Pipeline")

if __name__ == "__main__":
    process_stream()

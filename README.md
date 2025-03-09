# RAG with Streaming VectorDB via Kafka and Flink

A Retrieval-Augmented Generation (RAG) system for financial stock market data integrating a streaming Pinecone vector database with Kafka and Flink for real-time data processing and retrieval.

## Start Kafka and Create Topic

``` bash
curl -OL https://downloads.apache.org/kafka/3.9.0/kafka_2.12-3.9.0.tgz
tar -xzf kafka_2.12-3.9.0.tgz
cd kafka_2.12-3.9.0
```

Kafka uses ZooKeeper, if you do not have Zookeeper running, you can start it using the following command:

```bash
./bin/zookeeper-server-start.sh config/zookeeper.properties
```

Start a Kafka broker by running the following command in a new terminal:

``` bash
./bin/kafka-server-start.sh config/server.properties
```

In another terminal, run the following command to create a Kafka topic called `flink-demo`:

``` bash
bin/kafka-topics.sh --create --topic flink-demo --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

If the topic `flink-demo` already exists, remove it first with the following command:
``` bash
bin/kafka-topics.sh --delete --topic flink-demo --bootstrap-server localhost:9092
```

## Build and Run the Application

In the project folder:

```
$ pip3 install requirements.txt
$ mvn clean package 
```

And run the Python embedding service:

```
$ python3 embedding_service.py
```

and Flink Consumer:

```
$ mvn exec:java -Dexec.mainClass=com.grallandco.demos.ReadFromKafka
```

and Producer: 

```
mvn exec:java -Dexec.mainClass=com.grallandco.demos.WriteToKafka
```

Finally, you can run the RAG that uses the evolving Pinecone vector database:
```
$ python3 rag_pinecone.py
```

or test the RAG that uses no context at all to compare performance:

```
$ python3 rag_no_data.py
```


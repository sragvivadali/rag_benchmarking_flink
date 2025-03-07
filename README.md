# Apache Flink and Apache Kafka

This project is use a simple Flink job to show how to integrate Apache Kafka to Flink using the Flink Connector for Kafka.


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

## Build and Run the Application

In the project folder:

```
$ mvn clean package 
```

And run the Python embedding service:

```
$ python3 embedding_service.py
```

And Flink Consumer:

```
$ mvn exec:java -Dexec.mainClass=com.grallandco.demos.ReadFromKafka
```

and Producer: 

```
mvn exec:java -Dexec.mainClass=com.grallandco.demos.WriteToKafka
```

and the RAG that uses the pinecone:

```
$ python3 rag_pinecone.py
```

or the RAG that uses no context at all:

```
$ python3 rag_no_data.py
```


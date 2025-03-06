# flink-kafka-docker-compose.

## Setup your flink & kafka cluster via docker compose

```
1. Flink Job Manager
2. Flink Task Manager
3. Kafka.
4. Zookeeper
```

## Prereqs

- [Install Docker for Windows](https://docs.docker.com/docker-for-windows/install/)
- [Test your Docker Installation](https://docs.docker.com/docker-for-windows/#test-your-installation)
- [Docker Compose already included in Docker Desktop for Windows]

## Run

- Cluster up

```
   Run docker compose with dispatch mode on compose file
   docker compose up -d
```

- Validate status of cluster

```
   Run:
   docker compose ps

   All the 4 service containers should be up and running
                  Name                                Command               State                   Ports
--------------------------------------------------------------------------------------------------------------------------
flink-kafka-docker-example_jobmanager_1    /docker-entrypoint.sh jobm ...   Up      6123/tcp, 0.0.0.0:8081->8081/tcp
flink-kafka-docker-example_kafka_1         start-kafka.sh                   Up      0.0.0.0:9094->9094/tcp
flink-kafka-docker-example_taskmanager_1   /docker-entrypoint.sh task ...   Up      6121/tcp, 6122/tcp, 6123/tcp, 8081/tcp
flink-kafka-docker-example_zookeeper_1     /bin/sh -c /usr/sbin/sshd  ...   Up      2181/tcp, 22/tcp, 2888/tcp, 3888/tcp
```

## Default ports used

```
Flink Web Client on port 8081-> http://localhost:8081/
JobManager RPC port 6123
TaskManagers RPC port 6122
TaskManagers Data port 6121
```

## Create a topic

```
docker exec $(docker ps -q --filter "name=kafka-1") kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic my-topic
```

## List existing topics

```
docker exec $(docker ps -q --filter "name=kafka-1") kafka-topics.sh --bootstrap-server localhost:9092 --list
```

## Push data to topics in interactive mode

```
docker exec -it $(docker ps -q --filter "name=kafka-1") kafka-console-producer.sh --broker-list localhost:9092 --topic my-topic
```

## Pull data from topics

```
docker exec $(docker ps -q --filter "name=kafka-1") kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic my-topic --from-beginning
```

## Copy app jar to flink job manager container or use flink UI to submit job

```
docker cp ./target/kafka-flink-job-1.0-SNAPSHOT.jar $(docker ps -q --filter "name=jobmanager-1"):/tmp/kafka-flink-job-1.0-SNAPSHOT.jar
```

## Run flink jobs or use flink UI to submit job

```
docker exec $(docker ps -q --filter "name=jobmanager-1") flink run -c com.ibm.wh.engagement.App /tmp/kafka-flink-job-1.0-SNAPSHOT.jar
```

## List running flink jobs

```
docker exec $(docker ps -q --filter "name=jobmanager-1") flink list
```

# Stage 1: Build the project
FROM maven:3.8.4-openjdk-11 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

# Stage 2: Run the Flink job
FROM flink:1.14.4-scala_2.12-java11
WORKDIR /opt/flink/app
COPY --from=build /app/target/flink-kafka-stock-processor-1.0-SNAPSHOT.jar /opt/flink/lib/
CMD ["jobmanager.sh", "start-foreground"]
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.common.typeinfo.TypeHint;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer;
import org.apache.flink.util.Collector;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Properties;

public class FlinkKafkaStockProcessor {

    public static void main(String[] args) throws Exception {
        // Set up Flink execution environment
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // Kafka properties
        Properties properties = new Properties();
        properties.setProperty("bootstrap.servers", "localhost:9092");
        properties.setProperty("group.id", "flink-group");

        // Kafka Consumer
        FlinkKafkaConsumer<String> kafkaConsumer = new FlinkKafkaConsumer<>(
                "new_documents",
                new SimpleStringSchema(),
                properties);

        // Data Stream: Read from Kafka
        DataStream<String> stockStream = env.addSource(kafkaConsumer);

        // Parse JSON and extract relevant stock information
        DataStream<Tuple3<String, Double, Double>> processedStockStream = stockStream
                .flatMap((String value, Collector<Tuple3<String, Double, Double>> out) -> {
                    ObjectMapper objectMapper = new ObjectMapper();
                    try {
                        JsonNode rootNode = objectMapper.readTree(value);
                        if (rootNode.isArray()) {
                            for (JsonNode stockNode : rootNode) {
                                String symbol = stockNode.get("code").asText();
                                double closePrice = stockNode.get("close").asDouble();
                                double changePercent = stockNode.get("change_p").asDouble();
                                out.collect(new Tuple3<>(symbol, closePrice, changePercent));
                            }
                        }
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }).returns(new TypeHint<Tuple3<String, Double, Double>>() {
                });

        // Print processed stock data to console
        processedStockStream.print();

        // Kafka Producer (Optional: Send processed data back to Kafka)
        FlinkKafkaProducer<String> kafkaProducer = new FlinkKafkaProducer<>(
                "processed_stock_data",
                new SimpleStringSchema(),
                properties);

        processedStockStream.map(tuple -> tuple.f0 + ": Close Price = " + tuple.f1 + ", Change% = " + tuple.f2)
                .addSink(kafkaProducer);

        // Execute the Flink job
        env.execute("Flink Kafka Stock Processor");
    }
}
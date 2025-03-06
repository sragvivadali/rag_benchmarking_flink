/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// package com.grallandco.demos;


// import org.apache.flink.api.common.functions.MapFunction;
// import org.apache.flink.streaming.api.datastream.DataStream;
// import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
// import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer09;
// import org.apache.flink.streaming.util.serialization.SimpleStringSchema;

// import java.util.Properties;

// public class ReadFromKafka {


//   public static void main(String[] args) throws Exception {
//     // create execution environment
//     StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

//     Properties properties = new Properties();
//     properties.setProperty("bootstrap.servers", "localhost:9092");
//     properties.setProperty("group.id", "flink_consumer");


//     DataStream<String> stream = env
//             .addSource(new FlinkKafkaConsumer09<>("flink-demo", new SimpleStringSchema(), properties));

//     stream.map(new MapFunction<String, String>() {
//       private static final long serialVersionUID = -6867736771747690202L;

//       @Override
//       public String map(String value) throws Exception {
//         return "Stream Value: " + value;
//       }
//     }).print();

//     env.execute();
//   }


// }

package com.grallandco.demos;

import org.apache.flink.api.common.functions.RichMapFunction;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer09;
import org.apache.flink.streaming.util.serialization.SimpleStringSchema;
import org.json.JSONObject;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Properties;

public class ReadFromKafka {

    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        Properties properties = new Properties();
        properties.setProperty("bootstrap.servers", "localhost:9092");
        properties.setProperty("group.id", "flink_consumer");

        DataStream<String> stream = env
                .addSource(new FlinkKafkaConsumer09<>("flink-demo", new SimpleStringSchema(), properties));

        stream.map(new EmbeddingFunction()).print();

        env.execute();
    }

    public static class EmbeddingFunction extends RichMapFunction<String, String> {
        @Override
        public String map(String value) throws Exception {
            return getEmbedding(value);
        }

        private String getEmbedding(String jsonString) {
            try {
                JSONObject jsonObject = new JSONObject(jsonString);
                String text = jsonObject.optString("text", "");

                URL url = new URL("http://localhost:8000/embed");
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Content-Type", "application/json");
                conn.setDoOutput(true);

                String requestBody = new JSONObject().put("text", text).toString();
                try (OutputStream os = conn.getOutputStream()) {
                    byte[] input = requestBody.getBytes(StandardCharsets.UTF_8);
                    os.write(input, 0, input.length);
                }

                if (conn.getResponseCode() != 200) {
                    return "Error calling embedding service";
                }

                try (InputStream is = conn.getInputStream();
                     BufferedReader reader = new BufferedReader(new InputStreamReader(is, StandardCharsets.UTF_8))) {
                    StringBuilder response = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        response.append(line);
                    }
                    return "Embedding: " + response.toString();
                }

            } catch (Exception e) {
                e.printStackTrace();
                return "Error generating embedding";
            }
        }
    }
}

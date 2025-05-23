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

package com.grallandco.demos;

import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.source.SourceFunction;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer09;
import org.apache.flink.streaming.util.serialization.SimpleStringSchema;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Properties;

public class WriteToKafka {

    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        Properties properties = new Properties();
        properties.setProperty("bootstrap.servers", "localhost:9092");

        DataStream<String> stream = env.addSource(new SimpleStringGenerator());
        stream.addSink(new FlinkKafkaProducer09<>("flink-demo", new SimpleStringSchema(), properties));

        env.execute("Stock Data Kafka Producer");
    }

    /**
     * Fetches stock data from EODHD API and produces it to Kafka.
     */
    public static class SimpleStringGenerator implements SourceFunction<String> {
        private static final long serialVersionUID = 1L;
        private volatile boolean running = true;
        private final String apiToken = "demo";
        private final String[] symbols = {"AAPL.US", "TSLA.US", "AMZN.US", "VTI.US"};

        @Override
        public void run(SourceContext<String> ctx) throws Exception {
            while (running) {
                for (String symbol : symbols) {
                    String stockData = fetchStockData(symbol);
                    System.out.println(stockData);
                    if (stockData != null) {
                        ctx.collect(stockData);
                    }
                }
                Thread.sleep(20000);
            }
        }

        @Override
        public void cancel() {
            running = false;
        }

        private String fetchStockData(String symbol) {
            try {
                String urlString = "https://eodhd.com/api/real-time/" + symbol + "?api_token=" + apiToken + "&fmt=json";
                URL url = new URL(urlString);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("GET");

                BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                StringBuilder response = new StringBuilder();
                String line;
                while ((line = in.readLine()) != null) {
                    response.append(line);
                }
                in.close();
                return response.toString();
            } catch (Exception e) {
                System.err.println("Error fetching stock data for " + symbol + ": " + e.getMessage());
                return null;
            }
        }
    }
}
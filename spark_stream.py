from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, IntegerType

spark = (SparkSession.builder
         .appName("Kafka to Cassandra Streaming")
         .config("spark.jars.packages", 
                 "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,"
                 "com.datastax.spark:spark-cassandra-connector_2.12:3.4.1,"
                 "com.github.jnr:jnr-posix:3.1.16")  # Fix for JNR issue
         .config("spark.cassandra.connection.host", "cassandra")
         .getOrCreate())

# Define the schema of incoming Kafka messages
kafka_schema = StructType().add("id", IntegerType()).add("name", StringType()).add("value", IntegerType())

# Read from Kafka
kafka_df = (spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", "broker:29092")
            .option("subscribe", "test-topic")
            .option("startingOffsets", "earliest")
            .load()
            .selectExpr("CAST(value AS STRING) AS json"))

# Parse JSON messages
parsed_df = (kafka_df
             .select(from_json(col("json"), kafka_schema).alias("data"))
             .select("data.*"))

# Define the batch write function
def write_to_cassandra(batch_df, _):
    (batch_df.write
     .format("org.apache.spark.sql.cassandra")
     .mode("append")
     .options(keyspace="spark_demo", table="events")
     .save())

# Use foreachBatch to write to Cassandra
query = (parsed_df.writeStream
         .foreachBatch(write_to_cassandra)
         .option("checkpointLocation", "/tmp/checkpoints/kafka_cassandra")
         .start())

query.awaitTermination()

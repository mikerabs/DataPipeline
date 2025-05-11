from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.sql.functions import from_json, col
import logging

def get_spark():
    return SparkSession.builder \
        .appName("SparkKafkaToCassandra") \
        .config("spark.jars.packages",
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,"
                "com.datastax.spark:spark-cassandra-connector_2.12:3.4.1") \
        .config("spark.cassandra.connection.host", "cassandra") \
        .getOrCreate()

def main():
    spark = get_spark()
    spark.sparkContext.setLogLevel("ERROR")

    # Read from Kafka
    raw_df = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "broker:29092") \
        .option("subscribe", "users_created") \
        .option("startingOffsets", "earliest") \
        .load()

    # Parse JSON value
    schema = StructType([
        StructField("first_name", StringType()),
        StructField("last_name",  StringType()),
        StructField("email",      StringType()),
    ])
    parsed = raw_df.selectExpr("CAST(value AS STRING) as json_str") \
        .select(from_json(col("json_str"), schema).alias("data")) \
        .select("data.*")

    # Write to Cassandra
    query = parsed.writeStream \
        .format("org.apache.spark.sql.cassandra") \
        .option("checkpointLocation", "/tmp/checkpoint") \
        .option("keyspace", "spark_streams") \
        .option("table", "created_users") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()


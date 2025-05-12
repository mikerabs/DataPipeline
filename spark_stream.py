# ─────────────────────────────────────────────────────────────────────────────
#  spark_stream.py   –   Kafka → Cassandra streaming
#                       topic : users_created
#                       table : spark_demo.users_created
#                       PK    : email  (text, NOT NULL)
# ─────────────────────────────────────────────────────────────────────────────

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType

# ── 1. Spark session ────────────────────────────────────────────────────────
spark = (
    SparkSession.builder
        .appName("Kafka → Cassandra : users_created")
        .config(
            "spark.jars.packages",
            ",".join([
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1",
                "com.datastax.spark:spark-cassandra-connector_2.12:3.4.1",
                "com.github.jnr:jnr-posix:3.1.16"
            ])
        )
        .config("spark.cassandra.connection.host", "cassandra")
        .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

# ── 2. Schema that exactly matches the JSON payload ─────────────────────────
kafka_schema = (
    StructType()
        .add("first_name", StringType())
        .add("last_name",  StringType())
        .add("email",      StringType(), nullable=False)   # PK ⇒ NOT NULL
)

# ── 3. Read & parse Kafka JSON messages ─────────────────────────────────────
kafka_df = (
    spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "broker:29092")
        .option("subscribe", "users_created")
        # Use "earliest" while you’re re‑testing; switch to "latest" in prod
        .option("startingOffsets", "earliest")
        .load()
        .selectExpr("CAST(value AS STRING) AS json")
)

parsed_df = (
    kafka_df
        .select(from_json(col("json"), kafka_schema).alias("data"))
        .select("data.*")
        .filter(col("email").isNotNull())        # safety for the PK
)

# ── 4. Write each micro‑batch to Cassandra ──────────────────────────────────
def write_to_cassandra(batch_df, _epoch_id):
    (
        batch_df.write
            .format("org.apache.spark.sql.cassandra")
            .mode("append")
            .options(keyspace="spark_demo", table="users_created")
            .save()
    )

query = (
    parsed_df.writeStream
        .foreachBatch(write_to_cassandra)
        .option("checkpointLocation", "/opt/bitnami/spark/checkpoints/users_created")
        .start()
)

print("🚀  Streaming query RUNNING — waiting for messages on topic ‘users_created’ …")
query.awaitTermination()

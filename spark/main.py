import os
import geoip2.database
from user_agents import parse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, udf
from pyspark.sql.types import (StructType,
                               StructField,
                               StringType,
                               IntegerType,
                               MapType)

GEO = os.getenv('GEO')

def parse_user_agent(user_agent):
    ua = parse(user_agent)
    return ua.browser.family+' '+ua.browser.version_string, ua.os.family+' '+ua.os.version_string, ua.device.family, ua.device.brand, ua.device.model

def get_country(ip_address):
    reader = geoip2.database.Reader(GEO)
    try:
        response = reader.country(ip_address)
        country = response.country.name
    except geoip2.errors.AddressNotFoundError:
        country = None
    reader.close()
    return country

spark = SparkSession\
        .builder \
        .appName("Clickstream_spark") \
        .config("spark.streaming.stopGracefullyOnShutdown", True) \
        .config('spark.jars.packages',
                'org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.3,'
                'com.github.housepower:clickhouse-spark-runtime-3.4_2.12:0.7.1,'
                'com.github.housepower:clickhouse-native-jdbc-shaded:2.5.3'
                ) \
        .config('spark.sql.shuffle.partitions', os.getenv('PARTITIONS')) \
        .master("spark://spark-master:7077") \
        .getOrCreate()


scm = StructType([
    StructField("ip", StringType(), False),
    StructField("user_id", IntegerType(), False),
    StructField("user_agent", StringType(), False),
    StructField("session_id", StringType(), False),
    StructField("event_time", StringType(), False),
    StructField("event_name", StringType(), False),
    StructField("channel", StringType(), False),
    StructField("metadata", MapType(StringType(), StringType()), True)
])

device_schema = StructType([
    StructField("browser", StringType(), True),
    StructField("os", StringType(), True),
    StructField("family", StringType(), True),
    StructField("brand", StringType(), True),
    StructField("model", StringType(), True)
])

get_country_udf = udf(get_country, StringType())

device_udf = udf(parse_user_agent, device_schema)

stream_data = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", os.getenv('BROKER')) \
    .option("subscribe", os.getenv('TOPIC_NAME')) \
    .option("startingOffsets", "earliest") \
    .load()

df = stream_data.selectExpr("CAST(value AS STRING) as json_value") \
    .withColumn("data", from_json(col("json_value"), scm)) \
    .select("data.*")

df = df.withColumn("event_time", to_timestamp(col("event_time"), "dd/MM/yyyy HH:mm:ss.SSSSSS")) \
    .withColumn("temp", device_udf(df.user_agent)) \
    .withColumn("browser", col("temp").browser) \
    .withColumn("os", col("temp").os) \
    .withColumn("family", col("temp").family) \
    .withColumn("brand", col("temp").brand) \
    .withColumn("model", col("temp").model) \
    .withColumn("country", get_country_udf(df.ip)) \
    .withColumn("query", col("metadata").query) \
    .drop("temp") \
    .drop("metadata") \
    .drop("user_agent")
    
#These are the extra columns umcomment if you want to add them
    # .withColumn("pid", col("metadata").product_id) \
    # .withColumn("quantity", col("metadata").quantity) \
    # .withColumn("sold", col("metadata").cart_items) \
    # .withColumn("total_price", col("metadata").total_amount) \

# NULL values gave error while serializing to insert in clickhouse
# so replaceing NULL with blank
df = df.na.fill('')

clickopt = {
    'url':os.getenv('DB_URL'),
    'user':os.getenv('DB_USER'),
    'password':os.getenv('DB_PASSWORD'),
    'driver':'com.github.housepower.jdbc.ClickHouseDriver'
}


#IF you want to print to console
# query = df.writeStream \
#     .outputMode("append") \
#     .format("console") \
#     .option("truncate", False) \
#     .start()

query = df.writeStream \
    .foreachBatch(lambda batch_df, batch_id: batch_df.write \
                    .format("jdbc") \
                    .options(**clickopt) \
                    .option("dbtable", os.getenv('DB_TABLE')) \
                    .mode("append") \
                    .save()
                ) \
    .start()

query.awaitTermination()
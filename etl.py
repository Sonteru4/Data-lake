import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, monotonically_increasing_id
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format, dayofweek
from pyspark.sql.types import *

config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID'] = config['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY'] = config['AWS_SECRET_ACCESS_KEY']


def create_spark_session():
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    """
    Description:
        Process the songs data files and create extract songs table and artist table data from it.

    :param spark: a spark session instance
    :param input_data: input file path
    :param output_data: output file path
    """

    # get filepath to song data file
    song_data = input_data + "song_data/*/*/*/*"

    # read song data file
    df = spark.read.json(song_data, mode='PERMISSIVE', columnNameOfCorruptRecord='corrupt_record').drop_duplicates()

    # extract columns to create songs table
    songs_table = df.select("song_id","title","artist_id","year","duration").drop_duplicates()

    # write songs table to parquet files partitioned by year and artist
    songs_table.write.parquet(output_data + "songs/", mode="overwrite", partitionBy=["year","artist_id"])

    # extract columns to create artists table
    artists_table = df.select("artist_id","artist_name","artist_location","artist_latitude","artist_longitude").drop_duplicates()

    # write artists table to parquet files
    artists_table.write.parquet(output_data + "artists/", mode="overwrite")


def process_log_data(spark, input_data, output_data):
    """
    Description:
            Process the event log file and extract data for table time, users and songplays from it.

    :param spark: a spark session instance
    :param input_data: input file path
    :param output_data: output file path
    """

    # get filepath to log data file
    log_data = os.path.join(input_data, "log-data/")

    # read log data file
    df = spark.read.json(log_data, mode='PERMISSIVE', columnNameOfCorruptRecord='corrupt_record').drop_duplicates()

    # filter by actions for song plays
    df = df.filter(df.page == "NextSong")

    
def main():
    spark = create_spark_session()
    input_data = "s3://udacity-spark-project/"
    output_data = "s3://udacity-spark-project/output/"

    process_song_data(spark, input_data, output_data)
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()

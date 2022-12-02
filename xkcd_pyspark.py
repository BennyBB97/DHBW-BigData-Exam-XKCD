import pyspark
from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql.functions import col

if __name__ == '__main__':
    """
    Main Function
    """
    # Initialize Spark Context
    sc = pyspark.SparkContext()
    spark = SparkSession(sc)

    #Build spark session with mysql JDBC Driver
    spark = SparkSession.builder.config("spark.jars", "home/spark/jars/mysql-connector-j-8.0.31.jar") \
        .master("local").appName("Bigdata XKCD Comis").getOrCreate()

    #Read all HDFS json files in raw
    xkcd = spark.read.format('json')\
        .options(header='true', nullValue='null', inferschema='true')\
        .load('/user/hadoop/xkcd/raw/*/*.json')

    #Select col
    xkcd = xkcd.select(col("alt"),col("img"), col("num"), col("safe_title"), col("title"))

    #Write reduced dataframe to MySql
    xkcd.write.format('jdbc').options(
        url='jdbc:mysql://172.18.0.4:3306/bigdata',
        driver='com.mysql.cj.jdbc.Driver',
        dbtable='xkcd_comics',
        user="xkcd",
        password="4dmin").mode('overwrite').save()
        
    # Write data to HDFS Final
    xkcd.write.format('csv').\
            mode('overwrite').\
            save('/user/hadoop/xkcd/final')

---
layout: xdrive-documentation-page

description: Xdrive
title: Xdrive - Kafka Plugin
keywords: Xdrive Kafka Plugin

headline: Deepgreen DB Kafka Plugin

scroll: true

---

## Deepgreen-Kafka Integration

### Overview of the Deepgreen-Kafka Integration

Deepgreen-Kafak Integration provide high speed, parallel data transfer between Deepgreen
Database and Apache Kafka to support a streaming ETL pipeline.

The Deepgreen-Kafka Integration includes the dgkafka utility.

### Loading Kafka Data into Deepgreen

1. [Identify the format of the data source in Kafka](#datasource)
1. [Setup the mountpoint of Xdrive Kafka plugins](#mountpoint)
1. [Create topic in Kafka](#kafkatopic)
1. [Construct Configuration file dgkafka.toml](#configfile)
1. [Run the dgkafka setup command to setup the environment of the dgkafka](#dgkafkasetup)
1. [Create target Deepgreen Database table](#createtable)
1. [Run the dgkafka load command to load the data from Kafka](#dgkafkaload)
1. [Run the dgkafka check command to check the progress of the loading](#dgkafkacheck)
1. [Load CSV data from file to Kafka](#loadcsv)
1. [Write Data into Kafka](#writedata)


### More settings
1. [Configuration file dgkafka.toml](#configspec)
1. [About Transforming and Mapping Kafka Input Data](#jsontransform)
1. [SSL Configuration](#sslconfig)
1. [Troubleshooting](#troubleshoot)

---

#### <a name="datasource"></a>Identify the format of the data source in Kafka

Dgkafka supports Kafka message value data in following formats. 

|Format  | Description |
|------  | ---------   |
| csv    | Comma-delimited text format data  |
| json   | JSON-format data. dgkafka reads JSON data from Kafka only as a single column  |
| binary | binary-format data. dgkafka read binary data from Kafka only as bytea type single column |

To write Kafka data into a Deepgreen Database table, you must identify the data format in the
load configuration file.

##### CSV
Sample of CSV file

```
1|Customer#000000001|IVhzIApeRb ot,c,E|15|25-989-741-2988|711.56|BUILDING|to the even, regular platelets. regular, ironic epitaphs nag e
2|Customer#000000002|XSTf4,NCwDVaWNe6tEgvwfmRchLXak|13|23-768-687-3665|121.65|AUTOMOBILE|l accounts. blithely ironic theodolites integrate boldly: caref
3|Customer#000000003|MG9kdTD2WBHm|1|11-719-748-3364|7498.12|AUTOMOBILE| deposits eat slyly ironic, even instructions. express foxes detect slyly. blithely even accounts abov
4|Customer#000000004|XxVSJsLAGtn|4|14-128-190-5944|2866.83|MACHINERY| requests. final, regular ideas sleep final accou
5|Customer#000000005|KvpyuHCplrB84WgAiGV6sYpZq7Tj|3|13-750-942-6364|794.47|HOUSEHOLD|n accounts will have to unwind. foxes cajole accor
6|Customer#000000006|sKZz0CsnMD7mp4Xd0YrBvx,LREYKUWAh yVn|20|30-114-968-4951|7638.57|AUTOMOBILE|tions. even deposits boost according to the slyly bold packages. final accounts cajole requests. furious
```

---

##### JSON

Specify the json format when your Kafka message data is in JSON format.  dgkafka reads JSON data from Kafka only as a single column.
You must define a mapping if you want dgkafka to write the data into specific columns in the target Deepgreen Database table.

Sample JSON message data:
```
 {"custkey":111, "name": "eric", "address":"addr", "nationkey":2,"phone":"2345","acctbal":2.0, "mktsegment":"marketing","comment":"com
 {"custkey":222, "name": "peter", "address":"addr", "nationkey":2,"phone":"2345","acctbal":2.0, "mktsegment":"marketing","comment":"com
 {"custkey":333, "name": "john", "address":"addr", "nationkey":2,"phone":"2345","acctbal":2.0, "mktsegment":"marketing","comment":"com
ment"}
```

---

#### <a name="mountpoint"></a>Setup the mountpoint of Xdrive Kafka Plugins

The Kafka Plugin can read/write between Deepgreen DB and Kafka.  CSV or JSON data format can be used as
communication protocol.

The Kafka Plugin consists of one executable dgkafka and two xdrive plugins xdr_kafka and xdr_kafkaoffset.  The xdrive 
plugins are used together with dgkafka in order to support read/write between Kafka and Deepgreen from multiple
data segments in parallel.

We are using [librdkafka](https://github.com/edenhill/librdkafka) for Kafka client connection so
you may check out the client SSL configuration details
[here](https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md).

##### Mountpoint of xdr_kafka

xdr_kafka plugin is for reading and writing from/to the Kafka.  It supports new Kafka streaming APIs.

```
[[xdrive.mount]]
name = "kafka"
argv = ["xdr_kafka/xdr_kafka", "kafkahost1:9092,kafkahost2:9092"]

# arg1 - list of kafka brokers hostname

```

For SSL support, you can use -X key=value pair to supply SSL configurations in the command line argument.

```
[[xdrive.mount]]
name = "kafka"
argv = ["xdr_kafka/xdr_kafka", 
     "-X", "security.protocol=SSL",
     "-X", "ssl.key.location=/var/config/kafka/ca-key",
     "-X", "ssl.key.password=kafka123",
     "-X", "ssl.certificate.location=/var/config/kafka/ca-cert",
     "-X", "ssl.ca.location=/var/config/kafka/ca-cert",
     "kafkahost1:9092,kafkahost2:9092"]

# arg1 - list of kafka brokers hostname

```


##### Mountpoint of xdr_kafkaoffset

xdr_kafkaoffset plugin is used to get the committed offset of a consumergroup and topic.  It is used 
for offset management in Deepgreen.

```
[[xdrive.mount]]
name = "kafkaoffset"
argv = ["xdr_kafkaoffset/xdr_kafkaoffset", "kafkahost1:9092,kafkahost2:9092"]

# arg1 - list of kafka brokers hostname

```

For SSL support, you can use -X key=value pair to supply SSL configuration in the command line argument.

You can refer to the document [here](https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md)

```
[[xdrive.mount]]
name = "kafkaoffset"
argv = ["xdr_kafkaoffset/xdr_kafkaoffset",
     "-X", "security.protocol=SSL",
     "-X", "ssl.key.location=/var/config/kafka/ca-key",
     "-X", "ssl.key.password=kafka123",
     "-X", "ssl.certificate.location=/var/config/kafka/ca-cert",
     "-X", "ssl.ca.location=/var/config/kafka/ca-cert",
     "kafkahost1:9092,kafkahost2:9092"]

# arg1 - list of kafka brokers hostname

```

---

#### <a name="kafkatopic"></a>Create topic in Kafka

Try out this link to start [Kafka](https://kafka.apache.org/quickstart)

Create a topic customer with 3 partitions in Kafka,

```
% bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 3 --topic customer
```

---

#### <a name="configfile"></a>Construct Configuration file dgkafka.toml

First, create the configuration file in toml format,

```
[dgkafka]
database = "template1"
user = "ericlam"
password = ""
host = "localhost"
port = 5432
sslmode = "disable"
xdrive_host = "localhost"
xdrive_port = 7171
xdrive_offset_endpoint = "kafkaoffset"
xdrive_kafka_endpoint = "kafka"

[kafka]
  [kafka.input]
  format = "csv"
  delimiter = "|"
  consumer_group = "dggrp"
  topic = "customer"
  partition_num = 3
  nwriter = 2
  ext_read_table = "customer_kafka_read"
  ext_write_table = "customer_kafka_write"
  ext_offset_table = "kafka_offset"

    [[kafka.input.columns]]
    name = "c_custkey"
    type = "integer"

    [[kafka.input.columns]]
    name = "c_name"
    type = "varchar(25)"

    [[kafka.input.columns]]
    name = "c_address"
    type = "varchar(40)"
    ignored = false

    [[kafka.input.columns]]
    name = "c_nationkey"
    type = "integer"

    [[kafka.input.columns]]
    name = "c_phone"
    type = "varchar(15)"

    [[kafka.input.columns]]
    name = "c_acctbal"
    type = "double precision"

    [[kafka.input.columns]]
    name = "c_mktsegment"
    type = "varchar(10)"

    [[kafka.input.columns]]
    name = "c_comment"
    type = "varchar(117)"

  [kafka.output]
  offset_table = "kafka_offset_summary"
  output_table = "customer"

  [kafka.commit]
  max_row = 10000
  minimal_interval = -1
```

---

#### Dgkafka commands

Dgkafka is an executable to load the data from Kafka together with xdrive plugins xdr_kafka and xdr_kafkaoffset.  The dgkafka executable file
is located in ```$XDRIVE_HOME/plugin/dgkafka/dgkafka```.

dgkafka has three commands

* dgkafka setup - setup tables for offset management
* dgkafka load - load Kafak data into Deepgreen
* dgkafka check - check the offset of kafka and last recorded offset in Deepgreen


---

#### <a name="dgkafkasetup"></a>Running the dgkafka setup Command


```bash
% dgkafka setup dgkafka.toml
```

After running the setup, table ```kafka.input.ext_read_table```, ```kafka.input.ext_write_table ```, the offset tables ```kafka.input.ext_offset_table``` and ```kafka.output.offset_table``` defined in configuration file will be created.

---

#### <a name="createtable"></a>Create Output Table

You must pre-create the Deepgreen output table before you load Kafka data into Deepgreen Database.

```bash
drop table if exists customer;
create table customer (c_custkey integer, 
                        c_name varchar(25), 
                        c_address varchar(40),
                        c_nationkey integer,
                        c_phone varchar(15),
                        c_acctbal double precision,
                        c_mktsegment varchar(10),
                        c_comment varchar(117));

```

---

#### <a name="dgkafkaload"></a>Running the dgkafka load Command

You run dgkafka command to load Kafka data to Deepgreen.  When you run the command, you
provide the name of the configuration file that defines the parameters of the load operation.
For example,

```bash
% dgkafka load [-quit-at-eof] [{-force-reset-earliest | -force-reset-latest}] [-v] dgkafka.toml
```

The default mode of operation for dgkafka load is to read all pending messages and then to
wait for, and then consume new Kafka messages.  When running in this mode, dgkafka load waits
indefinitely, you can interrupt and exit the command with Control-C.

To run the command in batch mode, you provide the -quite-at-eof option.  In this mode,
dgkafka load exits when there are no new messages in the kafka stream.

dgkafka load resumes a subsquent data load operation specifying the same Kafka topic, consumer group and 
target Deepgreen Database table names from the last recorded offset.

You can also reset the offset by the option ```-force-reset-earliest``` and ```-force-reset-latest```.  ```-force-reset-earliest```
will reset the offset to the beginning offset.  ```-force-reset-latest``` will only wait for the future Kafka messages.

```bash
% dgkafka load -quit-at-eof dgkafka.toml
```

---

#### <a name="dgkafkacheck"></a>Running the dgkafka check Command

You run the dgkafka check command to check the offset in Kafka and recorded offset in Deepgreen.  If you want to see all history, 
you can check the table ```kafka.output.offset_table``` (defined in configuration file) in Deepgreen.

```bash
% dgkafka check dgkafka.toml
Database = template1, Topic = customer, Group = dggrp

[Last recorded offset]
Group	Topic	      Partition	 Committed	    Latest	               Start	                 End
dggrp	customer	    0	    144211	    144211	2019-05-17 03:45:02.646998 +0000 +0000	2019-05-17 03:45:05 +0000 +0000
dggrp	customer	    1	    143409	    143409	2019-05-17 03:45:02.646998 +0000 +0000	2019-05-17 03:45:05 +0000 +0000
dggrp	customer	    2	    144713	    144713	2019-05-17 03:45:02.646998 +0000 +0000	2019-05-17 03:45:05 +0000 +0000
dggrp	customer	    3	    143699	    143699	2019-05-17 03:45:02.646998 +0000 +0000	2019-05-17 03:45:05 +0000 +0000

[Offset from Kafka]
Group	Topic	      Partition	 Committed	    Latest	           Timestamp
dggrp	customer	    0	    144211	    144211	2019-05-17 04:28:35 +0000 +0000
dggrp	customer	    1	    143409	    143409	2019-05-17 04:28:35 +0000 +0000
dggrp	customer	    2	    144713	    144713	2019-05-17 04:28:35 +0000 +0000
dggrp	customer	    3	    143699	    143699	2019-05-17 04:28:35 +0000 +0000
```

<!--

#### Kafka Offset Table

Create the Kafka offset table with the data type in exact order.  Only one offset table should be
created for multiple Kafka external tables per database.

```
DROP EXTERNAL TABLE IF EXISTS kafka_offset;
CREATE EXTERNAL TABLE kafka_offset (consumer_group text,
                      topic text,
                      partition_number integer,
                      committed_offset bigint,
                      ts timestamp)
LOCATION ('xdrive://XDRIVE-HOST-PORT/kafkaoffset/')
FORMAT 'SPQ';
```

#### Usage of xdr_kafka plugin

The xdr_kafka plugin is used for read/write between Kafka and Deepgreen.  The plugin will return results when it received
the requested number of records (limit) or timeout.

You may run the SELECT statment with parameters inside ```dg_utils.xdrive_query```.

To read data from Kafka,

```
SQL> select * from kafka_r where dg_utils.xdrive_query($$group=dggrp&start=500,500,500&limit=100$$);
```


* ```group``` is the name of consumer group (Mandatory)
* ```start``` is the partition offset to start with (Comma as separator between offsets).  Possible values are 
natural number, earliest = -2, latest = -1. If start is not provided.  The default offset is latest (-1). (Optional)
* ```timeout``` is the timeout value in second. The default value is -1 second which means plugin
will exit as long as no message received. (Optional)
* ```limit``` is the limit of records received. The default value is 1000 records (Optional)


To write data to Kafka, run an INSERT statement to write data to Kafka.

```
SQL> insert into customer_kafka_w values (1, 'eric', 1.0);
```

#### Usage of xdr_kafkaoffset plugin

The xdr_kafkaoffset plugin is used for getting the committed offset from Kafka.

To get committed offset and latest offset from Kafka, run SELECT statment with parameters inside ```dg_utils.xdrive_query```.

```
SQL> select * from kafkaoffset_r where dg_utils.xdrive_query($$group=dggrp&topic=test$$);

consumer_group | topic | partition_number | committed_offset | latest_offset |         ts 
         
----------------+-------+------------------+------------------+---------------+------------
---------
 dggrp          | test  |                0 |            -1001 |           319 | 2018-10-10 
02:24:32
 dggrp          | test  |                1 |            -1001 |           335 | 2018-10-10 
02:24:32
 dggrp          | test  |                2 |            -1001 |           346 | 2018-10-10 
02:24:32
(3 rows)

```

* ```group``` is the name of consumer group (Mandatory)
* ```topic``` is the name of the topic (Mandatory)

-->

---

#### <a name="loadcsv"></a>Load CSV data from file to Kafka

You may use the provided executable ```$XDRIVE_HOME/plugin/csv2kafka/csv2kafka``` to upload the csv file to kafka by running the command

```bash
csv2kafka -d delimiterForRead -w delimiterForWrite -X key1=value1 -X key2=value2 kafkahost1,kafkahost2,...,kafkahostN topic csvfile
```

To support SSL,

```bash
% csv2kafka -d "|" -w "|" -X security.protocol=SSL
-X ssl.key.location=/home/dg/config/kafka/ca-key
-X ssl.key.password=kafka123
-X ssl.certificate.location=/home/dg/config/kafka/ca-cert
-X ssl.ca.location=/home/dg/config/kafka/ca-cert  localhost:9092 topic data.csv
```

---

#### <a name="writedata"></a>Write Data to Kafka

Simply run a INSERT SQL statement into the external writable table ```kafka.input.ext_write_table``` defined
in dgkafka.toml.  The columns of the table may vary depending on the format of the data.

For CSV, the columns will be the same as the definition in ```kafka.input.columns```.

```
INSERT INTO ext_write_table VALUES (col0, col1, ..., colN);
```

For JSON, a single column with name ```jdata``` and ```json``` type is defined in the table.  You have to
insert data in JSON format.

```
INSERT INTO ext_write_table VALUES ('{"name": "apple"}');
```

---

#### <a name="configspec"></a>Configuration File dgkafka.toml

```
[dgkafka]
database = "db_name"
user = "user_name'
password = "password"
host = "host"
port = deepgreen_port
sslmode = "disable"
xdrive_host = "xdrive_host"
xdrive_port = xdrive_port
xdrive_offset_endpoint = "xdr_kafkaoffset_mountpoint"
xdrive_kafka_endpoint = "xdr_kafka_mountpoint"

[kafka]
  [kafka.input]
  format = "data_format"
  delimiter = "delimiter_string"
  consumer_group = "kafka_consumer_group"
  topic = "kafka_topic"
  partition_num = kafka_topic_partition_number
  nwriter = number_of_xdrive_writer
  ext_read_table = "external_kafka_read_table_name"
  ext_write_table = "external_kafka_write_table_name"
  ext_offset_table = "external_kafka_offset_table_name"

   [
    [[kafka.input.columns]]
    name = "column_name"
    type = "column_data_type"
    ignored = [true | false]

    [...]]

  [kafka.output]
  offset_table = "output_kafka_offset_table_name"
  output_table = "output_table_name"

  [
   [[kafka.output.mappings]]
    name = "target_column_name"
    key = "{source_column_name | 'expression' }"

    [...]]

  [kafka.commit]
  max_row = num_rows
  minimal_interval = wait_time
```




The description of the parameters are:
```
* dgkafka.database - The name of the database to connect to
* dgkafka.user - The user to sign in as
* dgkafka.password - The user's password
* dgkafka.host - The host to connect to. Values that start with / are for unix
  domain sockets. (default is localhost)
* dgkafka.port - The port to bind to. (default is 5432)
* dgkafka.sslmode - Whether or not to use SSL (default is require, this is not
  the default for libpq)
* dgkafka.connect_timeout - Maximum wait for connection, in seconds. Zero or
  not specified means wait indefinitely.
* dgkafka.sslcert - Cert file location. The file must contain PEM encoded data.
* dgkafka.sslkey - Key file location. The file must contain PEM encoded data.
* dgkafka.sslrootcert - The location of the root certificate file. The file
  must contain PEM encoded data.
* dgkafka.xdrive_host - xdrive hostname
* dgkafka.xdrive_port - xdrive server port number
* dgkafka.xdrive_offset_endpoint - the name of offset endpoint defined in xdrive.toml
* dgkafka.xdrive_kafka_endpoint - the name of kafka endpoint defined in xdrive.toml
* kafka.input.format - csv or json
* kafka.input.delimiter - csv delimiter
* kafka.input.consumer_group - the name of consumer group.
* kafka.input.topic - topic in Kafka
* kafka.input.partition_num - partition number of the topic.  It MUST match with Kafka.
* kafka.input.nwriter - number of segments that write data to Kafka
* kafka.input.ext_read_table - external read-only table name
* kafka.input.ext_write_table - external writable table name
* kafka.input.ext_offset_table - external table for offset endpoint
* kafka.input.columns - columns of the data in correct order with Kafka data structure
* kafka.output.offset_table - output table for offset history
* kafka.output.output_table - target output table for data loading
* kafka.output.mappings - mapping of the json object
* kafka.commit.max_row is the maximum number of row for each poll.  The default value is 1000.
* kafka.commit.minimal_interval is the number of second wait for in each poll. The default value is -1 which means it will not wait
for new data as long as no message in the queue.
```

Valid values for dgkafka.sslmode are:

```
* disable - No SSL
* require - Always SSL (skip verification)
* verify-ca - Always SSL (verify that the certificate presented by the
  server was signed by a trusted CA)
* verify-full - Always SSL (verify that the certification presented by
  the server was signed by a trusted CA and the server host name
  matches the one in the certificate)
```

---

#### <a name="jsontransform"></a>About Transforming and Mapping Kafka Input Data

You can use a ```kafka.output.mappings``` to asign a value expression to a target table column.  The
expression must be one that you could specify in the SELECT list of a query, and can include a
contant value, a column reference, an operator invocation, a built-in or user-defined function call,
and so forth.

If you choose to map more than one input column in an expression, you can create a user-defined 
function to parse and transform the input column and return the columns of the interest.

For example, suppose a Kafka producer emits the following JSON messages to a topic:

```
{ "customer_id": 1313131, "some_intfield": 12 }
{ "customer_id": 77, "some_intfield": 7 }
{ "customer_id": 1234, "some_intfield": 56 }
```

You could define a user-defined function, udf_parse_json(), to parse the data as follows:

```
=> CREATE OR REPLACE FUNCTION udf_parse_json(value json)
     RETURNS TABLE (x int, y text)
   LANGUAGE plpgsql AS $$
     BEGIN
        RETURN query
        SELECT ((value->>'customer_id')::int), ((value->>'some_intfield')::text);
     END $$;
```
This function returns the two fields in each JSON record, casting the fields to integer and text, respectively.

An example ```kafka.output.mappings``` for the topic data in a JSON-type ```kafka.input.columns``` named ```jdata``` follows:

```
[[kafka.output.mappings]]
  name= "cust_id"
  key = "(jdata->>'customer_id')"
[[kafka.output.mappings]]
  name= "field2"
  key =  "((jdata->>'some_intfield') * .075)::decimal"
[[kafka.output.mappings]]
  name= "j1, j2"
  key= "(udf_parse_json(jdata)).*"
```

The Deepgreen Database table definition for this example scenario is:
```
=> CREATE TABLE t1map( cust_id int, field2 decimal(7,2), j1 int, j2 text );
```

---

#### <a name="sslconfig"></a>Kafka SSL Configuration

We are using [librdkafka](https://github.com/edenhill/librdkafka) for Kafka client connection so
you may check out the SSL configuration details
[here](https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md).  For setting up SSL
server authentication, please refer to the [document](https://docs.confluent.io/current/kafka/authentication_ssl.html).


Example of Kafka broker configuration ```server.properties```

```
listeners=SSL://:9092
security.inter.broker.protocol=SSL
ssl.client.auth=required
ssl.truststore.location=/home/dg/config/kafka/kafka.server.truststore.jks
ssl.truststore.password=kafka123
ssl.keystore.location=/home/dg/config/kafka//kafka.server.keystore.jks
ssl.keystore.password=kafka123
ssl.key.password=kafka123
```

Example of Kafka consumer and producer configuration ```consumer.properties``` and ```producer.properties```

```
security.protocol=SSL
ssl.truststore.location=/home/dg/config/kafka/kafka.client.truststore.jks
ssl.truststore.password=kafka123

ssl.keystore.location=/home/dg/config/kafka/kafka.server.keystore.jks
ssl.keystore.password=kafka123
ssl.key.password=kafka123
```

---

#### <a name="troubleshoot"></a>Consumer not receiving any messages?

<!--
By default, initial offsets is set to lastest offset.  This means that in the event that a
brand new consumer group is created, and it has never commited any offsets to kafka, it will
only receive messages starting from the message after the current one that was written.

If you wish to receive all messages (from the start of all messages in the topic) in the event
that a consumer does not have any offsets commited to kafka, you need to set initial offsets to earliest.

```
SELECT * from topic where dg_utils.xdrive_query($$initial_offsets=earliest$$);
```

Subsequence SELECT call will fetch the data from the last offset saved in kafka.

-->

By default, initial offsets is set to earliest offset.  If you want to start over again, you have to reset the offsets with 
the ```bin/kafka-consumer-groups.sh``` command.

```bash
% bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group dggrp --topic test --reset-offsets  --to-earliest --execute
```

to review the result of offsets reset without executing,

```bash

% bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group dggrp --topic test --reset-offsets  --to-earliest
```

To describe the status of the consumer group,

```bash
% bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 -describe -group dggrp
```


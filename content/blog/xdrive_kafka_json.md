---
#layout: post

date: "2019-06-25"

author: Eric Lam

categories: ["xdrive", "kafka"]

title: Parallel data transfer between Deepgreen and Kafka (Data in JSON format)
description: "Example of xdrive kafka plugin to transfer data between deepgreen and Kafka"
keywords: Kafka, Xdrive, JSON

headline: Blog
subheadline:
type: "post"

---

Today, we will talk about how to transfer the data in JSON format from Kafka to Deepgreen. It reads the data 
from Kafka partitions simultaneously via Xdrive plugins and transfer the data to Deepgreen DB table.

We will show you how to setup the configurations and read the JSON data from Kafka today.

<!--more-->

---

__1.__ We are going to use the customer table schema from Tpch.  Here is the data structure of the customer table:

| Column     | Type       |
| ---------- | ----------       |
| c_custkey  | integer       |
| c_name     | varchar(25)       |
| c_address  | varcahr(40)       |
| c_nationkey | integer       |
| c_phone    | varchar(15)       |
| c_acctbal  | double precision       |
| c_mktsegment | varchar(10)       |
| c_comment | varchar(117)       |

---

__2.__ Assume Kafka is running in standlone mode with localhost and port number 9092.  Create a topic ```customer``` with ```3```
partitions in Kafka by the command below:

```
% bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 3 --topic customer
```

---

__3.__ Add two Xdrive endpoints into the Xdrive configuration file ```xdrive.toml```.  The value of ```dgkafka.xdrive_offset_endpoint``` must match to  the name of the endpoint of ```xdr_kafkaoffset/xdr_kafkaoffset``` which is ```kafkaoffset``` in this case.


Copy and paste the following to create the configuration file ```xdrive.toml```.
```
[xdrive]
dir = "/tmp/xdrive"
port = 7171
host = [ "127.0.0.1" ]


[[xdrive.mount]]
name = "kafka"
argv = ["xdr_kafka/xdr_kafka", "127.0.0.1:9092"]


[[xdrive.mount]]
name = "kafkaoffset"
argv = ["xdr_kafkaoffset/xdr_kafkaoffset", "127.0.0.1:9092"]

```

__4.__ Deploy and Start the xdrive server

```
% xdrctl deploy xdrive.toml
% xdrctl start xdrive.toml
```

---

__5.__ We then need to create dgkafka configuration file [```dgkafka.toml```](../../products/deepgreen-db/xdrive/plugin-kafka/) in toml format.  For JSON format, Deepgreen requires a single column with json type and also a mapping between
JSON field and output table columns. 

```
[dgkafka]
database = "template1"
user = "ericlam"
password = ""
host = "127.0.0.1"
port = 5432
sslmode = "disable"
xdrive_host = "127.0.0.1"
xdrive_port = 7171
xdrive_offset_endpoint = "kafkaoffset"
xdrive_kafka_endpoint = "kafka"

[kafka]
  [kafka.input]
  format = "json"
  consumer_group = "dggrp"
  topic = "customer"
  partition_num = 3
  nwriter = 2
  ext_read_table = "customer_kafka_read"
  ext_write_table = "customer_kafka_write"
  ext_offset_table = "kafka_offset"
  
    [[kafka.input.columns]]
    name = "jdata"
    type = "json"

  [kafka.output]
  offset_table = "kafka_offset_summary"
  output_table = "customer"

    [[kafka.output.mappings]]
    name = "c_custkey"
    key = "(jdata->>'custkey')::integer"

    [[kafka.output.mappings]]
    name = "c_name"
    key = "(jdata->>'name')::varchar(25)"

    [[kafka.output.mappings]]
    name = "c_address"
    key = "(jdata->>'address')::varchar(40)"

    [[kafka.output.mappings]]
    name = "c_nationkey"
    key = "(jdata->>'nationkey')::integer"

    [[kafka.output.mappings]]
    name = "c_phone"
    key = "(jdata->>'phone')::varchar(15)"

    [[kafka.output.mappings]]
    name = "c_acctbal"
    key = "(jdata->>'acctbal')::double precision"

    [[kafka.output.mappings]]
    name = "c_mktsegment"
    key = "(jdata->>'mktsegment')::varchar(10)"

    [[kafka.output.mappings]]
    name = "c_comment"
    key = "(jdata->>'comment')::varchar(117)"


  [kafka.commit]
  max_row = 10000
  minimal_interval = -1

```

---

__6.__ Running the dgkafka setup command and create the Database tables.

```
% dgkafka setup dgkakfa.toml
```

After running the setup, table kafka.input.ext_read_table, kafka.input.ext_write_table, the offset tables kafka.input.ext_offset_table, kafka.output.offset_table and kafka.output.output_table defined in configuration file will be created.


Create the output table manually.

```
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

----

__7.__ Now, you are ready to run dgkafka.  Let's check the status of the topic ```customer``` by running ```dgkafka check```

```
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
---

__8.__ If everything is fine, we are ready to load data from Kafka to Deepgreen.  Open a new terminal and run ```dgkafka load```

```
% dgkafka load dgkafka.toml
```

It will wait for the messages from Kafka forever.  You may press CTRL-C to stop the process.

__9.__  Submit the data to Kafka by insert a JSON message into external writable table.

```
template1=# INSERT INTO customer_kafka_write VALUES ('{"custkey":111, "name": "eric", "address":"addr", "nationkey":2,"phone":"2345","acctbal":2.0, "mktsegment":"marketing","comment":"comment"}');
INSERT 0 1
```

The result will be loaded to the Database target table.
```
template1=# select * from customer;
 c_custkey | c_name | c_address | c_nationkey | c_phone | c_acctbal | c_mktsegment | c_comment 
-----------+--------+-----------+-------------+---------+-----------+--------------+-----------
       111 | eric   | addr      |           2 | 2345    |         2 | marketing    | comment
(1 row)

```

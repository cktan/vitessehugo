---
#layout: post

date: "2019-06-03"

author: Eric Lam

categories: ["xdrive", "kafka"]

title: Parallel data transfer between Deepgreen and Kafka via Xdrive
description: "Example of xdrive kafka plugin to transfer data between deepgreen and Kafka"
keywords: Kafka, Xdrive

headline: Blog
subheadline:
type: "post"

---

Deepgreen just released the latest Kafka extension ```dgkafka``` that can read/write data between Deepgreen and Kakfa in 
parallel fashion.  It reads the data from Kafka partitions simultaneously via Xdrive plugins and transfer the data to 
Deepgreen DB table.

We will show you how to setup the configurations and read the data from Kafka today.

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

__5.__ We then need to create dgkafka configuration file [```dgkafka.toml```](../../products/deepgreen-db/xdrive/plugin-kafka/) in toml format.

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

__9.__  Submit the data to Kafka.

Below is the sample CSV file that will submit to Kafka:

```
1|Customer#000000001|IVhzIApeRb ot,c,E|15|25-989-741-2988|711.56|BUILDING|to the even, regular platelets. regular, ironic epitaphs nag e
2|Customer#000000002|XSTf4,NCwDVaWNe6tEgvwfmRchLXak|13|23-768-687-3665|121.65|AUTOMOBILE|l accounts. blithely ironic theodolites integrate boldly: caref
3|Customer#000000003|MG9kdTD2WBHm|1|11-719-748-3364|7498.12|AUTOMOBILE| deposits eat slyly ironic, even instructions. express foxes detect slyly. blithely even accounts abov
4|Customer#000000004|XxVSJsLAGtn|4|14-128-190-5944|2866.83|MACHINERY| requests. final, regular ideas sleep final accou
5|Customer#000000005|KvpyuHCplrB84WgAiGV6sYpZq7Tj|3|13-750-942-6364|794.47|HOUSEHOLD|n accounts will have to unwind. foxes cajole accor
6|Customer#000000006|sKZz0CsnMD7mp4Xd0YrBvx,LREYKUWAh yVn|20|30-114-968-4951|7638.57|AUTOMOBILE|tions. even deposits boost according to the slyly bold packages. final accounts cajole requests. furious
```

Open another terminal and run the command ```$XDRIVE_HOME/plugin/csv2kafka/csv2kafka``` to submit the data to Kafka.

```
% csv2kafka -d "|" -w "|" 127.0.0.1:9092 customer data.csv
```

__10.__  All data will be loaded to the output table ```customer```.

```
template1=# select count(*) from customer;
 count  
--------
 150000
(1 row)

template1=# select * from customer limit 10;
 c_custkey |       c_name       |               c_address                | c_nationkey |     c_phone     | c_acctbal | c_mktsegment |     
                                               c_comment                                                    
-----------+--------------------+----------------------------------------+-------------+-----------------+-----------+--------------+-----
------------------------------------------------------------------------------------------------------------
        22 | Customer#000000022 | QI6p41,FNs5k7RZoCCVPUTkUdYpB           |           3 | 13-806-545-9701 |    591.98 | MACHINERY    | s no
d furiously above the furiously ironic ideas. 
        39 | Customer#000000039 | nnbRg,Pvy33dfkorYE FdeZ60              |           2 | 12-387-467-6509 |   6264.31 | AUTOMOBILE   | tion
s. slyly silent excuses slee
        41 | Customer#000000041 | IM9mzmyoxeBmvNw8lA7G3Ydska2nkZF        |          10 | 20-917-711-4011 |    270.95 | HOUSEHOLD    | ly r
egular accounts hang bold, silent packages. unusual foxes haggle slyly above the special, final depo
        53 | Customer#000000053 | HnaxHzTfFTZs8MuCpJyTbZ47Cm4wFOOgib     |          15 | 25-168-852-5363 |   4113.64 | HOUSEHOLD    | ar a
ccounts are. even foxes are blithely. fluffily pending deposits boost
        54 | Customer#000000054 | ,k4vf 5vECGWFy,hosTE,                  |           4 | 14-776-370-4745 |     868.9 | AUTOMOBILE   | sual
, silent accounts. furiously express accounts cajole special deposits. final, final accounts use furi
        55 | Customer#000000055 | zIRBR4KNEl HzaiV3a i9n6elrxzDEh8r8pDom |          10 | 20-180-440-8525 |   4572.11 | MACHINERY    | ully
 unusual packages wake bravely bold packages. unusual requests boost deposits! blithely ironic packages ab
        88 | Customer#000000088 | wtkjBN9eyrFuENSMmMFlJ3e7jE5KXcg        |          16 | 26-516-273-2566 |   8031.44 | AUTOMOBILE   | s ar
e quickly above the quickly ironic instructions; even requests about the carefully final deposi
        90 | Customer#000000090 | QxCzH7VxxYUWwfL7                       |          16 | 26-603-491-1238 |   7354.23 | BUILDING     | sly 
across the furiously even 
        96 | Customer#000000096 | vWLOrmXhRR                             |           8 | 18-422-845-1202 |   6323.92 | AUTOMOBILE   | pres
s requests believe furiously. carefully final instructions snooze carefully. 
       110 | Customer#000000110 | mymPfgphaYXNYtk                        |          10 | 20-893-536-2069 |   7462.99 | AUTOMOBILE   | nto 
beans cajole around the even, final deposits. quickly bold packages according to the furiously regular dept
(10 rows)

```

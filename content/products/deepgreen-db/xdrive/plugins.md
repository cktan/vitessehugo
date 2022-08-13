---
layout: xdrive-documentation-page

description: Xdrive
title: Xdrive
keywords: Xdrive

headline: Deepgreen DB

scroll: true

---

## System Plugins

List of __system xdrive plugins__:

- [parquet](#parquet)
- [orc](#orc)


### Parquet Plugin

Parquet plugin let you read/write datafile in parquet file format in
HDFS filesystem.

In the mountpoint configuration,

```bash
[[xdrive.mount]]
name = "hive_parquet"
argv = ["/usr/bin/java", "-Xmx1G", "-cp", "jars/vitessedata-file-plugin.jar",  "com.vitessedata.xdrive.parquet.Main", "hdfs", "/user/hive/warehouse" , "localhost", "8020", "ericlam"]

# argv[0] is the java command path
# argv[1-3] is the java options such as classpath and memory heap settings
# argv[4] is the Java runtime class
# argv[5] is the filesystem "hdfs"
# argv[6] is the root directory of the search path
# argv[7] is the hostname of hdfs namenode
# argv[8] is the port number of hdfs namenode
# argv[9] is the username in hdfs
```

External Table DDL

```bash
CREATE WRITABLE EXTERNAL TABLE W_NATION  ( N_NATIONKEY  INTEGER,
                            N_NAME       VARCHAR(25) /*CHAR(25)*/ ,
                            N_REGIONKEY  INTEGER ,
                            N_COMMENT    VARCHAR(152)) 
location('xdrive://localhost:50055/hive_parquet/nation/data#UUID#_#SEGID#') 
format 'spq';

CREATE EXTERNAL TABLE NATION  ( like W_NATION )
location('xdrive://localhost:50055/hive_parquet/nation/*') 
format 'spq';
```

### ORC Plugin

ORC plugin let you read/write datafile in orc file format in HDFS
filesystem.

In the mountpoint configuration,

```bash
[[xdrive.mount]]
name = "hive_orc"
argv = ["/usr/bin/java", "-Xmx1G", "-cp", "vitessedata-file-plugin.jar",  "com.vitessedata.xdrive.orc.Main", "hdfs", "/user/hive/warehouse" , "localhost", "8020", "ericlam"]

# argv[0] is the java command path
# argv[1-3] is the java options such as classpath and memory heap settings
# argv[4] is the Java runtime class
# argv[5] is the filesystem "hdfs"
# argv[6] is the root directory of the search path
# argv[7] is the hostname of hdfs namenode
# argv[8] is the port number of hdfs namenode
# argv[9] is the username in hdfs
```

External table DDL
```bash
CREATE WRITABLE EXTERNAL TABLE W_NATION  ( N_NATIONKEY  INTEGER,
                            N_NAME       VARCHAR(25) /*CHAR(25)*/ ,
                            N_REGIONKEY  INTEGER ,
                            N_COMMENT    VARCHAR(152)) 
location('xdrive://localhost:50055/hive_orc/nation/data#UUID#_#SEGID#') 
format 'spq';

CREATE EXTERNAL TABLE NATION  ( like W_NATION )
location('xdrive://localhost:50055/hive_orc/nation/*') 
format 'spq';
```



### Open Source Plugin

We also have open source Golang/Java xdrive plugins which are
supported by the community. You may download the source from github
and install it by yourself.

* Install GO Lang on your platform
* Get the source from github repos

```bash
% git clone https://github.com/vitesse-ftian/dgtools.git
  % cd dgtools/plugin/go
  % export GOPATH=$GOPATH:`pwd`
  % make
```

* After packages are built, you will see the package file in directory
  dgtools/plugin/go/package

```bash
% ls package
  esplugin.tgz  fsplugin.tgz  hbaseplugin.tgz  kafkaplugin.tgz  s3plugin.tgz
```

List of the xdrive plugins:

```bash
1. esplugin - elasticsearch real-time plugin
2. fsplugin - filesystem plugin 
3. hbaseplugin - hbase plugin
4. kafkaplugin - kafka plugin
5. s3plugin - AWS S3 plugin
6. esload - elasticsearch bulk plugin
```

* copy *.tgz files to $XDRIVE_HOME/plugin/package directory

* % cp package/*.tgz $XDRIVE_HOME/plugin/package directory

* deploy the plugin with xdrctl deployplugin command.

* check out the README, configuration settings and source code of
  plugins under the directory `dgtools/plugin/go/src/vitessedata`.

```bash
% ls dgtools/plugin/go/src/vitessedata
esload_spq esplugin_spq  fsplugin_csv  hbaseplugin_spq  kafkaplugin_spq  plugin  s3plugin_csv
```

***

## Question & Answer

Some hints for working with Hive and Deepgreen DB. Hive can create
both parquet and orc file as data storage. You can use our parquet and
orc plugin to directly read the data files generated by Hive. Here is
the summary of the problem you may encounter when you try to
manipulate the data between Hive and Deepgreen DB.

#### <i class="fas fa-question-circle highlight"></i> How to get rid
     of the '\N' character (NULL Character) in Hive?

__Affected Plugin__: orc and parquet

By default NULL values are written in the data files as \N and \N in
the data files are being interpreted as NULL when querying the data in
Hive.

This can be overridden by using
TBLPROPERTIES('serialization.null.format'=...)  e.g.

```bash
alter table orc_table set tblproperties('serialization.null.format'='')
```

#### <i class="fas fa-question-circle highlight"></i> How to get back
     the virtual columns in Hive partition which is not present in the
     partition table?

__Affected Plugin__: __orc__ and __parquet__

The partitioning columns is a virtual column, you cannot put a
partitioned Hive table on top of your data as it is. you need the
appropriate directory structure to be present in HDFS for partitioning
to work.

In order to maintain the partition information, you have to load the
data by each partitions.

__Hive Table__:

```bash
create table p_user ( name varchar(64), age int)
partitioned by (country varchar(64), state varchar(64))
stored as parquet;

insert into p_user partition (country, state) values ('eric', 20, 'usa', 'sf');
insert into p_user partition (country, state) values ('cecilia', 25, 'usa', 'ca');
```

__HDFS__:

```bash
% hadoop fs -ls /user/hive/warehouse/p_user/country=usa
/user/hive/warehouse/p_user/country=usa/state=sf
/user/hive/warehouse/p_user/country=usa/state=ca
```

__In Deepgreen__,

You have to specify the file location of each partition.

```bash
create external table p_user_usa_sf
( name varchar(64),
  age int
)
LOCATION ('xdrive://localhost:50055/hive_parquet/p_user/country=usa/state=sf')
FORMAT 'SPQ';
```

#### <i class="fas fa-question-circle highlight"></i> Why are ORC
     files generated by Hive cannot be recognized by Xdrive?

__Affected Plugin__: __orc__

We have tested Hive version 2.3.2, the column information is correct
and sync with the columns in Hive table.

For the version below 2.3.2, the orc file created by Hive may not have
correct column name in the orc file. the column names in the orc file
is _col0, _col1, ..., _colN. You can do the mapping in Deepgreen DB.
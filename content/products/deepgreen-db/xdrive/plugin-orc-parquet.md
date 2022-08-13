---
layout: xdrive-documentation-page

description: Xdrive Orc/Parquet Plugin
title: Xdrive Orc/Parquet Plugin
keywords: Xdrive Orc Parquet

headline: Deepgreen DB

scroll: true

---

## Xdrive Orc/Parquet Plugin

XDrive Orc/Parquet Plugin lets Deepgreen DB access files with ORC and Parquet file format residing on Local Storage/Amazon S3/Hadoop HDFS File System.  
Orc/Parquet file created by Hive including the partition table file can also be read by the plugin.

---

#### Executable

Xdrive Orc/Parquet plugin is written in Java and its library is located at ```$XDRIVE_HOME/plugin/jars/vitessedata-file-plugin.jar```.

* To execute Xdrive Orc Plugin, run Java class ```com.vitessedata.xdrive.orc.Main```.

* To execute Xdrive Parquet Plugin, run Java class ```com.vitessedata.xdrive.parquet.Main```.

---

#### DDL

External table DDL that refers to Orc/Parquet Plugin must have ```LOCATION``` clause that looks like this for Reads:
 
```
LOCATION(`xdrive://XDRIVE-HOST-PORT/MOUNTPOINT/path-to-files-with-wildcard.[orc|parquet]`)
FORMAT 'SPQ'
```
 
And for Writes:
 
```
LOCATION(`xdrive://XDRIVE-HOST-PORT/MOUNTPOINT/path-to-files-with-#UUID#.[orc|parquet]`)
FORMAT 'SPQ'
```
 
Setup the writable and readable external table as below.
 
```bash
CREATE WRITABLE EXTERNAL TABLE W_SUPPLIER ( S_SUPPKEY     INTEGER ,
                             S_NAME        VARCHAR(25) /*CHAR(25)*/ ,
                             S_ADDRESS     VARCHAR(40) ,
                             S_NATIONKEY   INTEGER ,
                             S_PHONE       VARCHAR(15) /*CHAR(15)*/ ,
                             S_ACCTBAL     DOUBLE PRECISION /*DECIMAL(15,2)*/ ,
                             S_COMMENT     VARCHAR(101) ) location('xdrive://127.0.0.1:50055/local_parquet/supplier/data#UUID#_#SEGID#') format 'spq';
 
CREATE EXTERNAL TABLE SUPPLIER( like W_SUPPLIER)location('xdrive://127.0.0.1:50055/local_parquet/supplier/*') format 'spq';
```

---

#### Mountpoint

##### Local Storage

Suppose we store data in the directory ```/dw/data``` under local hard disk, the following mountpoint would allow access to parquet/orc files in local hard disk.

```bash
# parquet local storage mountpoint
[[xdrive.mount]]
  name = "local_parquet"
  argv = ["/usr/bin/java", "-Xmx1G", "-cp", "jars/vitessedata-file-plugin.jar",  "com.vitessedata.xdrive.parquet.Main", "nfs", "/dw/data"]

# orc local storage mountpoint
[[xdrive.mount]]
  name = "local_orc"
  argv = ["/usr/bin/java", "-Xmx1G", "-cp", "jars/vitessedata-file-plugin.jar",  "com.vitessedata.xdrive.orc.Main", "nfs", "/dw/data"]
```

---

##### Amazon S3

Suppose we store data in the directory ```/dw/data``` under Amazon S3, the following mountpoint would allow access to parquet/orc files:

Make sure add the jar file ```jars/aws-java-sdk-bundle-1.11.271.jar``` in the classpath.

```bash
# S3 Parquet Mountpoint
[[xdrive.mount]]
  name = "s3_parquet"
  argv = ["/usr/bin/java", "-Xmx1G", "-cp", "jars/aws-java-sdk-bundle-1.11.271.jar:jars/vitessedata-file-plugin.jar",  "com.vitessedata.xdrive.parquet.Main", "s3", "S3_ENDPOINT", "S3_BUCKET", "/dw/data"]
  env = ["AWS_ACCESS_KEY_ID=AWS_KEYID", "AWS_SECRET_ACCESS_KEY=AWS_SECRET_KEY", "HDFS_CLIENT_CONF=path-to-hdfs-client-conf-xml"]

# S3 Orc Mountpoint
[[xdrive.mount]]
  name = "s3_orc"
  argv = ["/usr/bin/java", "-Xmx1G", "-cp", "jars/aws-java-sdk-bundle-1.11.271.jar:jars/vitessedata-file-plugin.jar",  "com.vitessedata.xdrive.orc.Main", "s3", "S3_ENDPOINT", "S3_BUCKET", "/dw/data"]
  env = ["AWS_ACCESS_KEY_ID=AWS_KEYID", "AWS_SECRET_ACCESS_KEY=AWS_SECRET_KEY", "HDFS_CLIENT_CONF=path-to-hdfs-client-conf-xml"]

# S3_ENDPOINT is the endpoint of the region, e.g. s3.amazonaws.com
# S3_BUCKET is the name of the S3 bucket
# AWS_KEYID is the AWS access key id
# AWS_SECRET_KEY is the AWS secret key
```

To support AWS S3 Fast upload and random file access for ORC and Parquet file, you may add the configurations in ```HDFS_CLIENT_CONF```.  If you don't need Fast Upload, you may remove the ```HDFS_CLIENT_CONF``` in the ```env```.

For more settings, please visit [Hadoop-AWS module: Integration with Amazon Web Services](https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html#Stabilizing:_S3A_Fast_Upload)

Example of hdfs_client.xml file,

```
<configuration>

<property>
  <name>fs.s3a.experimental.input.fadvise</name>
  <value>random</value>
</property>

<property>
  <name>fs.s3a.fast.upload</name>
  <value>true</value>
  <description>
    Use the incremental block upload mechanism with
    the buffering mechanism set in fs.s3a.fast.upload.buffer.
    The number of threads performing uploads in the filesystem is defined
    by fs.s3a.threads.max; the queue of waiting uploads limited by
    fs.s3a.max.total.tasks.
    The size of each buffer is set by fs.s3a.multipart.size.
  </description>
</property>

<property>
  <name>fs.s3a.fast.upload.buffer</name>
  <value>disk</value>
  <description>
    The buffering mechanism to use when using S3A fast upload
    (fs.s3a.fast.upload=true). Values: disk, array, bytebuffer.
    This configuration option has no effect if fs.s3a.fast.upload is false.

    "disk" will use the directories listed in fs.s3a.buffer.dir as
    the location(s) to save data prior to being uploaded.

    "array" uses arrays in the JVM heap

    "bytebuffer" uses off-heap memory within the JVM.

    Both "array" and "bytebuffer" will consume memory in a single stream up to the number
    of blocks set by:

        fs.s3a.multipart.size * fs.s3a.fast.upload.active.blocks.

    If using either of these mechanisms, keep this value low

    The total number of threads performing work across all threads is set by
    fs.s3a.threads.max, with fs.s3a.max.total.tasks values setting the number of queued
    work items.
  </description>
</property>

<property>
  <name>fs.s3a.multipart.size</name>
  <value>104857600</value>
  <description>How big (in bytes) to split upload or copy operations up into.
  </description>
</property>

<property>
  <name>fs.s3a.fast.upload.active.blocks</name>
  <value>4</value>
  <description>
    Maximum Number of blocks a single output stream can have
    active (uploading, or queued to the central FileSystem
    instance's pool of queued operations.

    This stops a single stream overloading the shared thread pool.
  </description>
</property>

<property>
  <name>fs.s3a.buffer.dir</name>
  <value>/tmp/</value>
  <description>Comma separated list of temporary directories use for
  storing blocks of data prior to their being uploaded to S3.
  When unset, the Hadoop temporary directory hadoop.tmp.dir is used</description>
</property>

<property>
  <name>fs.s3a.threads.max</name>
  <value>20</value>
  <description>The total number of threads available in the filesystem for data
    uploads *or any other queued filesystem operation*.</description>
</property>

<property>
  <name>fs.s3a.threads.core</name>
  <value>15</value>
  <description>Number of core threads in the threadpool.</description>
</property>

<property>
  <name>fs.s3a.connection.maximum</name>
  <value>30</value>
</property>

<property>
  <name>fs.s3a.max.total.tasks</name>
  <value>1000</value>
  <description>The number of operations which can be queued for execution</description>
</property>

<property>
  <name>fs.s3a.threads.keepalivetime</name>
  <value>60</value>
  <description>Number of seconds a thread can be idle before being
    terminated.</description>
</property>

</configuration>

```

---

##### Hadoop HDFS

Suppose we store data in the directory ```/dw/data``` under HDFS, the following mountpoint would allow access to parquet/orc files:

```bash
# parquet hdfs file
[[xdrive.mount]]
name = "parquet"
argv = ["/usr/bin/java", "-Xmx1G", "-cp", "jars/vitessedata-file-plugin.jar",  "com.vitessedata.xdrive.parquet.Main", "hdfs", "/dw/data" , "hdfsnamenode", "0"]
  env = ["HDFS_CLIENT_CONF=path-to-hdfs-client.xml"]

# parquet hdfs file
[[xdrive.mount]]
name = "orc"
argv = ["/usr/bin/java", "-Xmx1G", "-cp", "jars/vitessedata-file-plugin.jar",  "com.vitessedata.xdrive.orc.Main", "hdfs", "/dw/data" , "hdfsnamenode", "0"]
  env = ["HDFS_CLIENT_CONF=path-to-hdfs-client.xml"]
```

If ```hdfsnamenode``` is a service name, the value of ```hdfsnamenode``` will start with schema ```hdfs://``` and the value of port will be ‘0’. 


---

###### HDFS Client Configuration

You may pass the HDFS client configuration file by the environment variable ```HDFS_CLIENT_CONF```, 
which should explicitly point to the ```hdfs-client.xml``` file you want to use.  ```hdfs-client.xml``` is the file 
with the similar format as ```core-site.xml``` and ```hdfs-site.xml```.
You may concat ```core-site.xml``` and ```hdfs-site.xml``` to a single ```hdfs-client.xml```.

---

###### Simple HDFS Authentication

For non-secure connection, you’ll need to set ```hadoop.security.authentication``` property to ```simple``` 
and ```com.vitessedata.xdrive.security.user.name``` to username in Hadoop.


```
<configuration>
        <property>
                <name>hadoop.security.authentication</name>
                <value>simple</value>
         </property>

         <property>
                <name>com.vitessedata.xdrive.security.user.name</name>
                <value>hduser<value>
         </property>
</configuration>
```

---

###### Enabling HDFS authentication with Kerberos-secured Hadoop Cluster

We assume that kerberos is properly installed and configured on each Deepgreen data segment.

For secure connection, you’ll need to change ```hadoop.security.authentication``` property from ```simple``` to ```kerberos```.

```
<configuration>
        <property>
                <name>hadoop.security.authentication</name>
                <value>kerberos</value>
         </property>
</configuration>
```

Kerberos Authentication uses JAAS Configuration which is passed from java command line arguments. and the Kerberos ticket cache file path is passed by environment variable ```KRB5CCNAME```

```bash
# parquet hdfs file
[[xdrive.mount]]
name = "parquet"
argv = ["/usr/bin/java", "-Dsun.security.krb5.debug=true", "-Djavax.security.auth.useSubjectCredsOnly=false", "-Djava.security.krb5.conf=/etc/krb5.conf", "-Djava.security.auth.login.config=path-to-jaas.conf", "-Xmx1G", "-cp", "jars/vitessedata-file-plugin.jar",  "com.vitessedata.xdrive.parquet.Main", "hdfs", "/data" , "hdfs://mycluster", "0"]
  env = ["HDFS_CLIENT_CONF=path-to-hdfs-client.xml", "KRB5CCNAME=/run/user/krb5cc/krb5cc_1051"]

# orc hdfs file
[[xdrive.mount]]
name = "orc"
argv = ["/usr/bin/java", "-Dsun.security.krb5.debug=true", "-Djavax.security.auth.useSubjectCredsOnly=false", "-Djava.security.krb5.conf=/etc/krb5.conf", "-Djava.security.auth.login.config=path-to-jaas.conf", "-Xmx1G", "-cp", "jars/vitessedata-file-plugin.jar",  "com.vitessedata.xdrive.orc.Main", "hdfs", "/data" , "hdfs://mycluster", "0"]
  env = ["HDFS_CLIENT_CONF=path-to-hdfs-client.xml", "KRB5CCNAME=/run/user/krb5cc/krb5cc_1051"]
```

Example of jaas.conf file,

```
com.sun.security.jgss.krb5.initiate {
    com.sun.security.auth.module.Krb5LoginModule required
    doNotPrompt=true
    principal="gpadmin@VITESSEDATA.COM"
    useKeyTab=false
    useTicketCache=true
    TicketCache=/run/user/krb5cc/krb5cc_1051
    storeKey=true;
};
```

To add debug message of the kerberos security, 

```
java -Dsun.security.krb5.debug=true
```

---

###### High Availability Mode

Although HDFS is resilient to failure of data-nodes, the name-node is a single repository of metadata for the system, and so a single point of failure. High-availability (HA) involves configuring fall-back name-nodes which can take over in the event of failure.

```
<configuration>

        <property>
                <name>dfs.default.uri</name>
                <value>hdfs://mycluster</value>
        </property>
        <property>
                <name>dfs.nameservices</name>
                <value>mycluster</value>
        </property>

        <property>
                <name>dfs.ha.namenodes.mycluster</name>
                <value>namenode1,namenode2</value>
        </property>

        <property>
                <name>dfs.namenode.rpc-address.mycluster.namenode1</name>
                <value>hostname1:8020</value>
        </property>

        <property>
                <name>dfs.namenode.rpc-address.mycluster.namenode2</name>
                <value>hostname2:8020</value>
        </property>

        <property>
                <name>dfs.namenode.http-address.mycluster.namenode1</name>
                <value>hostname1:50070</value>
        </property>

        <property>
                <name>dfs.namenode.http-address.mycluster.namenode2</name>
                <value>hostname2:50070</value>
        </property>

</configuration>
```

---
###### Test HDFS Client Configuration

To Test the HDFS client configuration, you may run the ```$GPHOME/plugin/xdr_hdfs/xdr_hdfscmd``` to test
the connectivity to Hadoop server.

To read the content of a file on HDFS,
```
LIBHDFS3_CONF=path-to-hdfs-client.xml xdr_hdfscmd  cat 127.0.0.1 8020 /data/nation.csv
```

To print out the list of files in a directory on HDFS,
```
LIBHDFS3_CONF=path-to-hdfs-client.xml xdr_hdfscmd  ls 127.0.0.1 8020 /data/
```

---
###### ORC File Created By Hive (ORC ONLY)

In case you have created ORC file by Hive, the column name(s) specified in ORC file will not be the same as you defined in Hive.  The column name specified in your ORC file will be defined as (_col0, _col1, _col2, …, colN).  e.g.  if you have a table supplier created in Hive, you have to use the column name (_col0, _col1, _col2, …, colN) in Deepgreen instead of original column name specified in Hive.

For example, 

The column matching of the table ```supplier```

Column in Hive | Column in Deepgreen |
---------- | ------------------- |
S_SUPPKEY | _col0 |
S_NAME | _col1 |
S_ADDRESS | _col2 |
S_NATIONKEY | _col3 |
S_PHONE | _col4 |
S_ACCTBAL | _col5 |
S_COMMENT | _col6 |

The DDL of external table is

```bash
CREATE WRITABLE EXTERNAL TABLE W_SUPPLIER (   _col0   INTEGER ,
                             _col1        VARCHAR(25) /*CHAR(25)*/ ,
                             _col2     VARCHAR(40) ,
                             _col3   INTEGER ,
                             _col4       VARCHAR(15) /*CHAR(15)*/ ,
                             _col5     DOUBLE PRECISION /*DECIMAL(15,2)*/ ,
                             _col6     VARCHAR(101) ) location('xdrive://127.0.0.1:50055/tpch/supplier/data#UUID#_#SEGID#') format 'spq';
 
CREATE EXTERNAL TABLE SUPPLIER( like W_SUPPLIER)location('xdrive://127.0.0.1:50055/tpch/supplier/*') format 'spq';
```

---

###### Parameter Tuning

For big table transfer, you may run out of heap memory in Java.  You may increase the heap size in java startup command in xdrive.toml.  The default Java heap size is 1G.

* Use -Xmx to specify the maximum heap size



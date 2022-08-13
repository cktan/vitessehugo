---
layout: xdrive-documentation-page

description: Xdrive
title: Xdrive
keywords: Xdrive

headline: Deepgreen DB

scroll: true

---

## Xdrive HDFS Plugin

HDFS plugin lets Deepgreen DB access files residing on Hadoop File
System. It currently support two file formats: CSV and SPQ.

#### Mountpoint

Suppose we store data in the directory `/dw/data` under HDFS, the
following mountpoint would allow access to csv files:

```bash

[[xdrive.mount]]
name = "datacsv"                # mountpoint name
argv = ["xdr_hdfs/xdr_hdfs",             # plugin
     "csv",                     # file format (csv or spq)
     "hdfsnamenode",            # HDFS name node host or service name
     "8020",                    # HDFS name node port
     "/dw/data",                # root data dir 
     ]
env = ["LIBHDFS3_CONF=path-to-hdfs-client.xml"]
```

If `hdfsnamenode` is a service name, the value of `hdfsnamenode` will start with schema `hdfs://` and 
the value of port will be '0'. e.g., 

```bash

[[xdrive.mount]]
name = "datacsv"                # mountpoint name
argv = ["xdr_hdfs/xdr_hdfs",             # plugin
     "csv",                     # file format (csv or spq)
     "hdfs://mycluster",            # HDFS name node host or service name
     "0",                    # HDFS name node port
     "/dw/data",                # root data dir
     ]
env = ["LIBHDFS3_CONF=path-to-hdfs-client.xml"]
```

#### DDL

External table DDL that refers to HDFS Plugin must have `LOCATION`
clause that looks like this for Reads:

```
LOCATION(`xdrive://XDRIVE-HOST-PORT/MOUNTPOINT/path-to-files-with-wildcard.{csv|spq}`)
FORMAT '{CSV|SPQ}'
```

And for Writes:
```
LOCATION(`xdrive://XDRIVE-HOST-PORT/MOUNTPOINT/path-to-files-with-#UUID#.{csv|spq}`)
FORMAT '{CSV|SPQ}'
```

```bash

DROP EXTERNAL TABLE IF EXISTS nation; 
CREATE EXTERNAL TABLE nation (
    n_nationkey integer,
    n_name varchar,
    n_regionkey integer,
    n_comment varchar)
LOCATION ('xdrive://XDRIVE-HOST-PORT/datacsv/public/nation/nation*.csv')
FORMAT 'CSV';

DROP EXTERNAL TABLE IF EXISTS nation_writer;
CREATE WRITABLE EXTERNAL TABLE nation_writer (
    n_nationkey integer,
    n_name varchar,
    n_regionkey integer,
    n_comment varchar)
LOCATION ('xdrive://XDRIVE-HOST-PORT/datacsv/public/nation/nation#UUID#.csv')
FORMAT 'CSV';

```

#### HDFS Client Configuration

You may pass the HDFS client configuration file by the environment varialble `LIBHDFS3_CONF`, which
should explicitly point to the `hdfs-client.xml` file you want to use.

`hdfs-client.xml` is the file with the similar format as `core-site.xml` and `hdfs-site.xml`.  
You may concat `core-site.xml` and `hdfs-site.xml` to a single `hdfs-client.xml`.

#### Simple HDFS authentication

For non-secure connection, you'll need to set `hadoop.security.authentication` property to `simple` and 
`com.vitessedata.xdrive.security.user.name` to username in Hadoop.

```bash
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

#### Enabling HDFS authentication with Kerberos-secured Hadoop Cluster

For secure connection, you'll need to change `hadoop.security.authentication` property from `simple`
to `kerberos`.

If kerberos ticket cache is used for authentication, you can set the configuration 
`hadoop.security.kerberos.ticket.cache.path` with the value of ticket cache path
in the `hdfs-client.xml`.

```bash

<configuration>
        <property>
                <name>hadoop.security.authentication</name>
                <value>kerberos</value>
         </property>

         <property>
                <name>hadoop.security.kerberos.ticket.cache.path</name>
                <value>kerberos_ticket_cache_filepath</value>
         </property>
</configuration>
```
 or you can set the environment variable `KRB5CCNAME` to specify the ticket cache file path.

```bash
[[xdrive.mount]]
name = "datacsv"                # mountpoint name
argv = ["xdr_hdfs/xdr_hdfs",             # plugin
     "csv",                     # file format (csv or spq)
     "hdfsnamenode",            # HDFS name node host or service name
     "8020",                    # HDFS name node port
     "/dw/data",                # root data dir
     ]
env = ["LIBHDFS3_CONF=path-to-hdfs-client.xml", "KRB5CCNAME=path-to-kerberos-ticket-cache"]

```

#### High Availability Mode

Although HDFS is resilient to failure of data-nodes, the name-node is a single repository of metadata for the system, 
and so a single point of failure. High-availability (HA) involves configuring fall-back name-nodes 
which can take over in the event of failure. 

```bash
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

#### Test HDFS Client Configuration 

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


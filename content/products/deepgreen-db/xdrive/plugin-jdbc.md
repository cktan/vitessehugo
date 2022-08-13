---
layout: xdrive-documentation-page

description: Xdrive
title: Xdrive
keywords: Xdrive

headline: Deepgreen DB

scroll: true

---

## Xdrive JDBC Plugin

The JDBC Plugin allows Deepgreen DB to read/write tables of another database.

#### Mountpoint

```bash
[[xdrive.mount]]
name = "myotherdb"
argv = ["/usr/bin/java", 
         "-classpath", "YOUR-JDBC-JAR:jars/vitessedata-db-plugin.jar", 
         "com.vitessedata.xdrive.jdbc.Main"]
env = ["CONNECTION_STRING=YOUR-JDBC-CONNECTION-STRING"]
```

For PostgreSQL database:

- replace `YOUR-JDBC-JAR` above with `jars/postgresql-42.2.1.jar`

- replace `YOUR-JDBC-CONNECTION-STRING` with a string like this:<br/>
  `jdbc:postgresql://dbhost:port/myotherdb?user=scott&password=tiger&ssl=true&stringtype=unspecified`.<br/>
  For details on postgres connection string, please refer to this
  [document](https://jdbc.postgresql.org/documentation/head/connect.html).


#### DDL

When constructing an external table DDL that refers to a JDBC Plugin,
specify the `LOCATION` clause like this:

```
LOCATION('xdrive://XDRIVE-HOST-PORT/MOUNTPOINT/TABLENAME')
FORMAT 'SPQ'
```

For example, to read/write the `nation` table on another database
through the JDBC Plugin, we may write the DDL like this:

```bash
DROP EXTERNAL TABLE IF EXISTS nation;
CREATE EXTERNAL TABLE nation (
    n_nationkey int,
    n_name text,
    n_regionkey int,
    n_comment text) LOCATION('xdrive://XDRIVE-HOST-PORT/myotherdb/nation') 
FORMAT 'SPQ'; 


DROP EXTERNAL TABLE IF EXISTS w_nation;
CREATE WRITABLE EXTERNAL TABLE w_nation (
    n_nationkey int,
    n_name text,
    n_regionkey int,
    n_comment text) LOCATION('xdrive://XDRIVE-HOST-PORT/myotherdb/nation') 
FORMAT 'SPQ'; 

```

Note that:

- Our mountpoint name is `myotherdb`.

- Our table name on the source or destination database is `nation`.

- `FORMAT 'SPQ'` must be specified as the JDBC Plugin expects this format.

#### Troubleshooting

- To increase the Java heap size, add the option `-Xmx1g` in Java command line argument

- For Oracle JDBC connection, change the line from `securerandom.source=file:/dev/random` to `securerandom.source=file:/dev/urandom` in `$JAVA_HOME/jre/lib/security/java.security` to solve the Oracle authentication timeout.

- For PostgreSQL JDBC connection, add the option `stringtype=unspecified` to the JDBC connection string.

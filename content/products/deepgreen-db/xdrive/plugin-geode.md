---
layout: xdrive-documentation-page

description: Xdrive
title: Xdrive
keywords: Xdrive

headline: Deepgreen DB

scroll: true

---

## Xdrive Geode Plugin

Geode plugin is a write-only plugin, i.e., it lets Deepgreen DB
populate Geode regions.


#### Mountpoint Format

```bash
[[xdrive.mount]]
name = "imdg"
argv = ["/usr/bin/java", 
         "-classpath", "LOCATION-OF-GEODE-DEPENDENCIES-JAR:jars/vitessedata-db-plugin.jar", 
         "com.vitessedata.xdrive.geode.Main"]
```

Note: Make sure that `geode-dependencies.jar` is available on all
Deepgreen DB machines at the same file path, and substitute this file
path into the phrase `LOCATION-OF-GEODE-DEPENDENCIES-JAR` above.

#### DDL

When constructing an external table DDL that refers to a Geode
Plugin, specify the `LOCATION` clause like this:

```
LOCATION('xdrive://XDRIVE-HOST-PORT/MOUNTPOIN/REGION_NAME/PDX_CLASS_NAME/KEY')
FORMAT 'SPQ' (INTEGER TIMESTAMP)
```

For example, if we want to overwrite the `lineitem` table on geode, we may write something like this:

```bash

DROP EXTERNAL TABLE IF EXISTS w_lineitem; 
CREATE WRITABLE EXTERNAL TABLE w_lineitem (
        L_ORDERKEY     BIGINT, 
        L_PARTKEY      INTEGER, 
        L_SUPPKEY      INTEGER, 
        L_LINENUMBER   INTEGER, 
        L_QUANTITY     DOUBLE PRECISION,
        L_EXTENDEDPRICE  DOUBLE PRECISION,
        L_DISCOUNT     DOUBLE PRECISION,
        L_TAX          DOUBLE PRECISION,
        L_RETURNFLAG   VARCHAR(1),
        L_LINESTATUS   VARCHAR(1),
        L_SHIPDATE     DATE ,
        L_COMMITDATE   DATE ,
        L_RECEIPTDATE  DATE ,
        L_SHIPINSTRUCT VARCHAR(25),
        L_SHIPMODE     VARCHAR(10),
        L_COMMENT      VARCHAR(44) 
) LOCATION('xdrive://XDRIVE-HOST-PORT/imdg/lineitem/pod.lineitem/l_orderkey:l_partkey:l_suppkey:l_linenumber') 
FORMAT 'SPQ' (INTEGER TIMESTAMP);
```

Note that:

- Our mountpoint name is `imdg`.

- The region is `lineitem`.

- The PDX class name is `pod.lineitem`.

- The geode keys are a composite of 4: `(l_orderkey, l_partkey, l_suppkey, l_linenumber)`.

- `FORMAT 'SPQ'` must be specified as the plugin expects this format.

- `(INTEGER TIMESTAMP)` is specified to write the dates and timestamps
as integers to Geode. Otherwise, dates will be written as YYYY-MM-DD
strings.


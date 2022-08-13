---
layout: xdrive-documentation-page

description: Xdrive
title: Xdrive
keywords: Xdrive

headline: Deepgreen DB

scroll: true

---

## Xdrive FS Plugin

FS plugin lets Deepgreen read/write from/to local filesystem on the
servers running Xdrive. It currently supports four file formats for read and write: CSV, Orc, Parquet and
SPQ.

#### Mountpoint

Suppose we store data in the root directory `/dw/data`, the following
mountpoints would allow access to the data:

```bash
# xhost_arrow server to support parquet file format
[[xdrive.xhost]]
name = "arrow"
bin = "xhost_arrow"


[[xdrive.mount]]
name = "datacsv"                # mountpoint name
argv = ["xdr_fs/xdr_fs",               # plugin must be xdr_fs/xdr_fs
     "[csv|par|parquet|spq|orc]",                     # file format (orc, par, parquet, csv or spq)
     "/dw/data",                # root data dir, e.g. /dw/data
     ]

```

#### DDL

When constructing an external table DDL that refers to a FS Plugin,
specify the `LOCATION` clause like this for Reads:

```
LOCATION(`xdrive://XDRIVE-HOST-PORT/MOUNTPOINT/path-to-files-with-wildcard.{csv|spq|parquet|orc}`)
FORMAT '{CSV|SPQ|PARQUET|ORC}'
```

And for Writes:
```
LOCATION(`xdrive://XDRIVE-HOST-PORT/MOUNTPOINT/path-to-files-with-#UUID#.{csv|spq|parquet|orc}`)
FORMAT '{CSV|SPQ|PARQUET|ORC}'
```

For example, To read/write the `nation` csv table located in
`/dw/data/public/nation` directory, we create external table DDLs like
this:

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

Note that to read / write Parquet, SPQ and CSV files, you would need separate mountpoints.




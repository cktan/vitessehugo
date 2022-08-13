---
layout: xdrive-documentation-page

description: Xdrive
title: Xdrive
keywords: Xdrive

headline: Deepgreen DB

scroll: true

---

## Xdrive S3 Plugin

S3 Plugin lets Deepgreen accesses AWS S3.

#### Mountpoint

```bash
[[xdrive.mount]]
name = "tpch1fs3"
argv = ["xdr_s3/xdr_s3",       # plugin
     "csv",             # file format. csv or spq is supported
     "mybucket",        # bucket name
     "myregion",        # region name
     "tmpprefix",       # tmp directory prefix for fast uploading, default to "/tmp/"
     "/data"]           # root data dir
env = [
    "AWS_ACCESS_KEY_ID=YOUR-KEYID",
    "AWS_SECRET_ACCESS_KEY=YOUR_ACCESS_KEY"
    ]
```

#### DDL

When constructing an external table DDL that refers to an S3 Plugin,
specify the `LOCATION` clause like this for Reads:

```
LOCATION(`xdrive://XDRIVE-HOST-PORT/MOUNTPOINT/object-key-with-wildcard.{csv|spq}`)
FORMAT '{CSV|SPQ}'
```

And for Writes:
```
LOCATION(`xdrive://XDRIVE-HOST-PORT/MOUNTPOINT/object-key-with-#UUID#.{csv|spq}`)
FORMAT '{CSV|SPQ}'
```

For example, To read/write the `nation` csv table located in the
`mybucket` bucket, with mountpoint `tpch1fs3` and with absolute directory `/data/public/nation/`,
we create external table DDLs like this:

```
DROP EXTERNAL TABLE IF EXISTS 
CREATE EXTERNAL TABLE nation (
    n_nationkey integer,
    n_name varchar,
    n_regionkey integer,
    n_comment varchar)
LOCATION ('xdrive://XDRIVE-HOST-PORT/tpch1fs3/public/nation/nation*.csv')
FORMAT 'CSV';

DROP EXTERNAL TABLE IF EXISTS nation_writer;
CREATE WRITABLE EXTERNAL TABLE nation_writer (
    n_nationkey integer,
    n_name varchar,
    n_regionkey integer,
    n_comment varchar)
LOCATION ('xdrive://XDRIVE-HOST-PORT/tpch1fs3/public/nation/nation#UUID#.csv')
FORMAT 'CSV';
```

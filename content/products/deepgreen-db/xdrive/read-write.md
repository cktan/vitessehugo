---
layout: xdrive-documentation-page

description: Xdrive
title: Xdrive
keywords: Xdrive

headline: Deepgreen DB

scroll: true

---

## Reading Data With Deepgreen External Table

You can access the data on Xdrive through the external table mechanism
provided in Deepgreen DB. The syntax is essentially the same as
Greenplum external table.

```bash
CREATE EXTERNAL TABLE table_name (columnspec)
LOCATION (’xdrive://host:port/mountpoint/reader-path’)
FORMAT ’CSV’ [csv options]
     | ’SPQ’
     | ’PARQUET’
     | ’ORC’;
```

<i class="fas fa-info-circle text-info"></i> Xdrive currently supports
four formats: CSV and SPQ, PARQUET and ORC. SPQ stands for Simple Parquet Format; it is
Vitesse Data's proprietary high performance, column store format.

The `reader-path` specifies a UNIX file path glob pattern that can
match many files. If we had partition our lineitem spq table and store
the table fragments under the path:

```bash
/data/warehouse/lineitem/YYYY/MM/lineitem_part.spq
```

where ```YYYY``` and ```MM``` are substituted with the year and month
values respectively, we would specify our ```LOCATION``` clause as:

```bash
LOCATION ('xdrive://host:port/dw/lineitem/*/*/lineitem*.spq')
```

***

### Writing Data With Deepgreen External Table

With some effort, you can write to Xdrive using a more elaborate
external table construct:

```bash
CREATE WRITABLE EXTERNAL TABLE write_table_name (columnspec)
LOCATION (’xdrive://host:port/mountpoint/writer-path’)
FORMAT ’CSV’ [csv options]
     | ’SPQ’
     | ’PARQUET’
     | ’ORC’;
```
You may also limit the number of xdrive workers for write by setting the location URL as follow.

```bash
xdrive://host:port/mountpoint?nwriter=5/...
e.g. xdrive://127.0.0.1:50051/kafka?nwriter=5/customer
```


In contrast to the `reader-path`, the `writer-path` is a very
different animal. While a `reader-path` may resolve to multiple files
on Xdrive, a `writer-path` should map to only one target file. On any
INSERT to the external table, the target file will be created (or
truncated if it already exists) and appended to. To facilitate
creation of unique file names for the writes, the `writer-path` may be
annotated with a `#UUID#` substitution pattern. With the `#UUID#`
substitution, every INSERT statement will create a distinct new file.

Continuing with our example above, we would use the following external
table to insert lineitems into Jan 2016 partition:

```bash
CREATE WRITABLE EXTERNAL TABLE write_lineitem_2016_01 (columnspec)
LOCATION (’xdrive://host:port/dw/lineitem/2016/01/lineitem_#UUID#.spq')
FORMAT ’SPQ’;
```

Each INSERT will create a new SPQ file. If you recall, our
`reader-path` was `xdrive://host:port/dw/lineitem/*/*/lineitem*.spq`;
the wildcards in the path allow our scan to encompass the new files
created by the INSERT.

***

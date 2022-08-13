---
layout: xdrive-documentation-page

description: Xdrive
title: Xdrive
keywords: Xdrive

headline: Deepgreen DB

scroll: true

---

## What is Xdrive?

Xdrive is a Deepgreen DB connectivity service that extends
the reach of Deepgreen to external data sources. Through Xdrive, 
Deepgreen DB is able to read/write from/to a myriad of 
data management systems, including Amazon S3, HDFS, Oracle, and
Elastic Search.

### Plugins

Xdrive is written with extensibility in mind. Each plugin handles I/O
to a different storage system and/or format. Although Xdrive ships
with many plugins that Vitesse Data developed, customers can easily
write their own.


### Characteristics

Using Xdrive, Deepgreen DB is able to scan external tables at 
tremendous speed due to these underlying architectural choices:

**High Bandwidth** --- Compared to other similar products in the
market today, which transmit in units or batches of rows, Xdrive
transmit data to Deepgreen DB in batches of (optionally compressed)
columns. On the receiving side, due to the columnar layout of the
data, it is immediate ready for further filtering using vector
operations.

**Pushed-down Filters** --- In addition, Xdrive supports filtering at
the source. Deepgreen DB is able to push filter conditions to the
other side of the data pipeline, potentially eliminating substantial
amount of data before the transfer. This is especially crucial when
the network between the producer (e.g., a Hadoop cluster) and the
consumer (i.e., Deepgreen DB) is slow.

**Elasticity** --- Finally, Xdrive is elastic in the sense that
multiple Xdrive instances can work together to feed a Deepgreen DB
cluster. Each instance of Xdrive can filter and push mutually
exclusive fragments of data to distinctive Deepgreen DB segments, in
effect supplementing the cluster's CPU resources. Further, Deepgreen
MPP is able to scan and process external data in parallel since the
data lands evenly on all segments.



***

---
layout: db-feature-page

description: Deepgreen DB
title: Deepgreen DB
keywords: Deepgreen DB

headline: Deepgreen DB

---


### Column Store with lz4 and zstd

_lz4 new in version 16.05._ 
_zstd new in version 16.16._

---
 
Greenplum DB ships with available _zlib_ compression for
storage. In addition to zlib, Deepgreen DB incorporates two other
compression for storage that are better suited for database
workload: _zstd_ and _lz4_.

Customers who require a very good compression ratio to save on
disk space should pick _zstd_ compression algorithm for
column stores and append-optimized heap tables. Compared to
zlib, zstd has better compression ratio and also utilizes the
CPU much more efficiently.

Customers who have mostly read workload on fast I/O devices
should select _lz4_ due to its spectacular decompression
speed. Even though the compression ratio of lz4 is not as good
as zlib or zstd, we feel it offers a good tradeoff for
read-heavy database operation. This is especially true on fast
I/O devices, where the savings from reading less disk blocks does
not justify the CPU cost in decompressing the data.

For details on these new compression algorithms, please refer to their respective home pages:

* [zstd home page](http://facebook.github.io/zstd/)
* [lz4 home page](http://lz4.github.io/lz4/)


### Quick Test

Without going into too much details, a quick test of the none /
zlib / zstd / lz4 compression algorithms on column store can be
found below. Obviously, your mileage may vary depending on your
hardware. Our results are tabulated
here:

<div class="table-responsive">
<table class="table">
  <tr><th></th> <th>none</th> <th>zlib</th> <th>zstd</th> <th>lz4</th> </tr>
  <tr><th>Content Size (MB)</th>
  	<td>1708<br/>--</td>
  	<td>374<br/> <small>78% savings</small> </td>
  	<td class="highlight">325<br/>81% savings</td>
  	<td>785<br/> <small>54% savings</small> </td></tr>
  <tr><th>Write (sec)</th>
  	<td>92.8<br/>--</td>
  	<td>62.9<br/><small>32% faster</small> </td>
  	<td class="highlight">59.2<br/>36% faster</td>
  	<td>70.5<br/><small>24% faster</small> </td></tr>
  <tr><th>Read (sec)</th>
  	<td>2.53<br/>--</td>
  	<td>3.69<br/><small>45% slower</small> </td>
  	<td>3.12<br/><small>23% slower</small> </td>
  	<td class="highlight">2.59<br/>2% slower</td></tr>
</table>
</div>

<!--
|               | none          | zlib          | zstd          | lz4           |
|---------------|---------------|---------------|---------------|---------------|
| **Content Size (MB)**|1708<br/>– |374<br/>*78% savings* |325<br/>*81% savings*|785<br/>*54% savings* |
| **Write (sec)**  | 92.8<br/>–   | 62.9<br/>*32% faster* | 59.2<br/>*36% faster*| 70.5<br/>*24% faster*|
| **Read (sec)** | 2.53<br/>– | 3.69<br/>*45% slower* | 3.12<br/>*23% slower* | 2.59<br/>*2% slower* |
-->

---

```
create temp table ttnone (
i int,
t text,
default column encoding (compresstype=none))
with (appendonly=true, orientation=column)
distributed by (i);
CREATE TABLE
Time: 162.064 ms

create temp table ttzlib(
i int,
t text,
default column encoding (compresstype=zlib, compresslevel=1))
with (appendonly=true, orientation=column)
distributed by (i);
CREATE TABLE
Time: 163.772 ms

create temp table ttzstd (
i int,
t text,
default column encoding (compresstype=zstd, compresslevel=1))
with (appendonly=true, orientation=column)
distributed by (i);
CREATE TABLE
Time: 179.972 ms

create temp table ttlz4 (
i int,
t text,
default column encoding (compresstype=lz4))
with (appendonly=true, orientation=column)
distributed by (i);
CREATE TABLE
Time: 166.926 ms

-- -------------------------------
-- WRITE -------------------------
-- -------------------------------

insert into ttnone select i, 'user '||i from generate_series(1, 100000000) i;
INSERT 0 100000000
Time: 92833.687 ms

insert into ttzlib select i, 'user '||i from generate_series(1, 100000000) i;
INSERT 0 100000000
Time: 62898.443 ms

insert into ttzstd select i, 'user '||i from generate_series(1, 100000000) i;
INSERT 0 100000000
Time: 59157.905 ms

insert into ttlz4 select i, 'user '||i from generate_series(1, 100000000) i;
INSERT 0 100000000
Time: 70459.011 ms

-- -------------------------------
-- SIZE --------------------------
-- -------------------------------

select pg_size_pretty(pg_relation_size('ttnone'));
 pg_size_pretty
----------------
 1708 MB
(1 row)

Time: 0.857 ms

select pg_size_pretty(pg_relation_size('ttzlib'));
 pg_size_pretty
----------------
 374 MB
(1 row)

Time: 15.111 ms

select pg_size_pretty(pg_relation_size('ttzstd'));
 pg_size_pretty
----------------
 325 MB
(1 row)

Time: 0.889 ms

select pg_size_pretty(pg_relation_size('ttlz4'));
 pg_size_pretty
----------------
 785 MB
(1 row)

Time: 0.841 ms

-- -------------------------------
-- READ --------------------------
-- -------------------------------

select sum(length(t)) from ttnone;
sum
------------
 1288888898
(1 row)

Time: 2533.964 ms

select sum(length(t)) from ttzlib;
sum
------------
 1288888898
(1 row)

Time: 3688.746 ms

select sum(length(t)) from ttzstd;
sum
------------
 1288888898
(1 row)

Time: 3197.472 ms

select sum(length(t)) from ttlz4;
sum
------------
 1288888898
(1 row)

Time: 2591.616 ms
```

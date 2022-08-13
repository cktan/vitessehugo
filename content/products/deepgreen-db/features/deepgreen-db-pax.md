---
layout: db-feature-page

description: Deepgreen DB
title: Deepgreen DB
keywords: Deepgreen DB 

headline: Deepgreen DB

---

### PAX Column Store


_New in version 18.07._

---

Starting in version 18.x, Deepgreen DB includes a new column store called PAX that is in many ways 
superior to the default column store in GPDB. It addresses three major 
complaints of the GPDB column store from current users: 

1. Too many open files -- GPDB column store uses one file per column, and
   all of these must be kept open concurrently during a scan. This is 
   extremely taxing on the OS resources when users have very wide table, 
   as is customary for column store tables.

2. OID exhaustion -- this fault is also introduced by the one-file-per-column 
   design. Each file consumes an OID, which must be remembered in the catalog. 
   As a result, more OIDs are used during normal operation, and the catalog becomes
   bloated easily as entries relating to these new OIDs are inserted and deleted 
   during intensive ETL operation.
   
2. Lack of zonemap -- a zonemap is basically a coarse index that eliminates
   redundant scans that would never produce rows. Naturally, this has major performance 
   implication as it helps keep I/O to the minimal when scanning column 
   stores with filters.


### Usage

Creating a PAX table only requires the storage directive `APPENDONLY=true, COMPRESSTYPE=PAX`.

```
    CREATE TABLE T ( ... ) WITH (APPENDONLY=true, COMPRESSTYPE=PAX);
```

#### Example: Create

The following shows how we can create a PAX table and a regular GPDB column store table:

```
test=# create table paxtab (i bigint, f double precision) 
       with (appendonly=true, compresstype=pax);
CREATE TABLE

test=# create table coltab (i bigint, f double precision) 
       with (appendonly=true, orientation=column, compresstype=lz4);
CREATE TABLE
```

#### Example: Insert 

The following shows that the insertion speed is about on-par.

```
test=# insert into paxtab select i, i from generate_series(1, 10000000) i;
INSERT 0 10000000
Time: 4777.665 ms

test=# insert into coltab select i, i from generate_series(1, 10000000) i;
INSERT 0 10000000
Time: 4349.718 ms
```

#### Example: Count and Agg

For counts, a PAX table is about 2X faster than regular GPDB column table. 

For aggs, PAX table also performs faster than GPDB column store.

```
test=# select count(*) from paxtab;
  count   
----------
 10000000
(1 row)

Time: 79.673 ms
test=# select count(*) from coltab;
  count   
----------
 10000000
(1 row)

Time: 157.946 ms
test=# select sum(i), sum(f) from paxtab;
      sum       |      sum       
----------------+----------------
 50000005000000 | 50000005000000
(1 row)

Time: 216.214 ms
test=# select sum(i), sum(f) from coltab;
      sum       |      sum       
----------------+----------------
 50000005000000 | 50000005000000
(1 row)

Time: 264.438 ms
```

#### Example: Filter

PAX table has built-in zonemap which provides tremendous speed in filtering. This is 
evident from the example below:

```
test=# select * from paxtab where i = 1000000;
    i    |    f    
---------+---------
 1000000 | 1000000
(1 row)

Time: 14.329 ms
test=# select * from coltab where i = 1000000;
    i    |    f    
---------+---------
 1000000 | 1000000
(1 row)

Time: 247.382 ms
```

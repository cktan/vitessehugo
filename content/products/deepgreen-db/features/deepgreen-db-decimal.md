---
layout: db-feature-page

description: Deepgreen DB
title: Deepgreen DB
keywords: Deepgreen DB 

headline: Deepgreen DB

---

### Decimal64 / Decimal128


_New in version 16.04._

---

Deepgreen DB includes a new set of arbitrary precision decimal
types that are more efficient than the native postgres `Numeric`
type. These are the `Decimal64` and `Decimal128`
types that have 16-digit and 34-digit precisions respectively.

### Installation

After installing the Deepgreen DB bin file, execute the
following commands on your Deepgreen DB host to install the
decimal64 and decimal128 types and functions into the database.

```bash
% source deepgreendb/greenplum_path.sh
% cd $GPHOME/share/postgresql/contrib/
% psql your-database -f pg_decimal.sql
```

### Performance

We can now do some exercise to demonstrate the performance
characteristics of these types. The session below shows that
the simple query `select avg(x), sum(2*x) from table`
over a million records takes:

* 23 ms when x is 64-bit float;
* 38 ms when x is decimal64;
* 60 ms when x is decimal128;
* 86 ms when x is numeric with vitesse engine;
* 206 ms when x is numeric without vitesse engine;

Conclusion: for this query, decimal64 is more than 2x faster than numeric types on Deepgreen, and 5x faster than numeric types on GPDB.


```
% psql test
test=# drop table if exists tt;
DROP TABLE
test=# create table tt(
ii bigint,
 f64 double precision,
d64 decimal64,
d128 decimal128,
n numeric(15, 3))
distributed randomly;
CREATE TABLE
test=# insert into tt
select i,
    i + 0.123,
    (i + 0.123)::decimal64,
    (i + 0.123)::decimal128,
    i + 0.123
from generate_series(1, 1000000) i;
INSERT 0 1000000
test=# \timing on
Timing is on.
test=# select count(*) from tt;
count
---------
 1000000
(1 row)

Time: 16.929 ms
test=# set vitesse.enable=1;
SET
Time: 1.888 ms
test=# select avg(f64),sum(2*f64) from tt;
   avg       |       sum
-----------------+------------------
 500000.62300062 | 1000001246001.24
(1 row)

Time: 22.867 ms
test=# select avg(d64),sum(2*d64) from tt;
avg     |        sum
------------+-------------------
 500000.623 | 1000001246000.000
(1 row)

Time: 37.752 ms
test=# select avg(d128),sum(2*d128) from tt;
avg     |        sum
------------+-------------------
 500000.623 | 1000001246000.000
(1 row)

Time: 60.480 ms
test=# set vitesse.enable=1;
SET
Time: 1.704 ms
test=# select avg(n),sum(2*n) from tt;
     avg         |        sum
---------------------+-------------------
 500000.623000000000 | 1000001246000.000
(1 row)

Time: 86.086 ms
test=# set vitesse.enable=0;
SET
Time: 1.633 ms
test=# select avg(n),sum(2*n) from tt;
     avg         |        sum
---------------------+-------------------
 500000.623000000000 | 1000001246000.000
(1 row)

Time: 206.458 ms
```

---
#layout: post

date: "2015-05-17"

author: CK Tan

categories: ["postgres", "sql"]

title: Comparing Tables in Postgres
description: "Methods to tell if two tables are exactly the same in Postgres"
keywords: postgres sql

headline: Blog
subheadline:
type: "post"

---

How to tell if two tables are exactly the same?

<!--more-->

---

__Method 1: Use SQL EXCEPT__

If you google around, you will find [this post](http://dba.stackexchange.com/questions/72641/checking-whether-two-tables-have-identical-content-in-postgresql), where the use of EXCEPT is suggested. To obtain rows in t1 that are missing in t2:

```
select * from (table t1 except table t2) foo;
```

To obtain all rows that are different between t1 and t2:

```
-- note: do not drop the parens
select * 
from ((table t1 except table t2) 
	union all (table t2 except table t1)) foo;
```

Note that an empty result set from the above query does not indicate that t1 and t2 are EQUAL. For that, we would also need to assert that t1 and t2 has the same cardinality, i.e., same number of rows.

To get the true/false on equality:

```
select case
    when exists (table t1 except table t2) then 'diff'
    when exists (table t2 except table t1) then 'diff'
    when (select count(*) from t1) != (select count(*) from t2) then 'diff'
    else 'same' end;
```

---

__Method 2: Hash it ourselves__

```
with A as (
    select hashtext(textin(record_out(t1))) as h, count(*) as c
      from t1
      group by 1
),
 B as (
    select hashtext(textin(record_out(t2))) as h, count(*) as c
    from t2
    group by 1
)
select *
 from A full outer join B on (A.h + A.c = B.h + B.c)
 where A.h is null or B.h is null
 limit 5;
```

The SQL above gives you up to 5 differences between t1 and t2, and if there are 0 differences, then t1 and t2 are indeed EQUAL.

To see exactly which row is different, take the h value (e.g. 12345) of the result and match it:

```
select *
 from t1     -- or t2
 where hashtext(textin(record_out(t1))) = 12345;
```

[2015-05-22] Here is a clever way devised by Feng Tian (ftian at vitessedata.com) to tell if t1 equals t2 without any join. It uses an agg to sum the 1’s (coming from t1) and -1’s (coming from t2) of the same hash. Sum of non-zero means that particular record is missing from one or the other table, and we detect this using the HAVING clause.

```
select h, sum(cnt) from (
   select textin(record_out(t1)) as h, 1 as cnt from t1
   union all
   select textin(record_out(t2) as h, -1 as cnt from t2) foo
group by h 
having sum(cnt) <> 0;
```

---

__Which method is better?__

In general, the built-in EXCEPT clause works better. In the worst case, the SQL implies each table needs to be scanned 2 times for the case when they are equal. When the tables are different, however, the query may finish much faster with only a partial scan.

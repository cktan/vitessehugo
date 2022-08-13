---
layout: db-feature-page

description: Deepgreen DB
title: Deepgreen DB
keywords: Deepgreen DB

headline: Deepgreen DB

---


### Json Support

_New in version 16.05._
  <hr>

Deepgreen DB includes <code>json</code> type ported from Postgres 9.3. See the
[postgres documentation](http://www.postgresql.org/docs/9.3/static/functions-json.html) for details.

Note that the following functions are not supported at this time: json_each, json_each_text, json_extract_path, json_extract_path_text, json_object_keys, json_populate_record, json_populate_recordset, json_array_elements, and json_agg.

### Installation

To install the json extension, perform the following commands on your Deepgreen DB host:

```
% source deepgreendb/greenplum_path.sh
% psql your-database -f $GPHOME/share/postgresql/contrib/json.sql
```

### Try It Out
  
```
% psql test
test=# select '[1,2,3]'::json->2;
 ?column?
----------
 3
(1 row)

test=# create temp table mytab(i int, j json) distributed by (i);
CREATE TABLE

test=# insert into mytab values (1, null), (2, '[2,3,4]'), (3, '[3000,4000,5000]');
INSERT 0 3

test=# select i, j->2 from mytab;
 i | ?column?
---+----------
 2 | 4
 1 |
 3 | 5000
(3 rows)
```

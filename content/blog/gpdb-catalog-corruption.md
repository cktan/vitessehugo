---
#layout: post

date: "2015-10-20"

author: CK Tan

categories: ["greenplum", ]

title: Catalog Corruption in Greenplum DB
description: ""
keywords: greenplum, 

headline: Blog
subheadline:
type: "post"

---

Recently one of our clients experienced catalog corruption in Greenplum DB after a power outage.

<!--more-->

When the GPDB was restarted, a catalog corruption had manifested, and even though normal SQL submission still works, pg_dump was failing with an error like this:

```
$ pg_dump -t TABNAME DBNAME > /dev/null
  pg_dump: schema with OID 12345678 does not exist
```

First, determine what needs to be fixed. Fire up psql and check:

```
select oid from pg_type where typnamespace = 12345678;
select oid from pg_class where relnamespace = 12345678;
select oid from pg_operator where oprnamespace = 12345678;
select oid from pg_conversion where connamespace = 12345678;
select oid from pg_opclass where opcnamespace = 12345678;
select oid from pg_aggregate where aggnamespace = 12345678;
select oid from pg_proc where procnamespace = 12345678;
```

If any of the above queries returned a row, we can attempt to fix the corruption by deleting the offending entries.

<i class="fas fa-exclamation-triangle text-warning"></i> WARNING: THE FOLLOWING PROCEDURE SHOULD NOT BE DONE LIGHTLY. CONTACT YOUR SERVICE REP TO HELP YOU BACKUP DATABASE BEFORE PROCEEDING.

```
# Step 1: Shutdown GPDB
$ gpstop -M immediate

# Step 2: Restart GPDB master in *utility* mode:
$ gpstart -m

# Step 3: Connect to the master in utility mode for catalog maintenance:
$ PGOPTIONS='-c gp_session_role=utility' psql DBNAME

-- set the GUC to enable catalog updates. THIS IS NOT OBVIOUS!
set allow_system_table_mods=dml;

-- perform the updates
delete pg_type where typnamespace = 12345678;
delete pg_class where relnamespace = 12345678;
delete pg_operator where oprnamespace = 12345678;
delete pg_conversion where connamespace = 12345678;
delete pg_opclass where opcnamespace = 12345678;
delete pg_aggregate where aggnamespace = 12345678;
delete pg_proc where procnamespace = 12345678;

\quit

# Step 5: Restart GPDB:
$ gpstop -m; gpstart
```

Good luck!

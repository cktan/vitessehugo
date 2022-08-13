---
layout: db-feature-page

description: Deepgreen DB
title: Deepgreen DB
keywords: Deepgreen DB

headline: Deepgreen DB

---


## pgBadger for Deepgreen DB

pgBadger is a PostgreSQL log analyzer built for speed with fully
reports. For details, please refer to [this page.](https://github.com/dalibo/pgbadger)

Note that pgBadger is only relevant on the **master** node. 

### Quick Start

These packages are required by pgBadger, and should be installed on the 
**master** segment:


```
# ON REDHAT:
   % sudo yum install gcc make perl-CPAN
   % sudo cpan Text::CSV_XS

# ON UBUNTU:
   % sudo apt-get install gcc make
   % sudo cpan Text::CSV_XS
```

Next, we need to make the database log SQL statements. This can be
achieved by setting the following configurations in the
`postgresql.conf` file on the **master** segment.

```
   log_min_duration_statement = 0
   log_duration = on
```

After modifying the `postgresql.conf` file, restart the database by
issuing the command:

```
   % gpstop -r
```

Now, connect to the database and run some queries. Locate a new log
file in in the `$MASTER_DATA_DIRECTORY/pg_log` directory, and issue
the `pgbadger` command against it to generate a `out.html` file. For example:

```
   % pgbadger -f csv $MASTER_DATA_DIRECTORY/pg_log/gpdb-2018-08-08_11111.csv
```

You can now view the `out.html` file by pointing your browser to the
file. Note: you may need to copy the file to your local machine if
your browser cannot point to the file on the master segment.

### Daily Reports

You can generate daily pgBadger report by scheduling cron jobs. The following
command generates and stores daily reports in the `/var/reports/` directory. 

```
    59 23 * * * TODAY=`date +%F` && ${GPHOME}/bin/pgbadger -f csv -o /var/reports/gpdb-report-${TODAY}.html $MASTER_DATA_DIRECTORY/pg_log/gpdb-${TODAY}_*.csv
```

If your web server is on a remote machine, you can use passwordless SCP 
to copy the report to the web server.

```
    59 23 * * * TODAY=`date +%F` && $GPHOME/bin/pgbadger -f csv -o /var/reports/gpdb-report-${TODAY}.html $MASTER_DATA_DIRECTORY/pg_log/gpdb-${TODAY}_*.csv && scp /var/reports/gpdb-report-${TODAY}.html webadmin@webserver:/www/html/
```
    



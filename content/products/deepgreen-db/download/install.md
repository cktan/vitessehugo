---
layout: db-download-page

description: Download 
title: Deepgreen DB
keywords: Deepgreen DB

headline: Deepgreen DB

---

## Install

The file you downloaded is a `.bin` file that can be executed directly
with bash.

Execute the .bin script to install Deepgreen DB:

```
% bash THE-BIN-FILE-YOU-DOWNLOADED
```

The installation script will install the Deepgreen DB in the current
directory and create a simple symlink `deepgreendb` to point to it.

---

### Setting OS Parameters

**IMPORTANT:** Make sure your OS parameters are set properly according to 
[this page](https://gpdb.docs.pivotal.io/540/install_guide/prep_os_install_gpdb.html#topic3).

### Initializing the DB

To verify that the installation was successful, we will create an
instance and start the service.

```
% # Source the env
% source deepgreendb/greenplum_path.sh

% # Make sure we can ssh to localhost without passwords
% gpssh-exkeys -h localhost

% # Create data directories for master and 2 segments
% sudo mkdir /dbfast{0,1,2}
% sudo chown $USER /dbfast{0,1,2}

% # Create the hostfile
% echo localhost > hostfile

% # Create cluster.conf file
% cat > cluster.conf <<HEREHERE

ARRAY_NAME="mpp1 cluster"
CLUSTER_NAME="mpp1 cluster"
MACHINE_LIST_FILE=hostfile
SEG_PREFIX=dg
DATABASE_PREFIX=dg
PORT_BASE=25432
declare -a DATA_DIRECTORY=(/dbfast1 /dbfast2)
MASTER_HOSTNAME=localhost
MASTER_DIRECTORY=/dbfast0
MASTER_PORT=15432
IP_ALLOW=0.0.0.0/0
TRUSTED_SHELL=/usr/bin/ssh
CHECK_POINT_SEGMENTS=8
ENCODING=UNICODE
export MASTER_DATA_DIRECTORY
export TRUSTED_SHELL
DEFAULT_QD_MAX_CONNECT=25
QE_CONNECT_FACTOR=5

HEREHERE

% # Finally, run gpinitsystem
% gpinitsystem -c cluster.conf -h hostfile
```

---

### Now We Can Have Some Fun

Let's run some tests!

```
% # Source the env if this is a new shell
% source deepgreendb/greenplum_path.sh

% # We set up the DB on port 15432
% export PGPORT=15432

% # Create Test DB
% createdb test

% psql test
test=# create table tt as
select i::bigint as i, i::double precision as f
from generate_series(1, 1000000) i
distributed by (i);
SELECT 1000000
test=# show vitesse.version;
         vitesse.version
------------------------------------------------
Deepgreen DB 16.05 [rev 2c302da on 2016-05-08]
(1 row)

test=# \timing on
Timing is on.
test=# set vitesse.enable=0;
SET
Time: 1.799 ms
test=# select count(*), sum(i), avg(i) from tt;
count  |     sum      |   avg
---------+--------------+----------
1000000 | 500000500000 | 500000.5
(1 row)

Time: 439.994 ms
test=# set vitesse.enable=1;
SET
Time: 1.814 ms
test=# select count(*), sum(i), avg(i) from tt;
count  |     sum      |   avg
---------+--------------+----------
1000000 | 500000500000 | 500000.5
(1 row)

Time: 16.965 ms
test=# select 439/17;
?column?
----------
25
(1 row)

Time: 2.577 ms
test=#
```

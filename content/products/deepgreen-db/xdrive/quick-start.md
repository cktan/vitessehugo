---
layout: xdrive-documentation-page

description: Xdrive
title: Xdrive Quick Start
keywords: Xdrive Quick Start

headline: Deepgreen DB

scroll: true

---

### Quick Start

We will demonstrate an example to read/write the CSV file from local
filesystem via xdrive built-in csv plugin from scratch.

<i class="fas fa-info-circle text-info"></i> Before you run xdrive,
you have to setup the configuration file which is in toml file
format.

__1.__ Create the xdrive.toml [configuration file](../configuration) with the content below.  Setup the
standalone local server with port 50051 and also setup the CSV
mountpoint with name “mynfs_csv” and file base directory
/tmp/xdrive/tests/data.
  
```bash
[xdrive]
dir = "/tmp/xdrive"                     # xdrive base directory
host = [ "127.0.0.1" ]            # list of xdrive server hosts
port = 50051


[[xdrive.mount]]
  name = "mynfs_csv"                                                  # name of the plugin
  argv = ["xdr_fs/xdr_fs", "csv", "/tmp/xdrive/tests/data"]      # list of arguments to invoke the plugin

#arg0 is the plugin executable, arg1, arg2, arg3, argN are the command arguments

```

__2.__ Run xdrctl deploy command to [deploy the xdrive server](../deployment) to the
list of server hosts specified in the __xdrive.toml__

```bash
% xdrctl deploy xdrive.toml
mkdir destdir ...
scp xdrive to remote ...
scp xdrplugin to remote ...
scp conffile to remote ...
  ```

After the command, /tmp/xdrive directory will be created and your
xdrive.toml will be copied to
/tmp/xdrive/xdrive.toml and /tmp/xdrive/plugin is the plugin base
directory

```bash
ls /tmp/xdrive/
bin  log  plugin  xdrive.toml
```

__3.__ Now, you can start the xdrive servers by `xdrctl start`.

```bash
% cd /tmp/xdrive/
% xdrctl start xdrive.toml
% ps -ef | grep xdrive
ericlam   2349     1  0 08:24 ?        00:00:00 /tmp/xdrive/bin/xdrive -p 50051 -D /tmp/xdrive
```

__4.__ Start the Deepgreen database.

```bash
% gpstart
```

__5.__ Setup the DDL to [create the read-only and writable external
tables](../read-write) for the CSV files

```bash
DROP EXTERNAL TABLE IF EXISTS myxx1; 
CREATE EXTERNAL TABLE myxx1
    (
        i int,
        t text
    )
LOCATION ('xdrive://127.0.0.1:50051/mynfs_csv/x1.csv') 
FORMAT 'CSV';

DROP EXTERNAL TABLE IF EXISTS myxx2; 
CREATE EXTERNAL TABLE myxx2
    (
        i int,
        t text
    )
LOCATION ('xdrive://127.0.0.1:50051/mynfs_csv/x?.csv') 
FORMAT 'CSV';

DROP EXTERNAL TABLE IF EXISTS myxx3; 
CREATE EXTERNAL TABLE myxx3
    (
        i int,
        t text
    )
LOCATION ('xdrive://127.0.0.1:50051/mynfs_csv/x*.csv') 
FORMAT 'CSV';

DROP EXTERNAL TABLE IF EXISTS myxxw; 
CREATE WRITABLE EXTERNAL TABLE myxxw
    (
        i int,
        t text
    )
LOCATION ('xdrive://127.0.0.1:50051/mynfs_csv/x#UUID#.csv') 
FORMAT 'CSV';
```

__6.__ Create the data file /tmp/xdrive/tests/data/x1.csv

```bash
% cat /tmp/xdrive/tests/data/x1.csv
1,1
2,2
3,3
4,4
1,1
2,2
3,3
4,4
1,1
2,2
3,3
4,4

% wc -l x1.csv
12 x1.csv
```

__7.__ You can now run the psql to read the x1.csv from the local
filesystem

```bash
% psql
psql wetestdata
psql (8.2.15)
Type "help" for help.

wetestdata=# select * from myxx1;
 i | t 
---+---
 1 | 1
 2 | 2
 3 | 3
 4 | 4
 1 | 1
 2 | 2
 3 | 3
 4 | 4
 1 | 1
 2 | 2
 3 | 3
 4 | 4
(12 rows)

wetestdata=# select * from myxx2;
 i | t 
---+---
 1 | 1
 2 | 2
 3 | 3
 4 | 4
 1 | 1
 2 | 2
 3 | 3
 4 | 4
 1 | 1
 2 | 2
 3 | 3
 4 | 4
(12 rows)

wetestdata=# select * from myxx3;
 i | t 
---+---
 1 | 1
 2 | 2
 3 | 3
 4 | 4
 1 | 1
 2 | 2
 3 | 3
 4 | 4
 1 | 1
 2 | 2
 3 | 3
 4 | 4
(12 rows)
```

__8.__ You can also write the data to the local filesystem by writing
the data to the writable external table myxxw

```bash
wetestdata=# insert into myxxw select * from myxx1;
INSERT 0 12
```

Check the datafiles in /tmp/xdrive/tests/data

```bash
% ls -1 x*.csv
x1.csv  
x7907cde3-b048-4440-94bf-d9d31df37d72.csv 
xd7a467fd-614b-4641-876f-ede4116ffd42.csv

% cat x7907cde3-b048-4440-94bf-d9d31df37d72.csv 
2,2
4,4
2,2
4,4
2,2
4,4
% cat xd7a467fd-614b-4641-876f-ede4116ffd42.csv 
1,1
3,3
1,1
3,3
1,1
3,3
```

__9.__ Fetch the myxx3 table to see how many rows you can get.  The
number of rows should be 24 now.

```bash
wetestdata=# select count(*) from myxx3;
 count 
-------
    24
(1 row)
```

__10.__ To stop the xdrive, simply run xdrctl stop.

```bash
% xdrctl stop /tmp/xdrive/xdrive.toml
```

__11.__ You can run xdrive and csv plugin successfully.  For configuration setting, please
click [here](../configuration/) for more details.


***

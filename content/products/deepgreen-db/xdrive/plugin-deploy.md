---
layout: xdrive-documentation-page

description: Xdrive
title: Xdrive
keywords: Xdrive

headline: Deepgreen DB

scroll: true

---

## Deploying a New Plugin

All plugin packages are in .tgz file format and located in __package__ directory which is under 
the plugin-path specified in xdrive.toml file, e.g.,
XDRIVE_HOME/plugin/package. 

We use the open source plugin, plugin_csv,
from https://github.com/vitesse-ftian/dgtools/ as an example.

Copy your existing xdrive.toml to /tmp and add a new mount-point for the plugin_csv to /tmp/xdrive.toml,
```bash
[[xdrive.mount]]
  name = "mycsv"
  argv = ["/usr/bin/java", "-cp", "vitessedata-csv-plugin.jar",  "com.vitessedata.xdrive.csv.Main", "/tmp/xdrive/data"]
```

Xdrive server will invoke the plugin by executing either the
executable file or java library with java.  Make sure the file is
executable by Xdrive server. You can use any programming languages to
write the plugin.

Download the repo and compile the source files,
plugin_csv.tgz will be generated in the package directory.

```bash
% git clone https://github.com/vitesse-ftian/dgtools
% cd dgtools/plugin/java/plugin_csv/
% make
% ls package
jars plugin_csv.tgz
```

Let see the data structure of the plugin_csv.tgz,
```bash
% tar vft plugin_csv.tgz 
-rw-rw-r-- deepgreen/deepgreen 50219 2018-04-13 07:30 jars/vitessedata-csv-plugin.jar
```

Since the Xdrive configuration file has been modified,
you have to stop the Xdrive server and re-deploy the Xdrive.

```bash
% xdrctl stop /tmp/xdrive.toml
% xdrctl deploy /tmp/xdrive.toml
```

run `xdrctl deployplugin` to deploy the plugin.
```bash
% xdrctl deployplugin $XDRIVE_HOME/xdrive.toml package/plugin_csv.tgz
% xdrctl start $XDRIVE_HOME/xdrive.toml
```

plugin will be deployed to all Xdrive servers specified in
xdrive.toml. The deployed plugin will be located in directory
`plugin`.

Create the external tables,
```bash
DROP EXTERNAL TABLE IF EXISTS xx1; 
CREATE EXTERNAL TABLE xx1
    (
        i int,
        t text
    )
LOCATION ('xdrive://localhost:50051/mycsv/x?.csv') 
FORMAT 'CSV';

DROP EXTERNAL TABLE IF EXISTS xxw; 
CREATE WRITABLE EXTERNAL TABLE xxw
    (
        i int,
        t text
    )
LOCATION ('xdrive://localhost:50051/mycsv/x#UUID#.csv') 
FORMAT 'CSV';
```
Now, you are ready to run the plugin.

***


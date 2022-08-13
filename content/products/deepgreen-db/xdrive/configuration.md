---
layout: xdrive-documentation-page

description: Xdrive 
title: Xdrive
keywords: Xdrive

headline: Deepgreen DB

scroll: true

---

## Xdrive Configuration

The following shows the syntax and entries expected of a configuration
file for xdrive:

```console
#
# This file MUST be named 'xdrive.toml'
# What follows are configurations for xdrive.
#
[xdrive]

#
# Specify the working directory. Xdrive will cd into
# this directory at the target machine.
# Logs will be written to ${dir}/log/.
#
dir = "the-home-dir-on-target-machine"

#
# Specify the target machines and the port Xdrive will
# use for communication. For each entry, an Xdrive instance
# will be started.
#
port = 7171
host = [ "host1", "host2", ...]

#
# Each [[xdrive.mount]] specifies a mountpoint.
# There can be multiple [[xdrive.mount]].
#
[[xdrive.mount]]
name = "name-of-a-mountpoint, e.g. mydata"
argv = ["plugin-fname-or-fpath", "argv1", "argv2", ...]
env = ["envname=envvalue", ... ]


```

#### Dir

The `dir` configuration value specifies the "home" directory of the
Xdrive program on each host. If the directory does not exist, it will
be created automatically.

#### Port

The `port` configuration value gives the port number for the Xdrive TCP endpoint.

#### Host

The `host` configuration value specifies an array of machines that Xdrive should run on.

One commonly used host configuration in Deepgreen DB is to have an
entry for each _node_ of the cluster. Suppose you have a 2-node setup
where the hosts are `mdw`, `sdw1-1`, `sdw1-2`, `sdw2-1`, `sdw2-2`, you
would set up the host configuration like this:

```bash

# Run an xdrive on each of my segment machines. 
host = [ "sdw1-1", "sdw2-1", ]

```

<i class="fas fa-info-circle text-info"></i> A setup like this lets
you use `localhost` in the external table DDL.


#### Mountpoint

Utilizing the same concept as mounting a file system in UNIX, a
mountpoint is a symbol that represents the root of a file system in
Xdrive.

Multiple mountpoints may be specified in the configuration with the
`[[xdrive.mount]]` tag. Each mountpoint has:

- `name` -- a unique identifier to be used in the LOCATION clause for
  invocation of the plugin,

- `argv` -- an array that spells out the command line arguments used
  to invoke the plugin, and

- `env` -- an array that can be used to set up environment variables
  for use by the plugin.


Next, let's take a look the [Deployment](../deployment) of Xdrive.

***

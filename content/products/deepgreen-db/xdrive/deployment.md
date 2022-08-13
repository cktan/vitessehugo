---
layout: xdrive-documentation-page

description: Xdrive
title: Xdrive
keywords: Xdrive

headline: Deepgreen DB

scroll: true

---

## Xdrive Deploy / Start / Stop

To deploy xdrive, first create the [configuration file](../configuration).  With the
configuration file, deploy xdrive to all the target machines by using
the `xdrctl` program:

```bash

xdrctl deploy path-to-conf-file

```

The deployment step should be done once. After deployment, you can
start or stop xdrive by executing this command:

```bash

xdrctl {start|stop} path-to-conf-file

```

Let's deploy and start the xdrive server now.

```bash
% xdrctl deploy xdrive.toml
% xdrctl start xdrive.toml
```

Click [here](../read-write) to check out how to read/write from an external table.


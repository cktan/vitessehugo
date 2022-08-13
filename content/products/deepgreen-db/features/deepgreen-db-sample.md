---
layout: db-feature-page

description: Deepgreen DB
title: Deepgreen DB
keywords: Deepgreen DB

headline: Deepgreen DB

---


### True Sampling

_New in version 16.16._

---

Deepgreen DB has built-in support for true sampling with SQL. You can sample by either number of rows or by percentage of the table:

```sql
SELECT {select-clauses} LIMIT SAMPLE {n} ROWS;
SELECT {select-clauses} LIMIT SAMPLE {n} PERCENT;
```

---


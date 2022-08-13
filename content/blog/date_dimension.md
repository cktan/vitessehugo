---
#layout: post

date: "2015-03-15"

author: CK Tan

categories: ["data warehouse"]

title: Date Dimension Table in Postgres
description: "Date Dimension Table for Data Warehouse project in Postgress SQL"
keywords: Postgress, SQL, Database, Date Dimension

headline: Blog
subheadline:
type: "post"

---

One of the first dimension tables required for any Data Warehouse project is the Date Dimension table. See [Calendar Date Dimensions @kimballgroup](http://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/calendar-date-dimension/).

<!--more-->

---

We want our date dimension table to look like this:

```
Column             | Type | Description 
------------------ | ---- | ----------- 
date_key           | int  | A number corresponding to the date. e.g. 20150315. 
date               | date | SQL date. 
y                  | int  | Year in number, e.g. 2015. 
m                  | int  | Month in number (1..12). 
d                  | int  | Day of month (1..31). 
q                  | int  | Quarter (1..4). 
h                  | int  | First / second half of year (1 or 2). 
dow                | int  | Day of week (1..7). 
doy                | int  | Day of year (1..366). 
yow                | int  | Year of week.
                   |      |  Can be different from y only during first week of the year. 
woy                | int  | Week of year (1..52).
                   |      | Note: first few days of the year may be week 52 of last year. 
doe                | int  | Day of epoch, a serial number. 
woe                | int  | Week of epoch, a serial number. 
moe                | int  | Month of epoch, a serial number. 
yoe                | int  | Year of epoch, a serial number. 
is_weekday         | bool | True if Mon..Fri. 
is_weekend         | bool | True if Sat..Sun. 
first_date_of_week | date | Date of Monday of this week. 
last_date_of_week  | date | Date of Sunday of this week. 
yw                 | text | e.g. 2015-W5 for week 5 of 2015. 
ym                 | text | e.g. 2015-12 for December 2015. 
yq                 | text | e.g. 2015-Q4 for Q4 of 2015. 
is_holiday         | bool | Holiday indicator.
```

The SQL statement follows. A few things to note:

* You can edit section DR1 to set the starting date and the range of your date dimension. In the code below, we start generating dates from year 2000 through 2030.
* A week starts from Monday (1) and ends on Sunday (7).
* The first week of the year usually belongs to the previous year. For example, on January 1, 2000, the year-of-week is 1999, and the week-of-year is 52.
* You should add columns to this table to mark special dates such as holidays and significant events of the company.

```
create table datedim as
with
DR1 as (
    -- You can change the range here!
    -- epoch starting 2000-01-03, for 30 years
    -- must start on a Monday and end on a Sunday to avoid partial week
    select n,
       '2000-01-03'::date as first_date,
       '2000-01-03'::date + n as date
       from generate_series(0, '2031-01-05'::date - '2000-01-03') n
),
DR2 as (
    select *,
        extract(dow from first_date) as day_of_first_date,
        (date - first_date) + 1 as doe,
        extract(year from date)::int - 2000 + 1 as yoe,
        extract(week from date)::int as woy,
        extract(day from date)::int as dom,
        extract(dow from date)::int as dow,
        extract(doy from date)::int as doy, 
        extract(month from date)::int as m,
        extract(quarter from date)::int as q, 
        extract(year from date)::int as y
    from DR1
),
DR3 as (
    select *,
         (case when m = 1 and woy > 50 then y - 1 else y end) as yow,
         (8 - (case when day_of_first_date = 0
                    then 7 else day_of_first_date end))::int % 7 as dayoffset
    from DR2
),
DR4 as (
    select *,
        ((m - 1) / 6) + 1 as h,     -- half of year
        (doe - 1 - dayoffset + 7) / 7 + 1 as woe,
        (yoe - 1) * 12 + m as moe,
        (yoe - 1) * 4 + ((m - 1) / 3) + 1 as qoe,
        (1 <= dow and dow <= 5) as is_weekday,
        not (1 <= dow and dow <= 5) as is_weekend

    from DR3
),
MonthGroup as (
    select moe, max(date) as last_date_of_month from DR4 group by 1
),
WeekGroup as (
    select woe, min(date) as first_date_of_week,
           max(date) as last_date_of_week from DR4 group by 1
)
select
    to_char(date, 'YYYYMMDD')::int as date_key,
    date,
    y,                          -- year (YYYY)
    m,                          -- month (1..12)
    dom as d,                   -- day of month (1..31)
    q,                          -- quarter (1..4)
    h,              -- half (1..2)
    dow,                        -- day of week (1..7)
    doy,                        -- day of year (1..366)
    yow,                        -- year of week
    woy,                        -- week of year
    doe,                        -- day of epoch 
    DR4.woe,                    -- week of epoch
    DR4.moe,                    -- month of epoch
    yoe,                        -- year of epoch
    is_weekday,                 -- true if Mon .. Fri
    is_weekend,                 -- true if Sat or Sun 
    first_date_of_week,         -- date of Mon in week
    last_date_of_week,          -- date of Sun in week
    last_date_of_month,         -- date of last day in month
    yow||'-W'||LPAD(woy::text, '0', 2) as yw,       -- e.g.2015-W05
    to_char(date, 'yyyy-mm') as ym, -- e.g. 2015-07
    y||'-Q'||q as yq,               -- e.g. 2015-Q3
    0::bool as is_holiday
from DR4
join MonthGroup using (moe)
join WeekGroup using (woe)
;

-- Insert the *special date row* indicating invalid date
-- All columns are NULL except the date_key field. 

insert into datedim (date_key) values (99999999);

-- Populate holidays manually.

-- Populate other special dates manually.
```

drop table if exists climb;
create table climb (
    'origin_id' integer not null,
    'href' integer not null,
    'name' text not null,
    'rateYDS' text null,
    'feet' integer null,
    'description' real null,
    'grade' real null,
    'staraverage' real null,
    'best' integer null,
    'keyword' text null
);
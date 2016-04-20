drop table if exists climb;
create table climb (
    'origin_id' not null,
    'href_id' text not null,
    'name' text not null,
    'url' text not null,
    'rateYDS' text null,
    'feet' integer null,
    'combined_text' real null,
    'gradeComb' real null,
    'staraverage' real null,
    'best' real null
);
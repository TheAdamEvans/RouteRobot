drop table if exists climb;
create table climb (
    'origin_href' integer not null,
    'href' integer not null,
    'name' text not null,
    'type' text null,
    'rateYDS' text null,
    'rateHueco' text null,
    'feet' integer null,
    'keyword' text null,
    'best' integer null,
    'img_src' text null,
    'img_height' text null,
    'img_width' text null
);

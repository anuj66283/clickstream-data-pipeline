--Table to store events per minute
CREATE TABLE event_per_minute
(
    `cnt` UInt8,
    `event_date` datetime
)
ENGINE = MergeTree
ORDER BY event_date

--Materialized view
CREATE MATERIALIZED VIEW e_p_m TO event_per_minute
AS SELECT
    toStartOfMinute(event_time) AS event_date,
    count(*) AS cnt
FROM clickstream
GROUP BY event_date

-------------------------------------------------------------------------------

--top brand
CREATE TABLE top_brand
(
    `brand` String,
    `cnt` UInt8,
    `brand_date` date
)
ENGINE = MergeTree
ORDER BY brand_date

-- materialized view
CREATE MATERIALIZED VIEW t_b TO top_brand
AS SELECT
    brand,
    countDistinct(session_id) AS cnt,
    date(event_time) AS brand_date
FROM clickstream
WHERE brand != ''
GROUP BY
    brand_date,
    brand
ORDER BY brand_date DESC
LIMIT 5

-------------------------------------------------------------------------------

--source of traffic
CREATE TABLE source_of_traffic
(
    `channel` String,
    `cnt` UInt8,
    `traffic_date` date
)
ENGINE = MergeTree
ORDER BY traffic_date

--materialized view
CREATE MATERIALIZED VIEW s_o_t TO source_of_traffic
AS SELECT
    channel,
    countDistinct(session_id) AS cnt,
    date(event_time) AS traffic_date
FROM clickstream
GROUP BY
    traffic_date,
    channel
ORDER BY traffic_date ASC

-------------------------------------------------------------------------------

-- top countries
CREATE TABLE top_country
(
    `country` String,
    `cnt` UInt8,
    `country_date` date
)
ENGINE = MergeTree
ORDER BY country_date

--materialized view
CREATE MATERIALIZED VIEW t_c TO top_country
AS SELECT
    country,
    countDistinct(session_id) AS cnt,
    date(event_time) AS country_date
FROM clickstream
WHERE country != ''
GROUP BY
    country,
    country_date
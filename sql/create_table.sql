CREATE TABLE clickstream
(
    `ip` String,
    `user_id` Int8,
    `session_id` String,
    `event_time` DateTime,
    `event_name` String,
    `channel` String,
    `browser` String,
    `os` String,
    `family` String,
    `brand` String,
    `model` String,
    `country` String,
    `query` String
)
ENGINE = MergeTree
ORDER BY event_time
TTL date(event_time) + toIntervalDay(7)